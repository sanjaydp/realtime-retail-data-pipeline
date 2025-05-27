# Kafka Setup for Retail Data Pipeline

This directory contains the Kafka configuration and setup for the real-time retail data pipeline.

## Components

- `docker-compose.yml`: Kafka and Zookeeper container configuration
- `producer_config.py`: Kafka producer configuration for sending retail data
- `consumer_config.py`: Kafka consumer configuration for processing retail data

## Setup Instructions

1. Start Kafka and Zookeeper:
```bash
docker-compose up -d
```

2. Create required topics:
```bash
# Create transactions topic
kafka-topics.sh --create --topic retail-transactions \
    --bootstrap-server localhost:9092 \
    --partitions 3 \
    --replication-factor 1

# Create inventory topic
kafka-topics.sh --create --topic retail-inventory \
    --bootstrap-server localhost:9092 \
    --partitions 3 \
    --replication-factor 1
```

3. Verify topics:
```bash
kafka-topics.sh --list --bootstrap-server localhost:9092
```

## Topic Structure

### retail-transactions
- Key: transaction_id
- Value: JSON containing transaction details
  ```json
  {
    "transaction_id": "uuid",
    "timestamp": "ISO-8601",
    "store_location": "string",
    "customer_id": "uuid",
    "items": [
      {
        "product_id": "uuid",
        "quantity": "integer",
        "price": "decimal"
      }
    ],
    "total_amount": "decimal",
    "payment_method": "string"
  }
  ```

### retail-inventory
- Key: store_location:product_id
- Value: JSON containing inventory updates
  ```json
  {
    "timestamp": "ISO-8601",
    "store_location": "string",
    "product_id": "uuid",
    "new_inventory_count": "integer"
  }
  ```

## Monitoring

Access Kafka Manager at http://localhost:9000 to monitor topics, consumer groups, and broker status. 