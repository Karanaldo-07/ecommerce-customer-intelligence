-- UCI Online Retail II line-item staging schema.
-- Preserve raw transaction signs and cancellation invoices; filter only in analysis views.
CREATE TABLE IF NOT EXISTS retail_transactions (
    transaction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    invoice_no VARCHAR(20) NOT NULL,
    stock_code VARCHAR(40),
    description TEXT,
    quantity INTEGER,
    invoice_date TIMESTAMP,
    unit_price NUMERIC(12, 4),
    customer_id VARCHAR(20),
    country VARCHAR(100),
    is_cancellation BOOLEAN NOT NULL DEFAULT FALSE,
    is_valid_sale BOOLEAN NOT NULL DEFAULT FALSE,
    line_revenue NUMERIC(14, 4)
);
CREATE INDEX IF NOT EXISTS idx_retail_invoice_date ON retail_transactions(invoice_date);
CREATE INDEX IF NOT EXISTS idx_retail_customer_date ON retail_transactions(customer_id, invoice_date);
CREATE INDEX IF NOT EXISTS idx_retail_country ON retail_transactions(country);

-- Monthly revenue: valid positive sale lines only; dataset prices are treated as GBP.
SELECT date_trunc('month', invoice_date) AS revenue_month,
       SUM(quantity * unit_price) AS gross_line_revenue,
       COUNT(DISTINCT invoice_no) AS invoice_count
FROM retail_transactions
WHERE is_valid_sale
GROUP BY 1
ORDER BY 1;

-- Customer-level RFM base. Recency reference date should be explicitly documented.
SELECT customer_id,
       MAX(invoice_date) AS last_purchase,
       COUNT(DISTINCT invoice_no) AS frequency,
       SUM(quantity * unit_price) AS monetary
FROM retail_transactions
WHERE is_valid_sale AND customer_id IS NOT NULL
GROUP BY customer_id
ORDER BY monetary DESC;
