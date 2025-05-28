from great_expectations.dataset import PandasDataset
import pandas as pd
from datetime import datetime, timedelta

def validate_transactions(df: pd.DataFrame) -> dict:
    """Validate transaction data quality."""
    dataset = PandasDataset(df)
    
    # Basic schema validation
    dataset.expect_column_to_exist("transaction_id")
    dataset.expect_column_to_exist("timestamp")
    dataset.expect_column_to_exist("store_location")
    dataset.expect_column_to_exist("customer_id")
    dataset.expect_column_to_exist("total_amount")
    dataset.expect_column_to_exist("payment_method")
    
    # Data type validation
    dataset.expect_column_values_to_be_of_type("transaction_id", "str")
    dataset.expect_column_values_to_be_of_type("timestamp", "datetime64[ns]")
    dataset.expect_column_values_to_be_of_type("total_amount", "float64")
    
    # Value range validation
    dataset.expect_column_values_to_be_between(
        "total_amount",
        min_value=0.01,
        max_value=100000.00
    )
    
    # Format validation
    dataset.expect_column_values_to_match_regex(
        "transaction_id",
        "^TXN[0-9]+$"
    )
    
    # Uniqueness validation
    dataset.expect_column_values_to_be_unique("transaction_id")
    
    # Timestamp validation
    dataset.expect_column_values_to_be_between(
        "timestamp",
        min_value=datetime.now() - timedelta(days=7),
        max_value=datetime.now()
    )
    
    # Store location validation
    valid_locations = [
        "New York", "Los Angeles", "Chicago",
        "Houston", "Phoenix"
    ]
    dataset.expect_column_values_to_be_in_set(
        "store_location",
        valid_locations
    )
    
    # Payment method validation
    valid_payment_methods = [
        "Credit Card", "Debit Card", "Cash",
        "Mobile Payment", "Gift Card"
    ]
    dataset.expect_column_values_to_be_in_set(
        "payment_method",
        valid_payment_methods
    )
    
    return dataset.get_expectation_suite()

def validate_inventory(df: pd.DataFrame) -> dict:
    """Validate inventory data quality."""
    dataset = PandasDataset(df)
    
    # Basic schema validation
    dataset.expect_column_to_exist("timestamp")
    dataset.expect_column_to_exist("store_location")
    dataset.expect_column_to_exist("product_id")
    dataset.expect_column_to_exist("new_inventory_count")
    
    # Data type validation
    dataset.expect_column_values_to_be_of_type("timestamp", "datetime64[ns]")
    dataset.expect_column_values_to_be_of_type("product_id", "str")
    dataset.expect_column_values_to_be_of_type("new_inventory_count", "int64")
    
    # Value range validation
    dataset.expect_column_values_to_be_between(
        "new_inventory_count",
        min_value=0,
        max_value=1000
    )
    
    # Format validation
    dataset.expect_column_values_to_match_regex(
        "product_id",
        "^P[0-9]{3}$"
    )
    
    # Store location validation
    valid_locations = [
        "New York", "Los Angeles", "Chicago",
        "Houston", "Phoenix"
    ]
    dataset.expect_column_values_to_be_in_set(
        "store_location",
        valid_locations
    )
    
    # Timestamp validation
    dataset.expect_column_values_to_be_between(
        "timestamp",
        min_value=datetime.now() - timedelta(days=7),
        max_value=datetime.now()
    )
    
    return dataset.get_expectation_suite()

def validate_products(df: pd.DataFrame) -> dict:
    """Validate product data quality."""
    dataset = PandasDataset(df)
    
    # Basic schema validation
    dataset.expect_column_to_exist("product_id")
    dataset.expect_column_to_exist("name")
    dataset.expect_column_to_exist("category")
    dataset.expect_column_to_exist("price")
    
    # Data type validation
    dataset.expect_column_values_to_be_of_type("product_id", "str")
    dataset.expect_column_values_to_be_of_type("name", "str")
    dataset.expect_column_values_to_be_of_type("category", "str")
    dataset.expect_column_values_to_be_of_type("price", "float64")
    
    # Value range validation
    dataset.expect_column_values_to_be_between(
        "price",
        min_value=0.01,
        max_value=10000.00
    )
    
    # Format validation
    dataset.expect_column_values_to_match_regex(
        "product_id",
        "^P[0-9]{3}$"
    )
    
    # Uniqueness validation
    dataset.expect_column_values_to_be_unique("product_id")
    
    # Category validation
    valid_categories = [
        "Electronics", "Clothing", "Home & Kitchen",
        "Books", "Sports", "Beauty"
    ]
    dataset.expect_column_values_to_be_in_set(
        "category",
        valid_categories
    )
    
    return dataset.get_expectation_suite()

def validate_customers(df: pd.DataFrame) -> dict:
    """Validate customer data quality."""
    dataset = PandasDataset(df)
    
    # Basic schema validation
    dataset.expect_column_to_exist("customer_id")
    dataset.expect_column_to_exist("first_purchase_date")
    dataset.expect_column_to_exist("customer_segment")
    dataset.expect_column_to_exist("total_spent")
    
    # Data type validation
    dataset.expect_column_values_to_be_of_type("customer_id", "str")
    dataset.expect_column_values_to_be_of_type("first_purchase_date", "datetime64[ns]")
    dataset.expect_column_values_to_be_of_type("customer_segment", "str")
    dataset.expect_column_values_to_be_of_type("total_spent", "float64")
    
    # Value range validation
    dataset.expect_column_values_to_be_between(
        "total_spent",
        min_value=0.00,
        max_value=1000000.00
    )
    
    # Format validation
    dataset.expect_column_values_to_match_regex(
        "customer_id",
        "^CUST[0-9]{4}$"
    )
    
    # Uniqueness validation
    dataset.expect_column_values_to_be_unique("customer_id")
    
    # Customer segment validation
    valid_segments = ["Premium", "Regular", "New", "VIP"]
    dataset.expect_column_values_to_be_in_set(
        "customer_segment",
        valid_segments
    )
    
    return dataset.get_expectation_suite() 