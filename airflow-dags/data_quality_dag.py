from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.amazon.aws.operators.s3 import S3ListOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'retail_data_quality',
    default_args=default_args,
    description='Data quality checks for retail data',
    schedule_interval='0 0 * * *',  # Daily at midnight
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

# Check for missing data
check_missing_data = PostgresOperator(
    task_id='check_missing_data',
    postgres_conn_id='postgres_default',
    sql="""
    SELECT COUNT(*) as missing_count
    FROM retail_transactions
    WHERE transaction_id IS NULL
    OR store_id IS NULL
    OR customer_id IS NULL
    OR product_id IS NULL;
    """,
    dag=dag,
)

# Check for duplicate transactions
check_duplicates = PostgresOperator(
    task_id='check_duplicates',
    postgres_conn_id='postgres_default',
    sql="""
    SELECT transaction_id, COUNT(*) as count
    FROM retail_transactions
    GROUP BY transaction_id
    HAVING COUNT(*) > 1;
    """,
    dag=dag,
)

# Check for invalid amounts
check_invalid_amounts = PostgresOperator(
    task_id='check_invalid_amounts',
    postgres_conn_id='postgres_default',
    sql="""
    SELECT COUNT(*) as invalid_count
    FROM retail_transactions
    WHERE price <= 0 OR quantity <= 0;
    """,
    dag=dag,
)

# Check referential integrity
check_referential_integrity = PostgresOperator(
    task_id='check_referential_integrity',
    postgres_conn_id='postgres_default',
    sql="""
    SELECT COUNT(*) as invalid_count
    FROM retail_transactions t
    LEFT JOIN retail_customers c ON t.customer_id = c.customer_id
    LEFT JOIN retail_products p ON t.product_id = p.product_id
    WHERE c.customer_id IS NULL OR p.product_id IS NULL;
    """,
    dag=dag,
)

# Check data freshness
check_data_freshness = PostgresOperator(
    task_id='check_data_freshness',
    postgres_conn_id='postgres_default',
    sql="""
    SELECT COUNT(*) as stale_count
    FROM retail_transactions
    WHERE timestamp < NOW() - INTERVAL '24 hours';
    """,
    dag=dag,
)

# Export quality metrics to S3
export_quality_metrics = S3ToRedshiftOperator(
    task_id='export_quality_metrics',
    schema='public',
    table='data_quality_metrics',
    s3_bucket='retail-data-quality',
    s3_key='quality_metrics/{{ ds }}/metrics.csv',
    redshift_conn_id='redshift_default',
    aws_conn_id='aws_default',
    dag=dag,
)

# Set task dependencies
[check_missing_data, check_duplicates, check_invalid_amounts, 
 check_referential_integrity, check_data_freshness] >> export_quality_metrics 