import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict
import yaml
from confluent_kafka import Producer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetailDataGenerator:
    def __init__(self, config_path: str = 'config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize Kafka producer
        self.producer = Producer({
            'bootstrap.servers': self.config['kafka']['bootstrap_servers']
        })
        
        # Load reference data
        self.stores = self.config['stores']
        self.products = self.config['products']
        self.payment_methods = self.config['payment_methods']
        self.customer_segments = self.config['customer_segments']

    def generate_transaction(self) -> Dict:
        """Generate a single retail transaction."""
        store = random.choice(self.stores)
        customer_id = f"CUST{random.randint(1000, 9999)}"
        num_items = random.randint(1, 5)
        
        items = []
        total_amount = 0
        
        for _ in range(num_items):
            product = random.choice(self.products)
            quantity = random.randint(1, 3)
            price = product['price']
            item_total = price * quantity
            total_amount += item_total
            
            items.append({
                'product_id': product['id'],
                'name': product['name'],
                'category': product['category'],
                'price': price,
                'quantity': quantity,
                'inventory_count': random.randint(0, 100)
            })

        return {
            'transaction_id': f"TXN{int(time.time())}{random.randint(1000, 9999)}",
            'timestamp': datetime.now().isoformat(),
            'store_location': store['location'],
            'customer_id': customer_id,
            'items': items,
            'total_amount': round(total_amount, 2),
            'payment_method': random.choice(self.payment_methods),
            'is_fraudulent': random.random() < 0.01  # 1% chance of fraud
        }

    def generate_inventory_update(self) -> Dict:
        """Generate an inventory update."""
        store = random.choice(self.stores)
        num_updates = random.randint(1, 3)
        
        product_updates = []
        for _ in range(num_updates):
            product = random.choice(self.products)
            product_updates.append({
                'product_id': product['id'],
                'new_inventory_count': random.randint(0, 100)
            })

        return {
            'timestamp': datetime.now().isoformat(),
            'store_location': store['location'],
            'product_updates': product_updates
        }

    def delivery_report(self, err, msg):
        """Callback for message delivery reports."""
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def produce_messages(self, num_transactions: int = 100, interval: float = 1.0):
        """Produce messages to Kafka topics."""
        for _ in range(num_transactions):
            # Generate and send transaction
            transaction = self.generate_transaction()
            self.producer.produce(
                'retail-transactions',
                json.dumps(transaction).encode('utf-8'),
                callback=self.delivery_report
            )
            
            # Generate and send inventory update
            inventory_update = self.generate_inventory_update()
            self.producer.produce(
                'inventory-updates',
                json.dumps(inventory_update).encode('utf-8'),
                callback=self.delivery_report
            )
            
            # Flush messages
            self.producer.poll(0)
            
            # Wait for the specified interval
            time.sleep(interval)
        
        # Ensure all messages are delivered
        self.producer.flush()

def main():
    generator = RetailDataGenerator()
    try:
        logger.info("Starting data generation...")
        generator.produce_messages(num_transactions=1000, interval=0.5)
        logger.info("Data generation completed successfully")
    except KeyboardInterrupt:
        logger.info("Data generation stopped by user")
    except Exception as e:
        logger.error(f"Error during data generation: {e}")

if __name__ == "__main__":
    main() 