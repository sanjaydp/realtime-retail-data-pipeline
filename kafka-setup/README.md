# Kafka Setup Configuration

This directory contains configuration files and scripts for setting up Kafka in different environments.

## Directory Structure

- `local/`: Local development setup
- `staging/`: Staging environment configuration
- `production/`: Production environment configuration
- `scripts/`: Utility scripts for Kafka management

## Environment-Specific Configurations

### Local Development
- Single broker setup
- Minimal resource requirements
- Development-specific topics
- Local monitoring tools

### Staging
- Multi-broker setup (3 brokers)
- Medium resource allocation
- Test data topics
- Basic monitoring

### Production
- Multi-broker setup (5+ brokers)
- High availability configuration
- Production topics
- Full monitoring and alerting

## Setup Instructions

1. Choose the appropriate environment directory
2. Copy the configuration files to your Kafka installation
3. Update the configuration with environment-specific values
4. Start the Kafka cluster using the provided scripts

## Topic Management

Use the provided scripts in the `scripts/` directory to:
- Create topics
- Update topic configurations
- Monitor topic health
- Manage consumer groups

## Security

- SSL/TLS configuration for production
- SASL authentication
- ACL management
- Network security rules

## Monitoring

- JMX metrics configuration
- Prometheus integration
- Grafana dashboards
- Alert rules 