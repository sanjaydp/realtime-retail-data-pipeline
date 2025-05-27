import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List

from confluent_kafka import Producer
from faker import Faker

# Initialize Faker for generating realistic data
fake = Faker()

# Kafka configuration
KAFKA_CONFIG = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'retail-data-producer'
}

# Product categories and their price ranges
PRODUCT_CATEGORIES = {
    'Electronics': (50, 2000),
    'Clothing': (20, 200),
    'Home & Kitchen': (30, 500),
    'Books': (10, 50),
    'Sports': (25, 300),
    'Beauty': (15, 150),
    'Toys': (10, 100),
    'Food': (5, 50)
}

# Payment methods
PAYMENT_METHODS = ['Credit Card', 'Debit Card', 'Cash', 'Mobile Payment']

# Store locations
STORE_LOCATIONS = [
    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
    'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'
]

def generate_product() -> Dict:
    """Generate a random product with realistic attributes."""
    category = random.choice(list(PRODUCT_CATEGORIES.keys()))
    min_price, max_price = PRODUCT_CATEGORIES[category]
    return {
        'product_id': fake.uuid4(),
        'name': fake.word().capitalize() + ' ' + category[:-1],
        'category': category,
        'price': round(random.uniform(min_price, max_price), 2),
        'inventory_count': random.randint(0, 100)
    }

def generate_transaction() -> Dict:
    """Generate a random retail transaction."""
    num_items = random.randint(1, 5)
    items = [generate_product() for _ in range(num_items)]
    total_amount = sum(item['price'] for item in items)
    
    return {
        'transaction_id': fake.uuid4(),
        'timestamp': datetime.now().isoformat(),
        'store_location': random.choice(STORE_LOCATIONS),
        'customer_id': fake.uuid4(),
        'items': items,
        'total_amount': round(total_amount, 2),
        'payment_method': random.choice(PAYMENT_METHODS),
        'is_fraudulent': random.random() < 0.01  # 1% chance of being fraudulent
    }

def delivery_report(err, msg):
    """Callback function for Kafka message delivery reports."""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def main():
    """Main function to generate and send retail data to Kafka."""
    producer = Producer(KAFKA_CONFIG)
    
    try:
        while True:
            # Generate transaction data
            transaction = generate_transaction()
            
            # Convert to JSON
            transaction_json = json.dumps(transaction)
            
            # Send to Kafka
            producer.produce(
                'retail-transactions',
                transaction_json.encode('utf-8'),
                callback=delivery_report
            )
            
            # Flush to ensure delivery
            producer.poll(0)
            
            # Generate inventory update
            inventory_update = {
                'timestamp': datetime.now().isoformat(),
                'store_location': transaction['store_location'],
                'product_updates': [
                    {
                        'product_id': item['product_id'],
                        'new_inventory_count': max(0, item['inventory_count'] - 1)
                    }
                    for item in transaction['items']
                ]
            }
            
            # Send inventory update to Kafka
            producer.produce(
                'inventory-updates',
                json.dumps(inventory_update).encode('utf-8'),
                callback=delivery_report
            )
            
            # Flush to ensure delivery
            producer.poll(0)
            
            # Wait for 1 second before generating next transaction
            time.sleep(1)
            
    except KeyboardInterrupt:
        print('Stopping data generation...')
    finally:
        # Flush any remaining messages
        producer.flush()

if __name__ == '__main__':
    main() 