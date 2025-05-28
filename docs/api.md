# API Documentation

## Overview

The Retail Data Pipeline API provides endpoints for ingesting transaction and inventory data in real-time. The API is built with FastAPI and uses Kafka for message streaming.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. Future versions will implement OAuth2 with JWT tokens.

## Endpoints

### Create Transaction

Creates a new retail transaction and sends it to the Kafka stream.

```http
POST /transactions/
```

#### Request Body

```json
{
  "transaction_id": "TXN1234567890",
  "timestamp": "2024-03-14T12:00:00Z",
  "store_location": "New York",
  "customer_id": "CUST1234",
  "items": [
    {
      "product_id": "P001",
      "name": "Smartphone X",
      "category": "Electronics",
      "price": 999.99,
      "quantity": 1,
      "inventory_count": 50
    }
  ],
  "total_amount": 999.99,
  "payment_method": "Credit Card",
  "is_fraudulent": false
}
```

#### Response

```json
{
  "message": "Transaction created successfully",
  "transaction_id": "TXN1234567890"
}
```

#### Validation Rules

- `transaction_id`: Must start with "TXN"
- `store_location`: Must be a valid store location
- `payment_method`: Must be a valid payment method
- `total_amount`: Must match sum of items
- `items`: Must contain at least one item

### Update Inventory

Updates inventory levels for products and sends the update to Kafka.

```http
POST /inventory/
```

#### Request Body

```json
{
  "timestamp": "2024-03-14T12:00:00Z",
  "store_location": "New York",
  "product_updates": [
    {
      "product_id": "P001",
      "new_inventory_count": 45
    }
  ]
}
```

#### Response

```json
{
  "message": "Inventory update processed successfully"
}
```

#### Validation Rules

- `store_location`: Must be a valid store location
- `product_updates`: Must contain at least one update
- `new_inventory_count`: Must be non-negative

### Health Check

Checks the health status of the API.

```http
GET /health
```

#### Response

```json
{
  "status": "healthy"
}
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

## Rate Limiting

The API implements rate limiting:
- 100 requests per minute per IP
- 1000 requests per hour per IP

## Monitoring

The API exposes Prometheus metrics at `/metrics` endpoint, including:
- Request latency
- Request count
- Error rate
- Kafka producer metrics

## Examples

### Python

```python
import requests

# Create transaction
transaction = {
    "transaction_id": "TXN1234567890",
    "timestamp": "2024-03-14T12:00:00Z",
    "store_location": "New York",
    "customer_id": "CUST1234",
    "items": [
        {
            "product_id": "P001",
            "name": "Smartphone X",
            "category": "Electronics",
            "price": 999.99,
            "quantity": 1,
            "inventory_count": 50
        }
    ],
    "total_amount": 999.99,
    "payment_method": "Credit Card",
    "is_fraudulent": False
}

response = requests.post("http://localhost:8000/transactions/", json=transaction)
print(response.json())
```

### cURL

```bash
# Create transaction
curl -X POST http://localhost:8000/transactions/ \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN1234567890",
    "timestamp": "2024-03-14T12:00:00Z",
    "store_location": "New York",
    "customer_id": "CUST1234",
    "items": [
      {
        "product_id": "P001",
        "name": "Smartphone X",
        "category": "Electronics",
        "price": 999.99,
        "quantity": 1,
        "inventory_count": 50
      }
    ],
    "total_amount": 999.99,
    "payment_method": "Credit Card",
    "is_fraudulent": false
  }'
```

## Best Practices

1. Always validate data before sending
2. Handle rate limiting in your client code
3. Implement retry logic for failed requests
4. Monitor API response times
5. Use appropriate error handling
6. Keep transaction IDs unique
7. Verify total amounts match item sums 