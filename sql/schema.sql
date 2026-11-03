-- Initial normalized schema for an order-level e-commerce dataset.
-- Adapt column types and constraints after the selected dataset is inspected.

CREATE TABLE IF NOT EXISTS customers (
    customer_id       VARCHAR(64) PRIMARY KEY,
    first_seen_at     TIMESTAMP,
    country           VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS products (
    product_id        VARCHAR(64) PRIMARY KEY,
    product_name      TEXT,
    category          VARCHAR(150)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id          VARCHAR(64) PRIMARY KEY,
    customer_id       VARCHAR(64) NOT NULL REFERENCES customers(customer_id),
    order_timestamp   TIMESTAMP NOT NULL,
    order_status      VARCHAR(40),
    currency          CHAR(3)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id          VARCHAR(64) NOT NULL REFERENCES orders(order_id),
    product_id        VARCHAR(64) REFERENCES products(product_id),
    quantity          INTEGER NOT NULL CHECK (quantity > 0),
    unit_price        NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    discount_amount   NUMERIC(12, 2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0)
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_timestamp
    ON orders(customer_id, order_timestamp);

CREATE INDEX IF NOT EXISTS idx_orders_timestamp
    ON orders(order_timestamp);

CREATE INDEX IF NOT EXISTS idx_order_items_order
    ON order_items(order_id);

-- Example query: revenue by calendar month.
-- Assumes order status has already been filtered to the business definition
-- of completed/valid orders and currency has been normalized.
--
-- SELECT date_trunc('month', o.order_timestamp) AS order_month,
--        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS net_revenue
-- FROM orders AS o
-- JOIN order_items AS oi ON oi.order_id = o.order_id
-- WHERE o.order_status = 'completed'
-- GROUP BY 1
-- ORDER BY 1;
