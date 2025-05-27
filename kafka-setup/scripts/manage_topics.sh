#!/bin/bash

# Kafka Topic Management Script

# Configuration
KAFKA_HOME=${KAFKA_HOME:-"/opt/kafka"}
BOOTSTRAP_SERVERS=${BOOTSTRAP_SERVERS:-"localhost:9092"}
ZOOKEEPER=${ZOOKEEPER:-"localhost:2181"}

# Topic configurations
TRANSACTIONS_TOPIC="retail-transactions"
INVENTORY_TOPIC="retail-inventory"
CUSTOMERS_TOPIC="retail-customers"
PRODUCTS_TOPIC="retail-products"

# Function to create a topic
create_topic() {
    local topic=$1
    local partitions=$2
    local replication=$3
    
    echo "Creating topic: $topic"
    $KAFKA_HOME/bin/kafka-topics.sh --create \
        --bootstrap-server $BOOTSTRAP_SERVERS \
        --topic $topic \
        --partitions $partitions \
        --replication-factor $replication
}

# Function to delete a topic
delete_topic() {
    local topic=$1
    
    echo "Deleting topic: $topic"
    $KAFKA_HOME/bin/kafka-topics.sh --delete \
        --bootstrap-server $BOOTSTRAP_SERVERS \
        --topic $topic
}

# Function to list topics
list_topics() {
    echo "Listing all topics:"
    $KAFKA_HOME/bin/kafka-topics.sh --list \
        --bootstrap-server $BOOTSTRAP_SERVERS
}

# Function to describe a topic
describe_topic() {
    local topic=$1
    
    echo "Describing topic: $topic"
    $KAFKA_HOME/bin/kafka-topics.sh --describe \
        --bootstrap-server $BOOTSTRAP_SERVERS \
        --topic $topic
}

# Function to create all retail topics
create_retail_topics() {
    # Create transactions topic
    create_topic $TRANSACTIONS_TOPIC 3 1
    
    # Create inventory topic
    create_topic $INVENTORY_TOPIC 3 1
    
    # Create customers topic
    create_topic $CUSTOMERS_TOPIC 3 1
    
    # Create products topic
    create_topic $PRODUCTS_TOPIC 3 1
}

# Function to delete all retail topics
delete_retail_topics() {
    delete_topic $TRANSACTIONS_TOPIC
    delete_topic $INVENTORY_TOPIC
    delete_topic $CUSTOMERS_TOPIC
    delete_topic $PRODUCTS_TOPIC
}

# Main script logic
case "$1" in
    "create")
        create_retail_topics
        ;;
    "delete")
        delete_retail_topics
        ;;
    "list")
        list_topics
        ;;
    "describe")
        if [ -z "$2" ]; then
            echo "Please specify a topic name"
            exit 1
        fi
        describe_topic $2
        ;;
    *)
        echo "Usage: $0 {create|delete|list|describe [topic_name]}"
        exit 1
        ;;
esac

exit 0 