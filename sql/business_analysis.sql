-- Business analysis queries for PostgreSQL / UCI Online Retail II.
-- Assumes sql/schema.sql has been applied and valid sale flags are populated.
-- Prices are treated as GBP based on the source dataset.

-- 1. Monthly revenue, order count, units, and average order value.
WITH orders AS (
    SELECT invoice_no, date_trunc('month', MIN(invoice_date)) AS revenue_month,
           SUM(line_revenue) AS order_revenue, SUM(quantity) AS units
    FROM retail_transactions
    WHERE is_valid_sale AND customer_id IS NOT NULL
    GROUP BY invoice_no
)
SELECT revenue_month, SUM(order_revenue) AS revenue,
       COUNT(*) AS orders, SUM(units) AS units,
       AVG(order_revenue) AS average_order_value
FROM orders GROUP BY revenue_month ORDER BY revenue_month;

-- 2. Best-selling products by revenue and units.
SELECT stock_code, MAX(description) AS product_description,
       SUM(quantity) AS units_sold, SUM(line_revenue) AS revenue,
       COUNT(DISTINCT invoice_no) AS orders
FROM retail_transactions
WHERE is_valid_sale
GROUP BY stock_code
ORDER BY revenue DESC
LIMIT 20;

-- 3. Repeat-purchase behaviour and customer value.
WITH customer_orders AS (
    SELECT customer_id, invoice_no, SUM(line_revenue) AS order_revenue
    FROM retail_transactions
    WHERE is_valid_sale AND customer_id IS NOT NULL
    GROUP BY customer_id, invoice_no
)
SELECT customer_id, COUNT(*) AS order_frequency,
       SUM(order_revenue) AS lifetime_revenue,
       AVG(order_revenue) AS average_order_value
FROM customer_orders
GROUP BY customer_id
ORDER BY lifetime_revenue DESC;

-- 4. Monthly cohort retention. Cohort month is each customer's first valid purchase.
WITH customer_months AS (
    SELECT DISTINCT customer_id,
           date_trunc('month', invoice_date)::date AS activity_month
    FROM retail_transactions
    WHERE is_valid_sale AND customer_id IS NOT NULL
),
cohorts AS (
    SELECT customer_id, activity_month,
           MIN(activity_month) OVER (PARTITION BY customer_id) AS cohort_month
    FROM customer_months
),
cohort_activity AS (
    SELECT cohort_month, activity_month,
           ((EXTRACT(YEAR FROM activity_month) - EXTRACT(YEAR FROM cohort_month)) * 12
             + EXTRACT(MONTH FROM activity_month) - EXTRACT(MONTH FROM cohort_month) + 1)::int AS cohort_index,
           COUNT(DISTINCT customer_id) AS active_customers
    FROM cohorts
    GROUP BY cohort_month, activity_month
),
cohort_sizes AS (
    SELECT cohort_month, active_customers AS cohort_size
    FROM cohort_activity WHERE cohort_index = 1
)
SELECT a.cohort_month, a.activity_month, a.cohort_index,
       a.active_customers, s.cohort_size,
       ROUND(100.0 * a.active_customers / NULLIF(s.cohort_size, 0), 2) AS retention_pct
FROM cohort_activity a
JOIN cohort_sizes s USING (cohort_month)
ORDER BY a.cohort_month, a.cohort_index;

-- 5. Country contribution to total revenue.
WITH country_revenue AS (
    SELECT country, SUM(line_revenue) AS revenue
    FROM retail_transactions
    WHERE is_valid_sale
    GROUP BY country
)
SELECT country, revenue,
       ROUND(100.0 * revenue / NULLIF(SUM(revenue) OVER (), 0), 2) AS revenue_share_pct
FROM country_revenue
ORDER BY revenue DESC;

-- 6. Cancellation and return monitoring. Keep these separate from sales.
SELECT date_trunc('month', invoice_date) AS month,
       COUNT(*) FILTER (WHERE is_cancellation) AS cancellation_lines,
       COUNT(*) FILTER (WHERE quantity < 0 OR unit_price <= 0) AS return_or_non_sale_lines,
       SUM(ABS(quantity * unit_price)) FILTER (WHERE is_cancellation OR quantity < 0) AS flagged_value
FROM retail_transactions
GROUP BY 1 ORDER BY 1;
