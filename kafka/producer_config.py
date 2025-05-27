from confluent_kafka import Producer
import json
import uuid
from datetime import datetime
import random
import time

class RetailDataProducer:
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'retail-producer'
        })
        
    def delivery_report(self, err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def generate_transaction(self):
        """Generate a sample retail transaction."""
        return {
            'transaction_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'store_location': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            'customer_id': str(uuid.uuid4()),
            'items': [
                {
                    'product_id': str(uuid.uuid4()),
                    'quantity': random.randint(1, 5),
                    'price': round(random.uniform(10.0, 1000.0), 2)
                }
                for _ in range(random.randint(1, 5))
            ],
            'total_amount': round(random.uniform(50.0, 5000.0), 2),
            'payment_method': random.choice(['Credit Card', 'Debit Card', 'Cash', 'Mobile Payment'])
        }

    def generate_inventory_update(self):
        """Generate a sample inventory update."""
        return {
            'timestamp': datetime.now().isoformat(),
            'store_location': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            'product_id': str(uuid.uuid4()),
            'new_inventory_count': random.randint(0, 100)
        }

    def produce_transaction(self):
        """Produce a transaction message to Kafka."""
        transaction = self.generate_transaction()
        self.producer.produce(
            'retail-transactions',
            key=transaction['transaction_id'],
            value=json.dumps(transaction).encode('utf-8'),
            callback=self.delivery_report
        )
        self.producer.poll(0)

    def produce_inventory_update(self):
        """Produce an inventory update message to Kafka."""
        update = self.generate_inventory_update()
        key = f"{update['store_location']}:{update['product_id']}"
        self.producer.produce(
            'retail-inventory',
            key=key,
            value=json.dumps(update).encode('utf-8'),
            callback=self.delivery_report
        )
        self.producer.poll(0)

    def run(self, interval=1):
        """Run the producer continuously."""
        try:
            while True:
                # Produce a transaction
                self.produce_transaction()
                
                # Produce an inventory update
                self.produce_inventory_update()
                
                # Flush to ensure delivery
                self.producer.flush()
                
                # Wait for the next interval
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("Stopping producer...")
        finally:
            self.producer.flush()

if __name__ == '__main__':
    producer = RetailDataProducer()
    producer.run() 