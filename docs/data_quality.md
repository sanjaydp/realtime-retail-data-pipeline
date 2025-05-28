# Data Quality Documentation

## Overview

The retail data pipeline implements comprehensive data quality checks using Great Expectations. These checks ensure data integrity, consistency, and reliability across all data sources.

## Validation Rules

### Transaction Data

#### Schema Validation
- Required columns: `transaction_id`, `timestamp`, `store_location`, `customer_id`, `total_amount`, `payment_method`
- Data types:
  - `transaction_id`: string
  - `timestamp`: datetime
  - `total_amount`: float

#### Value Validation
- `transaction_id`: Must match pattern `^TXN[0-9]+$`
- `total_amount`: Must be between 0.01 and 100000.00
- `timestamp`: Must be within last 7 days
- `store_location`: Must be in valid locations list
- `payment_method`: Must be in valid payment methods list

#### Uniqueness
- `transaction_id`: Must be unique

### Inventory Data

#### Schema Validation
- Required columns: `timestamp`, `store_location`, `product_id`, `new_inventory_count`
- Data types:
  - `timestamp`: datetime
  - `product_id`: string
  - `new_inventory_count`: integer

#### Value Validation
- `product_id`: Must match pattern `^P[0-9]{3}$`
- `new_inventory_count`: Must be between 0 and 1000
- `store_location`: Must be in valid locations list
- `timestamp`: Must be within last 7 days

### Product Data

#### Schema Validation
- Required columns: `product_id`, `name`, `category`, `price`
- Data types:
  - `product_id`: string
  - `name`: string
  - `category`: string
  - `price`: float

#### Value Validation
- `product_id`: Must match pattern `^P[0-9]{3}$`
- `price`: Must be between 0.01 and 10000.00
- `category`: Must be in valid categories list

#### Uniqueness
- `product_id`: Must be unique

### Customer Data

#### Schema Validation
- Required columns: `customer_id`, `first_purchase_date`, `customer_segment`, `total_spent`
- Data types:
  - `customer_id`: string
  - `first_purchase_date`: datetime
  - `customer_segment`: string
  - `total_spent`: float

#### Value Validation
- `customer_id`: Must match pattern `^CUST[0-9]{4}$`
- `total_spent`: Must be between 0.00 and 1000000.00
- `customer_segment`: Must be in valid segments list

#### Uniqueness
- `customer_id`: Must be unique

## Implementation

### Great Expectations Suite

The validation rules are implemented using Great Expectations' expectation suite:

```python
def validate_transactions(df: pd.DataFrame) -> dict:
    dataset = PandasDataset(df)
    
    # Basic schema validation
    dataset.expect_column_to_exist("transaction_id")
    dataset.expect_column_values_to_be_of_type("transaction_id", "str")
    
    # Value validation
    dataset.expect_column_values_to_match_regex(
        "transaction_id",
        "^TXN[0-9]+$"
    )
    
    # Uniqueness validation
    dataset.expect_column_values_to_be_unique("transaction_id")
    
    return dataset.get_expectation_suite()
```

### Running Validations

Validations can be run in two ways:

1. **Real-time Validation**:
```python
from tests.data_quality.retail_expectations import validate_transactions

# Validate incoming data
validation_result = validate_transactions(transaction_df)
```

2. **Batch Validation**:
```python
# Run validation on historical data
great_expectations checkpoint run retail_transactions
```

## Monitoring

### Metrics

The following metrics are collected for data quality:

1. **Validation Success Rate**
   - Percentage of records passing all validations
   - Tracked per data type and validation rule

2. **Data Completeness**
   - Percentage of required fields present
   - Tracked per column and data type

3. **Data Accuracy**
   - Percentage of values within expected ranges
   - Tracked per validation rule

4. **Data Timeliness**
   - Age of data
   - Processing latency

### Alerts

Alerts are triggered when:

1. Validation success rate drops below 95%
2. Data completeness drops below 99%
3. Critical fields show unexpected patterns
4. Processing latency exceeds thresholds

## Best Practices

1. **Data Quality Checks**
   - Run validations at data ingestion
   - Implement real-time monitoring
   - Set up automated alerts

2. **Data Cleaning**
   - Handle missing values appropriately
   - Standardize data formats
   - Remove duplicates

3. **Documentation**
   - Document all validation rules
   - Keep track of rule changes
   - Maintain validation history

4. **Monitoring**
   - Track validation metrics
   - Set up dashboards
   - Configure alerts

## Troubleshooting

### Common Issues

1. **Validation Failures**
   - Check data source for changes
   - Verify validation rules
   - Review data transformation logic

2. **Performance Issues**
   - Optimize validation rules
   - Use appropriate batch sizes
   - Monitor system resources

3. **Alert Fatigue**
   - Fine-tune alert thresholds
   - Group related alerts
   - Implement alert suppression

### Support

For data quality issues:
1. Check the validation logs
2. Review the data quality dashboard
3. Contact the data engineering team 