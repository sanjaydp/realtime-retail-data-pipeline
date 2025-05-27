#!/bin/bash

# Kafka Monitoring Script

# Configuration
KAFKA_HOME=${KAFKA_HOME:-"/opt/kafka"}
BOOTSTRAP_SERVERS=${BOOTSTRAP_SERVERS:-"localhost:9092"}
ZOOKEEPER=${ZOOKEEPER:-"localhost:2181"}

# Function to check broker status
check_broker_status() {
    echo "Checking broker status..."
    $KAFKA_HOME/bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS --list
    if [ $? -eq 0 ]; then
        echo "Broker is running"
    else
        echo "Broker is not responding"
    fi
}

# Function to check consumer groups
check_consumer_groups() {
    echo "Listing consumer groups..."
    $KAFKA_HOME/bin/kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVERS --list
}

# Function to check consumer lag
check_consumer_lag() {
    local group=$1
    if [ -z "$group" ]; then
        echo "Please specify a consumer group"
        return 1
    fi
    
    echo "Checking lag for consumer group: $group"
    $KAFKA_HOME/bin/kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVERS \
        --describe --group $group
}

# Function to check topic details
check_topic_details() {
    local topic=$1
    if [ -z "$topic" ]; then
        echo "Please specify a topic"
        return 1
    fi
    
    echo "Checking details for topic: $topic"
    $KAFKA_HOME/bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS \
        --describe --topic $topic
}

# Function to check broker metrics
check_broker_metrics() {
    echo "Checking broker metrics..."
    $KAFKA_HOME/bin/kafka-run-class.sh kafka.tools.JmxTool \
        --object-name kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec \
        --jmx-url service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi
}

# Function to monitor a specific topic
monitor_topic() {
    local topic=$1
    if [ -z "$topic" ]; then
        echo "Please specify a topic"
        return 1
    fi
    
    echo "Monitoring topic: $topic"
    $KAFKA_HOME/bin/kafka-console-consumer.sh --bootstrap-server $BOOTSTRAP_SERVERS \
        --topic $topic --from-beginning --max-messages 10
}

# Main script logic
case "$1" in
    "status")
        check_broker_status
        ;;
    "groups")
        check_consumer_groups
        ;;
    "lag")
        check_consumer_lag $2
        ;;
    "topic")
        check_topic_details $2
        ;;
    "metrics")
        check_broker_metrics
        ;;
    "monitor")
        monitor_topic $2
        ;;
    *)
        echo "Usage: $0 {status|groups|lag [group]|topic [topic]|metrics|monitor [topic]}"
        exit 1
        ;;
esac

exit 0 