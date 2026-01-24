-- ============================================================
-- ADVANCED ANALYTICS QUERIES
-- Complex analytical patterns for senior DA interviews
-- ============================================================

-- 1. Year-over-Year Growth with Running Totals
WITH daily_metrics AS (
    SELECT
        order_date,
        strftime('%Y', order_date) AS year,
        strftime('%j', order_date) AS day_of_year,
        SUM(total_amount) AS daily_revenue,
        COUNT(order_id) AS daily_orders
    FROM orders
    WHERE status = 'completed'
    GROUP BY order_date
),
ytd_metrics AS (
    SELECT
        year,
        day_of_year,
        daily_revenue,
        SUM(daily_revenue) OVER (
            PARTITION BY year
            ORDER BY day_of_year
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS ytd_revenue
    FROM daily_metrics
)
SELECT
    t1.year AS current_year,
    t1.day_of_year,
    t1.ytd_revenue AS current_ytd,
    t2.ytd_revenue AS prior_ytd,
    ROUND((t1.ytd_revenue - t2.ytd_revenue) * 100.0 / NULLIF(t2.ytd_revenue, 0), 2) AS yoy_growth_pct
FROM ytd_metrics t1
LEFT JOIN ytd_metrics t2
    ON t1.day_of_year = t2.day_of_year
    AND CAST(t1.year AS INTEGER) = CAST(t2.year AS INTEGER) + 1
WHERE t1.year = strftime('%Y', 'now')
ORDER BY t1.day_of_year;


-- 2. Sessionization - Group Events into Sessions
-- (Using orders as proxy for sessions with 30-min threshold)
WITH ordered_events AS (
    SELECT
        customer_id,
        order_id,
        created_at,
        LAG(created_at) OVER (PARTITION BY customer_id ORDER BY created_at) AS prev_event_time,
        CASE
            WHEN LAG(created_at) OVER (PARTITION BY customer_id ORDER BY created_at) IS NULL
                 OR (julianday(created_at) - julianday(LAG(created_at) OVER (PARTITION BY customer_id ORDER BY created_at))) * 24 * 60 > 30
            THEN 1
            ELSE 0
        END AS is_new_session
    FROM orders
),
session_ids AS (
    SELECT
        *,
        SUM(is_new_session) OVER (PARTITION BY customer_id ORDER BY created_at) AS session_id
    FROM ordered_events
)
SELECT
    customer_id,
    session_id,
    COUNT(*) AS events_in_session,
    MIN(created_at) AS session_start,
    MAX(created_at) AS session_end,
    ROUND((julianday(MAX(created_at)) - julianday(MIN(created_at))) * 24 * 60, 2) AS session_duration_minutes
FROM session_ids
GROUP BY customer_id, session_id
ORDER BY customer_id, session_id;


-- 3. Percentile Analysis with Multiple Metrics
WITH customer_metrics AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(total_amount) AS total_spent,
        AVG(total_amount) AS avg_order_value
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT
    'Order Count' AS metric,
    MIN(order_count) AS min_val,
    MAX(order_count) AS max_val,
    ROUND(AVG(order_count), 2) AS mean_val,
    -- Approximate percentiles using NTILE
    (SELECT AVG(order_count) FROM (
        SELECT order_count, NTILE(4) OVER (ORDER BY order_count) AS quartile
        FROM customer_metrics
    ) WHERE quartile = 1) AS p25,
    (SELECT AVG(order_count) FROM (
        SELECT order_count, NTILE(2) OVER (ORDER BY order_count) AS half
        FROM customer_metrics
    ) WHERE half = 1) AS median,
    (SELECT AVG(order_count) FROM (
        SELECT order_count, NTILE(4) OVER (ORDER BY order_count) AS quartile
        FROM customer_metrics
    ) WHERE quartile = 3) AS p75
FROM customer_metrics
UNION ALL
SELECT
    'Total Spent' AS metric,
    MIN(total_spent),
    MAX(total_spent),
    ROUND(AVG(total_spent), 2),
    (SELECT AVG(total_spent) FROM (
        SELECT total_spent, NTILE(4) OVER (ORDER BY total_spent) AS quartile
        FROM customer_metrics
    ) WHERE quartile = 1),
    (SELECT AVG(total_spent) FROM (
        SELECT total_spent, NTILE(2) OVER (ORDER BY total_spent) AS half
        FROM customer_metrics
    ) WHERE half = 1),
    (SELECT AVG(total_spent) FROM (
        SELECT total_spent, NTILE(4) OVER (ORDER BY total_spent) AS quartile
        FROM customer_metrics
    ) WHERE quartile = 3)
FROM customer_metrics;


-- 4. Funnel Analysis with Drop-off Rates
WITH funnel_steps AS (
    SELECT 'visit' AS step, 1 AS step_order, COUNT(DISTINCT customer_id) AS users
    FROM orders
    UNION ALL
    SELECT 'add_to_cart', 2, COUNT(DISTINCT customer_id)
    FROM orders WHERE total_amount > 0
    UNION ALL
    SELECT 'checkout_started', 3, COUNT(DISTINCT customer_id)
    FROM orders WHERE status IN ('pending', 'completed', 'cancelled')
    UNION ALL
    SELECT 'purchase_complete', 4, COUNT(DISTINCT customer_id)
    FROM orders WHERE status = 'completed'
)
SELECT
    step,
    users,
    LAG(users) OVER (ORDER BY step_order) AS prev_step_users,
    ROUND(users * 100.0 / FIRST_VALUE(users) OVER (ORDER BY step_order), 2) AS conversion_from_start,
    ROUND(users * 100.0 / NULLIF(LAG(users) OVER (ORDER BY step_order), 0), 2) AS step_conversion,
    ROUND((LAG(users) OVER (ORDER BY step_order) - users) * 100.0 /
          NULLIF(LAG(users) OVER (ORDER BY step_order), 0), 2) AS drop_off_rate
FROM funnel_steps
ORDER BY step_order;


-- 5. Moving Window Analysis (7-day, 30-day, 90-day)
WITH daily_revenue AS (
    SELECT
        order_date,
        SUM(total_amount) AS revenue,
        COUNT(order_id) AS orders
    FROM orders
    WHERE status = 'completed'
    GROUP BY order_date
)
SELECT
    order_date,
    revenue,
    orders,
    -- 7-day moving average
    ROUND(AVG(revenue) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS ma_7d,
    -- 30-day moving average
    ROUND(AVG(revenue) OVER (
        ORDER BY order_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 2) AS ma_30d,
    -- 7-day moving sum
    SUM(revenue) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_revenue,
    -- 30-day moving sum
    SUM(revenue) OVER (
        ORDER BY order_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_30d_revenue
FROM daily_revenue
ORDER BY order_date;


-- 6. Customer Journey Analysis
WITH customer_journey AS (
    SELECT
        customer_id,
        order_id,
        order_date,
        total_amount,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_sequence,
        LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_date,
        LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_amount,
        LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS next_order_date
    FROM orders
    WHERE status = 'completed'
)
SELECT
    customer_id,
    order_sequence,
    order_date,
    total_amount,
    julianday(order_date) - julianday(prev_order_date) AS days_since_prev_order,
    total_amount - COALESCE(prev_order_amount, 0) AS order_value_change,
    CASE
        WHEN next_order_date IS NULL THEN 'Latest Order'
        WHEN julianday(next_order_date) - julianday(order_date) > 90 THEN 'Long Gap After'
        ELSE 'Regular'
    END AS order_status
FROM customer_journey
ORDER BY customer_id, order_sequence;


-- 7. Comparative Analysis Across Segments
WITH segment_metrics AS (
    SELECT
        c.segment,
        strftime('%Y-%m', o.order_date) AS month,
        COUNT(DISTINCT c.customer_id) AS customers,
        COUNT(o.order_id) AS orders,
        SUM(o.total_amount) AS revenue
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
    GROUP BY c.segment, strftime('%Y-%m', o.order_date)
)
SELECT
    segment,
    month,
    customers,
    orders,
    revenue,
    ROUND(revenue / customers, 2) AS revenue_per_customer,
    ROUND(orders * 1.0 / customers, 2) AS orders_per_customer,
    -- Rank within month
    RANK() OVER (PARTITION BY month ORDER BY revenue DESC) AS revenue_rank,
    -- MoM growth
    ROUND((revenue - LAG(revenue) OVER (PARTITION BY segment ORDER BY month)) * 100.0 /
          NULLIF(LAG(revenue) OVER (PARTITION BY segment ORDER BY month), 0), 2) AS mom_growth
FROM segment_metrics
ORDER BY month, revenue DESC;


-- 8. Gap Analysis - Days Without Orders
WITH daily_orders AS (
    SELECT DISTINCT order_date
    FROM orders
    WHERE status = 'completed'
),
date_range AS (
    SELECT MIN(order_date) AS start_date, MAX(order_date) AS end_date
    FROM daily_orders
),
all_dates AS (
    SELECT date(start_date, '+' || seq || ' days') AS date
    FROM date_range,
    (SELECT 0 AS seq UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
     UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) AS t1,
    (SELECT 0 AS seq2 UNION SELECT 10 UNION SELECT 20 UNION SELECT 30 UNION SELECT 40
     UNION SELECT 50 UNION SELECT 60 UNION SELECT 70 UNION SELECT 80 UNION SELECT 90) AS t2
    WHERE date(start_date, '+' || (seq + seq2) || ' days') <= end_date
)
SELECT
    ad.date,
    CASE WHEN do.order_date IS NULL THEN 'No Orders' ELSE 'Has Orders' END AS status
FROM all_dates ad
LEFT JOIN daily_orders do ON ad.date = do.order_date
WHERE do.order_date IS NULL
ORDER BY ad.date;


-- 9. Recursive CTE for Category Hierarchy (if applicable)
-- Example: Calculate metrics for hierarchical categories
WITH RECURSIVE category_tree AS (
    -- Base case: top-level categories
    SELECT
        category AS path,
        category,
        1 AS level
    FROM products
    WHERE subcategory IS NULL

    UNION ALL

    -- Recursive case: subcategories
    SELECT
        ct.path || ' > ' || p.subcategory,
        p.subcategory,
        ct.level + 1
    FROM category_tree ct
    JOIN products p ON ct.category = p.category
    WHERE p.subcategory IS NOT NULL
)
SELECT DISTINCT path, level
FROM category_tree
ORDER BY level, path;


-- 10. Time-Weighted Metrics
-- Calculate time-weighted average order value
WITH daily_aov AS (
    SELECT
        order_date,
        AVG(total_amount) AS aov,
        COUNT(*) AS orders,
        julianday(LEAD(order_date) OVER (ORDER BY order_date)) -
        julianday(order_date) AS days_until_next
    FROM orders
    WHERE status = 'completed'
    GROUP BY order_date
)
SELECT
    SUM(aov * COALESCE(days_until_next, 1)) / SUM(COALESCE(days_until_next, 1)) AS time_weighted_aov,
    AVG(aov) AS simple_avg_aov,
    SUM(aov * orders) / SUM(orders) AS order_weighted_aov
FROM daily_aov;


-- 11. Anomaly Detection - Orders Outside Normal Range
WITH daily_stats AS (
    SELECT
        order_date,
        COUNT(*) AS order_count,
        SUM(total_amount) AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY order_date
),
stats AS (
    SELECT
        AVG(order_count) AS avg_orders,
        AVG(order_count * order_count) - AVG(order_count) * AVG(order_count) AS var_orders,
        AVG(revenue) AS avg_revenue,
        AVG(revenue * revenue) - AVG(revenue) * AVG(revenue) AS var_revenue
    FROM daily_stats
)
SELECT
    ds.order_date,
    ds.order_count,
    ds.revenue,
    CASE
        WHEN ABS(ds.order_count - s.avg_orders) > 2 * SQRT(s.var_orders) THEN 'Anomaly'
        ELSE 'Normal'
    END AS order_anomaly,
    CASE
        WHEN ABS(ds.revenue - s.avg_revenue) > 2 * SQRT(s.var_revenue) THEN 'Anomaly'
        ELSE 'Normal'
    END AS revenue_anomaly
FROM daily_stats ds
CROSS JOIN stats s
WHERE ABS(ds.order_count - s.avg_orders) > 2 * SQRT(s.var_orders)
   OR ABS(ds.revenue - s.avg_revenue) > 2 * SQRT(s.var_revenue)
ORDER BY ds.order_date;


-- 12. Self-Join for Sequential Pattern Analysis
-- Find customers who made purchases in consecutive months
WITH monthly_purchases AS (
    SELECT
        customer_id,
        strftime('%Y-%m', order_date) AS purchase_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id, strftime('%Y-%m', order_date)
)
SELECT
    m1.customer_id,
    m1.purchase_month AS month_1,
    m2.purchase_month AS month_2,
    m3.purchase_month AS month_3
FROM monthly_purchases m1
JOIN monthly_purchases m2
    ON m1.customer_id = m2.customer_id
    AND date(m1.purchase_month || '-01', '+1 month') = date(m2.purchase_month || '-01')
JOIN monthly_purchases m3
    ON m2.customer_id = m3.customer_id
    AND date(m2.purchase_month || '-01', '+1 month') = date(m3.purchase_month || '-01')
ORDER BY m1.customer_id, m1.purchase_month;
