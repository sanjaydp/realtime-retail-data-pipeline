# Airflow DAGs for Retail Data Pipeline

This directory contains Apache Airflow DAGs for orchestrating the batch and data quality workflows in the real-time retail data pipeline.

## Prerequisites
- Docker & Docker Compose (recommended for local setup)
- Python 3.8+
- The main project dependencies installed (see root README)

## Setup Instructions

### 1. Clone the Repository (if not already done)
```bash
git clone https://github.com/yourusername/realtime-retail-data-pipeline.git
cd realtime-retail-data-pipeline/airflow-dags
```

### 2. Start Airflow with Docker Compose
A sample `docker-compose.yml` is provided for local Airflow setup. From the `airflow-dags` directory:
```bash
docker-compose up -d
```
This will start the Airflow webserver, scheduler, and supporting services.

- **Airflow UI:** [http://localhost:8080](http://localhost:8080)
- Default credentials: `airflow` / `airflow` (unless changed)

### 3. Configure Connections (if needed)
- Set up connections for PostgreSQL, AWS, and any other services via the Airflow UI (Admin > Connections).
- Example connection IDs used in DAGs: `postgres_default`, `aws_default`, `redshift_default`.

### 4. Trigger DAGs
- In the Airflow UI, enable and trigger the DAGs (e.g., `retail_data_pipeline`, `data_quality_dag`).
- DAGs will orchestrate data quality checks, batch processing, and exports as defined in the Python files in this directory.

### 5. Integration with the Pipeline
- For a full end-to-end demo, see the main project's `README.md` section: **End-to-End Demo**.
- Airflow will coordinate with Kafka, Spark, PostgreSQL, S3, and Great Expectations as part of the pipeline.

## DAGs Included
- `retail_pipeline_dag.py`: Main pipeline orchestration
- `data_quality_dag.py`: Data quality checks and metrics export

## Troubleshooting
- Check Airflow logs in the UI for task failures.
- Ensure all required services (Kafka, PostgreSQL, S3, etc.) are running and accessible.
- Verify connection IDs and credentials in Airflow.

## More Information
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- For support, open an issue in the main repository. 