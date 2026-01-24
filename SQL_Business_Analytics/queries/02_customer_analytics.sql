-- ============================================================
-- CUSTOMER ANALYTICS QUERIES
-- Customer behavior, segmentation, and lifetime value analysis
-- ============================================================

-- 1. Customer Lifetime Value (CLV) Calculation
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.signup_date,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value,
    julianday('now') - julianday(c.signup_date) AS customer_age_days,
    ROUND(
        SUM(o.total_amount) /
        NULLIF((julianday('now') - julianday(c.signup_date)) / 365.0, 0),
        2
    ) AS annual_value
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
GROUP BY c.customer_id, c.first_name, c.last_name, c.signup_date
ORDER BY total_spent DESC;


-- 2. RFM Segmentation (Recency, Frequency, Monetary)
WITH rfm_base AS (
    SELECT
        customer_id,
        julianday('now') - julianday(MAX(order_date)) AS recency_days,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(total_amount) AS monetary
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT
        customer_id,
        recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency) AS f_score,
        NTILE(5) OVER (ORDER BY monetary) AS m_score
    FROM rfm_base
)
SELECT
    customer_id,
    recency_days,
    frequency,
    ROUND(monetary, 2) AS monetary,
    r_score,
    f_score,
    m_score,
    r_score || f_score || m_score AS rfm_segment,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score <= 2 THEN 'Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'Cant Lose Them'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Lost'
        ELSE 'Others'
    END AS customer_segment
FROM rfm_scores
ORDER BY monetary DESC;


-- 3. New vs Returning Customer Analysis
WITH customer_orders AS (
    SELECT
        customer_id,
        order_id,
        order_date,
        total_amount,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_number
    FROM orders
    WHERE status = 'completed'
)
SELECT
    strftime('%Y-%m', order_date) AS month,
    SUM(CASE WHEN order_number = 1 THEN 1 ELSE 0 END) AS new_customers,
    SUM(CASE WHEN order_number > 1 THEN 1 ELSE 0 END) AS returning_customers,
    SUM(CASE WHEN order_number = 1 THEN total_amount ELSE 0 END) AS new_customer_revenue,
    SUM(CASE WHEN order_number > 1 THEN total_amount ELSE 0 END) AS returning_customer_revenue,
    ROUND(
        SUM(CASE WHEN order_number > 1 THEN 1 ELSE 0 END) * 100.0 /
        COUNT(*),
        2
    ) AS returning_pct
FROM customer_orders
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;


-- 4. Customer Purchase Frequency Distribution
WITH purchase_counts AS (
    SELECT
        customer_id,
        COUNT(order_id) AS order_count
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT
    order_count AS purchases,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_customers
FROM purchase_counts
GROUP BY order_count
ORDER BY order_count;


-- 5. Time Between Purchases Analysis
WITH customer_orders AS (
    SELECT
        customer_id,
        order_date,
        LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_date
    FROM orders
    WHERE status = 'completed'
)
SELECT
    customer_id,
    AVG(julianday(order_date) - julianday(prev_order_date)) AS avg_days_between_orders,
    MIN(julianday(order_date) - julianday(prev_order_date)) AS min_days_between,
    MAX(julianday(order_date) - julianday(prev_order_date)) AS max_days_between,
    COUNT(*) - 1 AS repeat_purchases
FROM customer_orders
WHERE prev_order_date IS NOT NULL
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY avg_days_between_orders;


-- 6. Customer Acquisition by Month with Retention
WITH first_order AS (
    SELECT
        customer_id,
        strftime('%Y-%m', MIN(order_date)) AS acquisition_month
    FROM orders
    GROUP BY customer_id
),
monthly_activity AS (
    SELECT
        f.acquisition_month,
        strftime('%Y-%m', o.order_date) AS activity_month,
        COUNT(DISTINCT o.customer_id) AS active_customers
    FROM first_order f
    JOIN orders o ON f.customer_id = o.customer_id
    WHERE o.status = 'completed'
    GROUP BY f.acquisition_month, strftime('%Y-%m', o.order_date)
)
SELECT
    acquisition_month,
    activity_month,
    active_customers,
    FIRST_VALUE(active_customers) OVER (
        PARTITION BY acquisition_month
        ORDER BY activity_month
    ) AS cohort_size,
    ROUND(
        active_customers * 100.0 /
        FIRST_VALUE(active_customers) OVER (
            PARTITION BY acquisition_month
            ORDER BY activity_month
        ),
        2
    ) AS retention_pct
FROM monthly_activity
ORDER BY acquisition_month, activity_month;


-- 7. Customer Segment Performance
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_revenue,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value,
    ROUND(SUM(o.total_amount) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
GROUP BY c.segment
ORDER BY total_revenue DESC;


-- 8. Customer Churn Risk Identification
-- Customers who haven't ordered in 90+ days but were previously active
WITH customer_activity AS (
    SELECT
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.email,
        MAX(o.order_date) AS last_order_date,
        COUNT(o.order_id) AS total_orders,
        SUM(o.total_amount) AS total_spent,
        julianday('now') - julianday(MAX(o.order_date)) AS days_since_last_order
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
    GROUP BY c.customer_id, c.first_name, c.last_name, c.email
)
SELECT
    customer_id,
    customer_name,
    email,
    last_order_date,
    total_orders,
    ROUND(total_spent, 2) AS total_spent,
    days_since_last_order,
    CASE
        WHEN days_since_last_order > 180 THEN 'High Risk'
        WHEN days_since_last_order > 90 THEN 'Medium Risk'
        WHEN days_since_last_order > 60 THEN 'Low Risk'
        ELSE 'Active'
    END AS churn_risk
FROM customer_activity
WHERE total_orders >= 2  -- Had repeat purchases
ORDER BY days_since_last_order DESC;


-- 9. Customer Geographic Analysis
SELECT
    c.country,
    c.city,
    COUNT(DISTINCT c.customer_id) AS customers,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(o.total_amount) AS revenue,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value,
    ROUND(SUM(o.total_amount) / COUNT(DISTINCT c.customer_id), 2) AS ltv
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
GROUP BY c.country, c.city
HAVING COUNT(DISTINCT c.customer_id) >= 5
ORDER BY revenue DESC;


-- 10. First Purchase Product Analysis
-- What products do customers buy first?
WITH first_orders AS (
    SELECT
        o.customer_id,
        o.order_id,
        o.order_date,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date) AS order_rank
    FROM orders o
    WHERE o.status = 'completed'
)
SELECT
    p.category,
    p.name AS product_name,
    COUNT(DISTINCT fo.customer_id) AS first_purchase_count,
    ROUND(
        COUNT(DISTINCT fo.customer_id) * 100.0 /
        (SELECT COUNT(DISTINCT customer_id) FROM first_orders WHERE order_rank = 1),
        2
    ) AS pct_of_first_purchases
FROM first_orders fo
JOIN order_items oi ON fo.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE fo.order_rank = 1
GROUP BY p.category, p.name
ORDER BY first_purchase_count DESC
LIMIT 20;
