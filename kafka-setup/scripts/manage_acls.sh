#!/bin/bash

# Script to manage Kafka ACLs
# Usage: ./manage_acls.sh <bootstrap_servers> <command> [options]

set -e

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <bootstrap_servers> <command> [options]"
    echo "Commands:"
    echo "  list"
    echo "  add <principal> <resource_type> <resource_name> <operation> <host>"
    echo "  remove <principal> <resource_type> <resource_name> <operation> <host>"
    echo "  describe <principal>"
    exit 1
fi

BOOTSTRAP_SERVERS=$1
COMMAND=$2

# Function to list all ACLs
list_acls() {
    kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVERS} --list
}

# Function to add an ACL
add_acl() {
    if [ "$#" -ne 5 ]; then
        echo "Usage: add <principal> <resource_type> <resource_name> <operation> <host>"
        exit 1
    fi
    
    PRINCIPAL=$1
    RESOURCE_TYPE=$2
    RESOURCE_NAME=$3
    OPERATION=$4
    HOST=$5
    
    kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVERS} \
        --add \
        --principal ${PRINCIPAL} \
        --resource-type ${RESOURCE_TYPE} \
        --resource-name ${RESOURCE_NAME} \
        --operation ${OPERATION} \
        --host ${HOST}
}

# Function to remove an ACL
remove_acl() {
    if [ "$#" -ne 5 ]; then
        echo "Usage: remove <principal> <resource_type> <resource_name> <operation> <host>"
        exit 1
    fi
    
    PRINCIPAL=$1
    RESOURCE_TYPE=$2
    RESOURCE_NAME=$3
    OPERATION=$4
    HOST=$5
    
    kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVERS} \
        --remove \
        --principal ${PRINCIPAL} \
        --resource-type ${RESOURCE_TYPE} \
        --resource-name ${RESOURCE_NAME} \
        --operation ${OPERATION} \
        --host ${HOST}
}

# Function to describe ACLs for a principal
describe_acl() {
    if [ "$#" -ne 1 ]; then
        echo "Usage: describe <principal>"
        exit 1
    fi
    
    PRINCIPAL=$1
    
    kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVERS} \
        --list \
        --principal ${PRINCIPAL}
}

# Main script logic
case ${COMMAND} in
    "list")
        list_acls
        ;;
    "add")
        shift 2
        add_acl "$@"
        ;;
    "remove")
        shift 2
        remove_acl "$@"
        ;;
    "describe")
        shift 2
        describe_acl "$@"
        ;;
    *)
        echo "Unknown command: ${COMMAND}"
        exit 1
        ;;
esac

# Example usage:
# ./manage_acls.sh localhost:9092 list
# ./manage_acls.sh localhost:9092 add User:alice topic retail-transactions Read *
# ./manage_acls.sh localhost:9092 remove User:alice topic retail-transactions Read *
# ./manage_acls.sh localhost:9092 describe User:alice 