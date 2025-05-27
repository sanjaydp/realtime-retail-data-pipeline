from confluent_kafka import Consumer, KafkaError
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RetailDataConsumer:
    def __init__(self, bootstrap_servers='localhost:9092', group_id='retail-consumer-group'):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })
        
        # Subscribe to topics
        self.consumer.subscribe(['retail-transactions', 'retail-inventory'])
        
    def process_transaction(self, message):
        """Process a retail transaction message."""
        try:
            transaction = json.loads(message.value().decode('utf-8'))
            logger.info(f"Processing transaction: {transaction['transaction_id']}")
            
            # Add your transaction processing logic here
            # For example:
            # - Validate transaction data
            # - Calculate metrics
            # - Store in database
            # - Trigger alerts for suspicious transactions
            
            return True
        except Exception as e:
            logger.error(f"Error processing transaction: {str(e)}")
            return False
            
    def process_inventory_update(self, message):
        """Process an inventory update message."""
        try:
            update = json.loads(message.value().decode('utf-8'))
            logger.info(f"Processing inventory update for {update['store_location']}:{update['product_id']}")
            
            # Add your inventory processing logic here
            # For example:
            # - Update inventory levels
            # - Check for low stock alerts
            # - Trigger reorder notifications
            
            return True
        except Exception as e:
            logger.error(f"Error processing inventory update: {str(e)}")
            return False
            
    def run(self):
        """Run the consumer continuously."""
        try:
            while True:
                msg = self.consumer.poll(1.0)
                
                if msg is None:
                    continue
                    
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.info(f"Reached end of partition {msg.topic()} [{msg.partition()}]")
                    else:
                        logger.error(f"Error: {msg.error()}")
                else:
                    # Process message based on topic
                    if msg.topic() == 'retail-transactions':
                        success = self.process_transaction(msg)
                    elif msg.topic() == 'retail-inventory':
                        success = self.process_inventory_update(msg)
                    
                    # Commit offset if processing was successful
                    if success:
                        self.consumer.commit(msg)
                        
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
        finally:
            self.consumer.close()

if __name__ == '__main__':
    consumer = RetailDataConsumer()
    consumer.run() 