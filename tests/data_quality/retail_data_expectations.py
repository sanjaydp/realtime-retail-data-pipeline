from great_expectations.dataset import PandasDataset
import pandas as pd
import pytest
from datetime import datetime, timedelta

def test_transaction_metrics():
    """Test data quality for transaction metrics."""
    # Create sample data
    data = {
        'transaction_id': ['123', '456', '789'],
        'timestamp': [
            datetime.now(),
            datetime.now() - timedelta(hours=1),
            datetime.now() - timedelta(hours=2)
        ],
        'store_location': ['New York', 'Los Angeles', 'Chicago'],
        'customer_id': ['cust1', 'cust2', 'cust3'],
        'total_amount': [100.50, 75.25, 200.00],
        'payment_method': ['Credit Card', 'Debit Card', 'Cash'],
        'is_fraudulent': [False, False, True]
    }
    df = pd.DataFrame(data)
    dataset = PandasDataset(df)

    # Test expectations
    assert dataset.expect_column_values_to_not_be_null('transaction_id').success
    assert dataset.expect_column_values_to_not_be_null('timestamp').success
    assert dataset.expect_column_values_to_not_be_null('store_location').success
    assert dataset.expect_column_values_to_not_be_null('customer_id').success
    assert dataset.expect_column_values_to_not_be_null('total_amount').success
    assert dataset.expect_column_values_to_not_be_null('payment_method').success
    assert dataset.expect_column_values_to_not_be_null('is_fraudulent').success

    # Test value ranges
    assert dataset.expect_column_values_to_be_between(
        'total_amount', min_value=0
    ).success

    # Test value sets
    valid_payment_methods = ['Credit Card', 'Debit Card', 'Cash', 'Mobile Payment']
    assert dataset.expect_column_values_to_be_in_set(
        'payment_method', valid_payment_methods
    ).success

def test_inventory_updates():
    """Test data quality for inventory updates."""
    # Create sample data
    data = {
        'timestamp': [
            datetime.now(),
            datetime.now() - timedelta(hours=1),
            datetime.now() - timedelta(hours=2)
        ],
        'store_location': ['New York', 'Los Angeles', 'Chicago'],
        'product_id': ['prod1', 'prod2', 'prod3'],
        'new_inventory_count': [50, 30, 20]
    }
    df = pd.DataFrame(data)
    dataset = PandasDataset(df)

    # Test expectations
    assert dataset.expect_column_values_to_not_be_null('timestamp').success
    assert dataset.expect_column_values_to_not_be_null('store_location').success
    assert dataset.expect_column_values_to_not_be_null('product_id').success
    assert dataset.expect_column_values_to_not_be_null('new_inventory_count').success

    # Test value ranges
    assert dataset.expect_column_values_to_be_between(
        'new_inventory_count', min_value=0
    ).success

def test_daily_sales_metrics():
    """Test data quality for daily sales metrics."""
    # Create sample data
    data = {
        'date': [
            datetime.now().date(),
            datetime.now().date() - timedelta(days=1),
            datetime.now().date() - timedelta(days=2)
        ],
        'store_location': ['New York', 'Los Angeles', 'Chicago'],
        'total_sales': [1000.50, 750.25, 2000.00],
        'transaction_count': [100, 75, 200],
        'average_transaction_value': [10.01, 10.00, 10.00]
    }
    df = pd.DataFrame(data)
    dataset = PandasDataset(df)

    # Test expectations
    assert dataset.expect_column_values_to_not_be_null('date').success
    assert dataset.expect_column_values_to_not_be_null('store_location').success
    assert dataset.expect_column_values_to_not_be_null('total_sales').success
    assert dataset.expect_column_values_to_not_be_null('transaction_count').success
    assert dataset.expect_column_values_to_not_be_null('average_transaction_value').success

    # Test value ranges
    assert dataset.expect_column_values_to_be_between(
        'total_sales', min_value=0
    ).success
    assert dataset.expect_column_values_to_be_between(
        'transaction_count', min_value=0
    ).success
    assert dataset.expect_column_values_to_be_between(
        'average_transaction_value', min_value=0
    ).success

if __name__ == '__main__':
    pytest.main([__file__]) 