-- ============================================================
-- REVENUE ANALYSIS QUERIES
-- Advanced SQL for business metrics and financial analysis
-- ============================================================

-- 1. Daily Revenue with Running Total
-- Shows daily revenue with cumulative sum
SELECT
    order_date,
    COUNT(order_id) AS orders,
    SUM(total_amount) AS daily_revenue,
    SUM(SUM(total_amount)) OVER (
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total,
    ROUND(AVG(total_amount), 2) AS avg_order_value
FROM orders
WHERE status = 'completed'
GROUP BY order_date
ORDER BY order_date;


-- 2. Monthly Revenue with Month-over-Month Growth
WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', order_date) AS month,
        SUM(total_amount) AS revenue,
        COUNT(DISTINCT order_id) AS orders,
        COUNT(DISTINCT customer_id) AS customers
    FROM orders
    WHERE status = 'completed'
    GROUP BY strftime('%Y-%m', order_date)
)
SELECT
    month,
    revenue,
    orders,
    customers,
    LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month)) * 100.0 /
        NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
        2
    ) AS mom_growth_pct
FROM monthly_revenue
ORDER BY month;


-- 3. Revenue by Day of Week
-- Identify best/worst performing days
SELECT
    CASE strftime('%w', order_date)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS day_of_week,
    COUNT(order_id) AS total_orders,
    SUM(total_amount) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS avg_order_value,
    ROUND(SUM(total_amount) * 100.0 / (SELECT SUM(total_amount) FROM orders WHERE status = 'completed'), 2) AS revenue_pct
FROM orders
WHERE status = 'completed'
GROUP BY strftime('%w', order_date)
ORDER BY total_revenue DESC;


-- 4. Revenue by Category with Market Share
WITH category_revenue AS (
    SELECT
        p.category,
        SUM(oi.quantity * oi.unit_price) AS revenue,
        COUNT(DISTINCT o.order_id) AS orders
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.status = 'completed'
    GROUP BY p.category
)
SELECT
    category,
    revenue,
    orders,
    ROUND(revenue * 100.0 / SUM(revenue) OVER (), 2) AS market_share_pct,
    RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM category_revenue
ORDER BY revenue DESC;


-- 5. 7-Day Moving Average Revenue
WITH daily_revenue AS (
    SELECT
        order_date,
        SUM(total_amount) AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY order_date
)
SELECT
    order_date,
    revenue,
    ROUND(
        AVG(revenue) OVER (
            ORDER BY order_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS moving_avg_7d,
    ROUND(
        AVG(revenue) OVER (
            ORDER BY order_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS moving_avg_30d
FROM daily_revenue
ORDER BY order_date;


-- 6. Revenue Percentile Analysis
-- Identify revenue distribution
WITH order_revenue AS (
    SELECT
        order_id,
        total_amount,
        NTILE(10) OVER (ORDER BY total_amount) AS decile
    FROM orders
    WHERE status = 'completed'
)
SELECT
    decile,
    COUNT(*) AS order_count,
    MIN(total_amount) AS min_revenue,
    MAX(total_amount) AS max_revenue,
    ROUND(AVG(total_amount), 2) AS avg_revenue,
    SUM(total_amount) AS total_revenue
FROM order_revenue
GROUP BY decile
ORDER BY decile;


-- 7. Revenue Concentration (Pareto Analysis)
-- Shows how much revenue comes from top customers
WITH customer_revenue AS (
    SELECT
        customer_id,
        SUM(total_amount) AS total_revenue,
        ROW_NUMBER() OVER (ORDER BY SUM(total_amount) DESC) AS revenue_rank
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
total AS (
    SELECT
        SUM(total_revenue) AS grand_total,
        COUNT(*) AS total_customers
    FROM customer_revenue
)
SELECT
    cr.revenue_rank,
    cr.total_revenue,
    ROUND(cr.total_revenue * 100.0 / t.grand_total, 2) AS pct_of_total,
    ROUND(SUM(cr.total_revenue) OVER (ORDER BY cr.revenue_rank) * 100.0 / t.grand_total, 2) AS cumulative_pct
FROM customer_revenue cr
CROSS JOIN total t
ORDER BY cr.revenue_rank
LIMIT 100;


-- 8. Average Order Value Trend
SELECT
    strftime('%Y-%m', order_date) AS month,
    COUNT(order_id) AS total_orders,
    SUM(total_amount) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS aov,
    ROUND(AVG(total_amount) - LAG(AVG(total_amount)) OVER (ORDER BY strftime('%Y-%m', order_date)), 2) AS aov_change
FROM orders
WHERE status = 'completed'
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;


-- 9. Revenue by Payment Method
SELECT
    payment_method,
    COUNT(order_id) AS orders,
    SUM(total_amount) AS revenue,
    ROUND(AVG(total_amount), 2) AS avg_order,
    ROUND(SUM(total_amount) * 100.0 / (SELECT SUM(total_amount) FROM orders WHERE status = 'completed'), 2) AS revenue_share_pct
FROM orders
WHERE status = 'completed'
GROUP BY payment_method
ORDER BY revenue DESC;


-- 10. Hourly Revenue Pattern
-- Useful for operational planning
SELECT
    strftime('%H', created_at) AS hour,
    COUNT(order_id) AS orders,
    SUM(total_amount) AS revenue,
    ROUND(AVG(total_amount), 2) AS avg_order_value
FROM orders
WHERE status = 'completed'
GROUP BY strftime('%H', created_at)
ORDER BY hour;
