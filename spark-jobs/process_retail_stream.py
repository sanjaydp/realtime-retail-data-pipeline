from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, window, expr, current_timestamp,
    sum as spark_sum, count, avg, max as spark_max
)
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType,
    TimestampType, ArrayType, BooleanType
)

# Define schemas for Kafka messages
TRANSACTION_SCHEMA = StructType([
    StructField("transaction_id", StringType()),
    StructField("timestamp", StringType()),
    StructField("store_location", StringType()),
    StructField("customer_id", StringType()),
    StructField("items", ArrayType(
        StructType([
            StructField("product_id", StringType()),
            StructField("name", StringType()),
            StructField("category", StringType()),
            StructField("price", DoubleType()),
            StructField("inventory_count", DoubleType())
        ])
    )),
    StructField("total_amount", DoubleType()),
    StructField("payment_method", StringType()),
    StructField("is_fraudulent", BooleanType())
])

INVENTORY_SCHEMA = StructType([
    StructField("timestamp", StringType()),
    StructField("store_location", StringType()),
    StructField("product_updates", ArrayType(
        StructType([
            StructField("product_id", StringType()),
            StructField("new_inventory_count", DoubleType())
        ])
    ))
])

def create_spark_session():
    """Create and configure Spark session."""
    return (SparkSession.builder
            .appName("RetailDataProcessor")
            .config("spark.jars.packages", 
                   "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,"
                   "org.postgresql:postgresql:42.6.0")
            .getOrCreate())

def read_kafka_stream(spark, topic, schema):
    """Read stream from Kafka topic."""
    return (spark
            .readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "localhost:9092")
            .option("subscribe", topic)
            .option("startingOffsets", "latest")
            .load()
            .select(from_json(col("value").cast("string"), schema).alias("data"))
            .select("data.*"))

def process_transactions(transaction_df):
    """Process transaction data with windowed aggregations."""
    return (transaction_df
            .withColumn("timestamp", col("timestamp").cast(TimestampType()))
            .withWatermark("timestamp", "1 minute")
            .groupBy(
                window("timestamp", "5 minutes"),
                "store_location"
            )
            .agg(
                spark_sum("total_amount").alias("total_sales"),
                count("transaction_id").alias("transaction_count"),
                avg("total_amount").alias("average_transaction_value"),
                spark_max("total_amount").alias("max_transaction_value")
            ))

def process_inventory(inventory_df):
    """Process inventory updates."""
    return (inventory_df
            .withColumn("timestamp", col("timestamp").cast(TimestampType()))
            .withWatermark("timestamp", "1 minute")
            .select(
                "timestamp",
                "store_location",
                expr("explode(product_updates) as product_update")
            )
            .select(
                "timestamp",
                "store_location",
                "product_update.product_id",
                "product_update.new_inventory_count"
            ))

def write_to_postgres(df, table_name, checkpoint_location):
    """Write stream to PostgreSQL."""
    return (df.writeStream
            .foreachBatch(lambda batch_df, batch_id: 
                batch_df.write
                .format("jdbc")
                .option("url", "jdbc:postgresql://localhost:5432/retail_db")
                .option("dbtable", table_name)
                .option("user", "retail_user")
                .option("password", "retail_password")
                .mode("append")
                .save())
            .option("checkpointLocation", checkpoint_location)
            .start())

def write_to_s3(df, path, checkpoint_location):
    """Write stream to S3."""
    return (df.writeStream
            .format("parquet")
            .option("path", path)
            .option("checkpointLocation", checkpoint_location)
            .start())

def main():
    # Create Spark session
    spark = create_spark_session()
    
    # Read streams from Kafka
    transaction_stream = read_kafka_stream(spark, "retail-transactions", TRANSACTION_SCHEMA)
    inventory_stream = read_kafka_stream(spark, "inventory-updates", INVENTORY_SCHEMA)
    
    # Process streams
    transaction_metrics = process_transactions(transaction_stream)
    inventory_updates = process_inventory(inventory_stream)
    
    # Write to PostgreSQL
    transaction_query = write_to_postgres(
        transaction_metrics,
        "transaction_metrics",
        "checkpoints/transaction_metrics"
    )
    
    inventory_query = write_to_postgres(
        inventory_updates,
        "inventory_updates",
        "checkpoints/inventory_updates"
    )
    
    # Write to S3
    transaction_s3_query = write_to_s3(
        transaction_stream,
        "s3://retail-data/transactions",
        "checkpoints/transactions_s3"
    )
    
    inventory_s3_query = write_to_s3(
        inventory_stream,
        "s3://retail-data/inventory",
        "checkpoints/inventory_s3"
    )
    
    # Wait for termination
    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    main() 