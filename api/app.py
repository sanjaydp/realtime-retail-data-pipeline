from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import json
from confluent_kafka import Producer
import logging
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config_path = Path(__file__).parent.parent / 'data-generator' / 'config.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Initialize Kafka producer
producer = Producer({
    'bootstrap.servers': config['kafka']['bootstrap_servers']
})

app = FastAPI(
    title="Retail Data Ingestion API",
    description="API for ingesting retail transaction and inventory data",
    version="1.0.0"
)

class ProductItem(BaseModel):
    product_id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    price: float = Field(..., gt=0, description="Product price")
    quantity: int = Field(..., gt=0, description="Quantity purchased")
    inventory_count: int = Field(..., ge=0, description="Current inventory count")

    @validator('product_id')
    def validate_product_id(cls, v):
        if not v.startswith('P'):
            raise ValueError('Product ID must start with P')
        return v

class Transaction(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Transaction timestamp")
    store_location: str = Field(..., description="Store location")
    customer_id: str = Field(..., description="Customer identifier")
    items: List[ProductItem] = Field(..., min_items=1, description="List of purchased items")
    total_amount: float = Field(..., gt=0, description="Total transaction amount")
    payment_method: str = Field(..., description="Payment method used")
    is_fraudulent: bool = Field(default=False, description="Fraud flag")

    @validator('transaction_id')
    def validate_transaction_id(cls, v):
        if not v.startswith('TXN'):
            raise ValueError('Transaction ID must start with TXN')
        return v

    @validator('store_location')
    def validate_store_location(cls, v):
        valid_locations = [store['location'] for store in config['stores']]
        if v not in valid_locations:
            raise ValueError(f'Invalid store location. Must be one of: {valid_locations}')
        return v

    @validator('payment_method')
    def validate_payment_method(cls, v):
        if v not in config['payment_methods']:
            raise ValueError(f'Invalid payment method. Must be one of: {config["payment_methods"]}')
        return v

class InventoryUpdate(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now, description="Update timestamp")
    store_location: str = Field(..., description="Store location")
    product_updates: List[dict] = Field(..., min_items=1, description="List of product updates")

    @validator('store_location')
    def validate_store_location(cls, v):
        valid_locations = [store['location'] for store in config['stores']]
        if v not in valid_locations:
            raise ValueError(f'Invalid store location. Must be one of: {valid_locations}')
        return v

def delivery_report(err, msg):
    """Callback for message delivery reports."""
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def send_to_kafka(topic: str, data: dict):
    """Send data to Kafka topic."""
    try:
        producer.produce(
            topic,
            json.dumps(data).encode('utf-8'),
            callback=delivery_report
        )
        producer.poll(0)
    except Exception as e:
        logger.error(f"Error sending message to Kafka: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message to Kafka")

@app.post("/transactions/", status_code=201)
async def create_transaction(transaction: Transaction, background_tasks: BackgroundTasks):
    """Create a new transaction."""
    try:
        # Validate total amount matches items
        calculated_total = sum(item.price * item.quantity for item in transaction.items)
        if abs(calculated_total - transaction.total_amount) > 0.01:
            raise HTTPException(
                status_code=400,
                detail="Total amount does not match sum of items"
            )

        # Send to Kafka in background
        background_tasks.add_task(
            send_to_kafka,
            'retail-transactions',
            transaction.dict()
        )

        return {"message": "Transaction created successfully", "transaction_id": transaction.transaction_id}
    except Exception as e:
        logger.error(f"Error processing transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/inventory/", status_code=201)
async def update_inventory(update: InventoryUpdate, background_tasks: BackgroundTasks):
    """Update inventory levels."""
    try:
        # Send to Kafka in background
        background_tasks.add_task(
            send_to_kafka,
            'inventory-updates',
            update.dict()
        )

        return {"message": "Inventory update processed successfully"}
    except Exception as e:
        logger.error(f"Error processing inventory update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 