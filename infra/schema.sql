-- Create schema for retail data pipeline

-- Transaction metrics table
CREATE TABLE IF NOT EXISTS transaction_metrics (
    id SERIAL PRIMARY KEY,
    transaction_id UUID NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    store_location VARCHAR(100) NOT NULL,
    customer_id UUID NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    is_fraudulent BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Daily sales metrics table
CREATE TABLE IF NOT EXISTS daily_sales_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    store_location VARCHAR(100) NOT NULL,
    total_sales DECIMAL(10,2) NOT NULL,
    transaction_count INTEGER NOT NULL,
    average_transaction_value DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, store_location)
);

-- Inventory updates table
CREATE TABLE IF NOT EXISTS inventory_updates (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    store_location VARCHAR(100) NOT NULL,
    product_id UUID NOT NULL,
    new_inventory_count INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Inventory alerts table
CREATE TABLE IF NOT EXISTS inventory_alerts (
    id SERIAL PRIMARY KEY,
    product_id UUID NOT NULL,
    store_location VARCHAR(100) NOT NULL,
    current_inventory INTEGER NOT NULL,
    alert_timestamp TIMESTAMP NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Product catalog table
CREATE TABLE IF NOT EXISTS product_catalog (
    product_id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_transaction_metrics_timestamp ON transaction_metrics(timestamp);
CREATE INDEX idx_transaction_metrics_store_location ON transaction_metrics(store_location);
CREATE INDEX idx_daily_sales_metrics_date ON daily_sales_metrics(date);
CREATE INDEX idx_inventory_updates_timestamp ON inventory_updates(timestamp);
CREATE INDEX idx_inventory_updates_product_id ON inventory_updates(product_id);
CREATE INDEX idx_inventory_alerts_product_id ON inventory_alerts(product_id);
CREATE INDEX idx_inventory_alerts_is_resolved ON inventory_alerts(is_resolved);

-- Create views
CREATE OR REPLACE VIEW vw_low_inventory_products AS
SELECT 
    p.product_id,
    p.name,
    p.category,
    iu.store_location,
    iu.new_inventory_count,
    iu.timestamp as last_updated
FROM product_catalog p
JOIN inventory_updates iu ON p.product_id = iu.product_id
WHERE iu.new_inventory_count < 10
ORDER BY iu.new_inventory_count ASC;

CREATE OR REPLACE VIEW vw_store_performance AS
SELECT 
    store_location,
    DATE_TRUNC('day', timestamp) as date,
    COUNT(*) as total_transactions,
    SUM(total_amount) as total_sales,
    AVG(total_amount) as average_transaction_value,
    COUNT(CASE WHEN is_fraudulent THEN 1 END) as fraudulent_transactions
FROM transaction_metrics
GROUP BY store_location, DATE_TRUNC('day', timestamp)
ORDER BY date DESC, total_sales DESC;

-- Create functions
CREATE OR REPLACE FUNCTION update_product_catalog()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER trg_update_product_catalog
    BEFORE UPDATE ON product_catalog
    FOR EACH ROW
    EXECUTE FUNCTION update_product_catalog(); 