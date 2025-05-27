from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.amazon.aws.operators.s3 import S3CopyObjectOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'retail_data_pipeline',
    default_args=default_args,
    description='Daily retail data pipeline tasks',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

# Task 1: Check if new data is available in S3
check_new_data = S3KeySensor(
    task_id='check_new_data',
    bucket_key='transactions/*',
    bucket_name='retail-data',
    aws_conn_id='aws_default',
    dag=dag,
)

# Task 2: Run data quality checks
run_data_quality = GreatExpectationsOperator(
    task_id='run_data_quality',
    data_context_root_dir='/opt/airflow/great_expectations',
    checkpoint_name='retail_transactions_checkpoint',
    dag=dag,
)

# Task 3: Create daily aggregations
create_daily_aggregations = PostgresOperator(
    task_id='create_daily_aggregations',
    postgres_conn_id='postgres_default',
    sql="""
    INSERT INTO daily_sales_metrics (
        date,
        store_location,
        total_sales,
        transaction_count,
        average_transaction_value
    )
    SELECT 
        DATE_TRUNC('day', timestamp) as date,
        store_location,
        SUM(total_amount) as total_sales,
        COUNT(*) as transaction_count,
        AVG(total_amount) as average_transaction_value
    FROM transaction_metrics
    WHERE DATE_TRUNC('day', timestamp) = CURRENT_DATE - INTERVAL '1 day'
    GROUP BY 1, 2;
    """,
    dag=dag,
)

# Task 4: Backup data to S3
backup_to_s3 = S3CopyObjectOperator(
    task_id='backup_to_s3',
    source_bucket_key='transactions/*',
    dest_bucket_key='backups/{{ ds }}/transactions/',
    source_bucket_name='retail-data',
    dest_bucket_name='retail-data-backups',
    aws_conn_id='aws_default',
    dag=dag,
)

# Task 5: Check for low inventory
check_low_inventory = PostgresOperator(
    task_id='check_low_inventory',
    postgres_conn_id='postgres_default',
    sql="""
    INSERT INTO inventory_alerts (
        product_id,
        store_location,
        current_inventory,
        alert_timestamp
    )
    SELECT 
        product_id,
        store_location,
        new_inventory_count,
        CURRENT_TIMESTAMP
    FROM inventory_updates
    WHERE new_inventory_count < 10
    AND DATE_TRUNC('day', timestamp) = CURRENT_DATE;
    """,
    dag=dag,
)

# Task 6: Clean up old data
cleanup_old_data = PostgresOperator(
    task_id='cleanup_old_data',
    postgres_conn_id='postgres_default',
    sql="""
    DELETE FROM transaction_metrics
    WHERE timestamp < CURRENT_DATE - INTERVAL '90 days';
    
    DELETE FROM inventory_updates
    WHERE timestamp < CURRENT_DATE - INTERVAL '90 days';
    """,
    dag=dag,
)

# Define task dependencies
check_new_data >> run_data_quality >> create_daily_aggregations
create_daily_aggregations >> backup_to_s3
check_new_data >> check_low_inventory
backup_to_s3 >> cleanup_old_data 