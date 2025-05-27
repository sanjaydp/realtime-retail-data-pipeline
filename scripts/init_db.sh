#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h postgres -U retail_user -d retail_db; do
    sleep 1
done

# Run database migrations
echo "Running database migrations..."
psql -h postgres -U retail_user -d retail_db -f /app/infra/schema.sql

# Create initial data
echo "Creating initial data..."
psql -h postgres -U retail_user -d retail_db << EOF
-- Insert sample products
INSERT INTO product_catalog (product_id, name, category, price)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'Smartphone X', 'Electronics', 999.99),
    ('22222222-2222-2222-2222-222222222222', 'Running Shoes', 'Sports', 89.99),
    ('33333333-3333-3333-3333-333333333333', 'Coffee Maker', 'Home & Kitchen', 49.99),
    ('44444444-4444-4444-4444-444444444444', 'Novel: The Journey', 'Books', 19.99),
    ('55555555-5555-5555-5555-555555555555', 'T-Shirt', 'Clothing', 24.99);

-- Insert sample inventory
INSERT INTO inventory_updates (timestamp, store_location, product_id, new_inventory_count)
VALUES 
    (CURRENT_TIMESTAMP, 'New York', '11111111-1111-1111-1111-111111111111', 50),
    (CURRENT_TIMESTAMP, 'Los Angeles', '22222222-2222-2222-2222-222222222222', 30),
    (CURRENT_TIMESTAMP, 'Chicago', '33333333-3333-3333-3333-333333333333', 20),
    (CURRENT_TIMESTAMP, 'Houston', '44444444-4444-4444-4444-444444444444', 100),
    (CURRENT_TIMESTAMP, 'Phoenix', '55555555-5555-5555-5555-555555555555', 75);
EOF

echo "Database initialization completed!" 