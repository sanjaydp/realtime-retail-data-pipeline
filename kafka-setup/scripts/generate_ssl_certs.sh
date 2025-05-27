#!/bin/bash

# Script to generate SSL certificates for Kafka security
# Usage: ./generate_ssl_certs.sh <output_dir> <validity_days>

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <output_dir> <validity_days>"
    exit 1
fi

OUTPUT_DIR=$1
VALIDITY_DAYS=$2

# Create output directory
mkdir -p ${OUTPUT_DIR}

# Generate CA key and certificate
openssl req -new -x509 -keyout ${OUTPUT_DIR}/ca-key -out ${OUTPUT_DIR}/ca-cert -days ${VALIDITY_DAYS} -nodes \
    -subj "/CN=kafka-ca/OU=Kafka/O=Retail/L=City/ST=State/C=US"

# Generate server keystore
keytool -keystore ${OUTPUT_DIR}/kafka.server.keystore.jks -alias localhost -validity ${VALIDITY_DAYS} -genkey \
    -keyalg RSA -dname "CN=localhost,OU=Kafka,O=Retail,L=City,ST=State,C=US" \
    -storepass kafka123 -keypass kafka123

# Generate server CSR
keytool -keystore ${OUTPUT_DIR}/kafka.server.keystore.jks -alias localhost -certreq -file ${OUTPUT_DIR}/server-cert-file \
    -storepass kafka123 -keypass kafka123

# Sign server certificate
openssl x509 -req -CA ${OUTPUT_DIR}/ca-cert -CAkey ${OUTPUT_DIR}/ca-key -in ${OUTPUT_DIR}/server-cert-file \
    -out ${OUTPUT_DIR}/server-cert-signed -days ${VALIDITY_DAYS} -CAcreateserial -passin pass:kafka123

# Import CA certificate into server keystore
keytool -keystore ${OUTPUT_DIR}/kafka.server.keystore.jks -alias CARoot -import -file ${OUTPUT_DIR}/ca-cert \
    -storepass kafka123 -keypass kafka123 -noprompt

# Import signed server certificate into server keystore
keytool -keystore ${OUTPUT_DIR}/kafka.server.keystore.jks -alias localhost -import -file ${OUTPUT_DIR}/server-cert-signed \
    -storepass kafka123 -keypass kafka123 -noprompt

# Create server truststore
keytool -keystore ${OUTPUT_DIR}/kafka.server.truststore.jks -alias CARoot -import -file ${OUTPUT_DIR}/ca-cert \
    -storepass kafka123 -keypass kafka123 -noprompt

# Generate client keystore
keytool -keystore ${OUTPUT_DIR}/kafka.client.keystore.jks -alias localhost -validity ${VALIDITY_DAYS} -genkey \
    -keyalg RSA -dname "CN=localhost,OU=Kafka,O=Retail,L=City,ST=State,C=US" \
    -storepass kafka123 -keypass kafka123

# Generate client CSR
keytool -keystore ${OUTPUT_DIR}/kafka.client.keystore.jks -alias localhost -certreq -file ${OUTPUT_DIR}/client-cert-file \
    -storepass kafka123 -keypass kafka123

# Sign client certificate
openssl x509 -req -CA ${OUTPUT_DIR}/ca-cert -CAkey ${OUTPUT_DIR}/ca-key -in ${OUTPUT_DIR}/client-cert-file \
    -out ${OUTPUT_DIR}/client-cert-signed -days ${VALIDITY_DAYS} -CAcreateserial -passin pass:kafka123

# Import CA certificate into client keystore
keytool -keystore ${OUTPUT_DIR}/kafka.client.keystore.jks -alias CARoot -import -file ${OUTPUT_DIR}/ca-cert \
    -storepass kafka123 -keypass kafka123 -noprompt

# Import signed client certificate into client keystore
keytool -keystore ${OUTPUT_DIR}/kafka.client.keystore.jks -alias localhost -import -file ${OUTPUT_DIR}/client-cert-signed \
    -storepass kafka123 -keypass kafka123 -noprompt

# Create client truststore
keytool -keystore ${OUTPUT_DIR}/kafka.client.truststore.jks -alias CARoot -import -file ${OUTPUT_DIR}/ca-cert \
    -storepass kafka123 -keypass kafka123 -noprompt

echo "SSL certificates generated successfully in ${OUTPUT_DIR}"
echo "Please update your Kafka configuration with the following properties:"
echo "ssl.keystore.location=${OUTPUT_DIR}/kafka.server.keystore.jks"
echo "ssl.keystore.password=kafka123"
echo "ssl.key.password=kafka123"
echo "ssl.truststore.location=${OUTPUT_DIR}/kafka.server.truststore.jks"
echo "ssl.truststore.password=kafka123" 