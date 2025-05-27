provider "aws" {
  region = var.aws_region
}

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "retail-pipeline-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = {
    Environment = var.environment
    Project     = "retail-pipeline"
  }
}

# MSK Cluster
resource "aws_msk_cluster" "kafka" {
  cluster_name           = "retail-kafka-cluster"
  kafka_version         = "2.8.1"
  number_of_broker_nodes = 3

  broker_node_group_info {
    instance_type   = "kafka.t3.small"
    ebs_storage_size = 100
    client_subnets  = module.vpc.private_subnets
    security_groups = [aws_security_group.kafka.id]
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }

  tags = {
    Environment = var.environment
  }
}

# RDS Instance
resource "aws_db_instance" "postgres" {
  identifier           = "retail-postgres"
  engine              = "postgres"
  engine_version      = "13.4"
  instance_class      = "db.t3.medium"
  allocated_storage   = 20
  storage_type        = "gp2"
  db_name             = "retail_db"
  username            = var.db_username
  password            = var.db_password
  skip_final_snapshot = true

  vpc_security_group_ids = [aws_security_group.postgres.id]
  db_subnet_group_name   = aws_db_subnet_group.postgres.name

  tags = {
    Environment = var.environment
  }
}

# EMR Cluster for Spark
resource "aws_emr_cluster" "spark" {
  name          = "retail-spark-cluster"
  release_label = "emr-6.7.0"
  applications  = ["Spark", "Hadoop"]

  service_role = aws_iam_role.emr_service_role.arn

  master_instance_group {
    instance_type = "m5.xlarge"
  }

  core_instance_group {
    instance_type  = "m5.large"
    instance_count = 2
  }

  vpc_options {
    subnet_id = module.vpc.private_subnets[0]
  }

  tags = {
    Environment = var.environment
  }
}

# Security Groups
resource "aws_security_group" "kafka" {
  name        = "kafka-sg"
  description = "Security group for Kafka brokers"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "postgres" {
  name        = "postgres-sg"
  description = "Security group for PostgreSQL"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "db_username" {
  description = "Database username"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
} 