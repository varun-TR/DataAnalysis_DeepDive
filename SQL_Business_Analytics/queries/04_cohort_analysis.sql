-- ============================================================
-- COHORT ANALYSIS QUERIES
-- Customer retention, cohort behavior, and lifetime progression
-- ============================================================

-- 1. Monthly Cohort Retention Matrix
WITH first_purchase AS (
    SELECT
        customer_id,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
cohort_activity AS (
    SELECT
        fp.cohort_month,
        strftime('%Y-%m', o.order_date) AS activity_month,
        COUNT(DISTINCT o.customer_id) AS customers
    FROM first_purchase fp
    JOIN orders o ON fp.customer_id = o.customer_id AND o.status = 'completed'
    GROUP BY fp.cohort_month, strftime('%Y-%m', o.order_date)
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS size
    FROM first_purchase
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    cs.size AS cohort_size,
    ca.activity_month,
    (julianday(ca.activity_month || '-01') - julianday(ca.cohort_month || '-01')) / 30 AS months_since_acquisition,
    ca.customers AS active_customers,
    ROUND(ca.customers * 100.0 / cs.size, 2) AS retention_pct
FROM cohort_activity ca
JOIN cohort_size cs ON ca.cohort_month = cs.cohort_month
ORDER BY ca.cohort_month, ca.activity_month;


-- 2. Cohort Revenue Analysis
WITH first_purchase AS (
    SELECT
        customer_id,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT
    fp.cohort_month,
    COUNT(DISTINCT fp.customer_id) AS cohort_size,
    strftime('%Y-%m', o.order_date) AS activity_month,
    SUM(o.total_amount) AS cohort_revenue,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value,
    ROUND(SUM(o.total_amount) / COUNT(DISTINCT fp.customer_id), 2) AS revenue_per_customer
FROM first_purchase fp
JOIN orders o ON fp.customer_id = o.customer_id AND o.status = 'completed'
GROUP BY fp.cohort_month, strftime('%Y-%m', o.order_date)
ORDER BY fp.cohort_month, activity_month;


-- 3. Cohort Cumulative LTV
WITH first_purchase AS (
    SELECT
        customer_id,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
monthly_revenue AS (
    SELECT
        fp.cohort_month,
        fp.customer_id,
        (julianday(strftime('%Y-%m', o.order_date) || '-01') -
         julianday(fp.cohort_month || '-01')) / 30 AS months_since_acquisition,
        SUM(o.total_amount) AS revenue
    FROM first_purchase fp
    JOIN orders o ON fp.customer_id = o.customer_id AND o.status = 'completed'
    GROUP BY fp.cohort_month, fp.customer_id, strftime('%Y-%m', o.order_date)
),
cohort_ltv AS (
    SELECT
        cohort_month,
        months_since_acquisition,
        SUM(revenue) AS monthly_revenue,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM monthly_revenue
    GROUP BY cohort_month, months_since_acquisition
)
SELECT
    cohort_month,
    months_since_acquisition,
    monthly_revenue,
    SUM(monthly_revenue) OVER (
        PARTITION BY cohort_month
        ORDER BY months_since_acquisition
    ) AS cumulative_revenue,
    (SELECT COUNT(*) FROM first_purchase WHERE cohort_month = cohort_ltv.cohort_month) AS cohort_size,
    ROUND(
        SUM(monthly_revenue) OVER (
            PARTITION BY cohort_month
            ORDER BY months_since_acquisition
        ) / (SELECT COUNT(*) FROM first_purchase WHERE cohort_month = cohort_ltv.cohort_month),
        2
    ) AS cumulative_ltv_per_customer
FROM cohort_ltv
ORDER BY cohort_month, months_since_acquisition;


-- 4. Cohort Purchase Frequency
WITH first_purchase AS (
    SELECT
        customer_id,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
customer_orders AS (
    SELECT
        fp.cohort_month,
        fp.customer_id,
        COUNT(DISTINCT o.order_id) AS total_orders
    FROM first_purchase fp
    JOIN orders o ON fp.customer_id = o.customer_id AND o.status = 'completed'
    GROUP BY fp.cohort_month, fp.customer_id
)
SELECT
    cohort_month,
    COUNT(*) AS cohort_size,
    ROUND(AVG(total_orders), 2) AS avg_orders_per_customer,
    SUM(CASE WHEN total_orders = 1 THEN 1 ELSE 0 END) AS one_time_buyers,
    SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END) AS repeat_buyers,
    ROUND(
        SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) AS repeat_rate_pct
FROM customer_orders
GROUP BY cohort_month
ORDER BY cohort_month;


-- 5. First Month vs Long-term Value Comparison
WITH first_purchase AS (
    SELECT
        customer_id,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month,
        MIN(order_date) AS first_order_date
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
customer_value AS (
    SELECT
        fp.customer_id,
        fp.cohort_month,
        SUM(CASE
            WHEN o.order_date < date(fp.first_order_date, '+30 days')
            THEN o.total_amount ELSE 0
        END) AS first_30_days_value,
        SUM(o.total_amount) AS total_ltv
    FROM first_purchase fp
    JOIN orders o ON fp.customer_id = o.customer_id AND o.status = 'completed'
    GROUP BY fp.customer_id, fp.cohort_month
)
SELECT
    cohort_month,
    COUNT(*) AS customers,
    ROUND(AVG(first_30_days_value), 2) AS avg_first_30_days,
    ROUND(AVG(total_ltv), 2) AS avg_total_ltv,
    ROUND(AVG(total_ltv) / NULLIF(AVG(first_30_days_value), 0), 2) AS ltv_multiplier
FROM customer_value
GROUP BY cohort_month
ORDER BY cohort_month;


-- 6. Cohort Behavior Changes Over Time
WITH first_purchase AS (
    SELECT
        customer_id,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
order_sequence AS (
    SELECT
        fp.customer_id,
        fp.cohort_month,
        o.order_id,
        o.total_amount,
        ROW_NUMBER() OVER (PARTITION BY fp.customer_id ORDER BY o.order_date) AS order_number
    FROM first_purchase fp
    JOIN orders o ON fp.customer_id = o.customer_id AND o.status = 'completed'
)
SELECT
    cohort_month,
    order_number,
    COUNT(*) AS customers,
    ROUND(AVG(total_amount), 2) AS avg_order_value,
    SUM(total_amount) AS total_revenue
FROM order_sequence
WHERE order_number <= 10
GROUP BY cohort_month, order_number
ORDER BY cohort_month, order_number;


-- 7. Time to Second Purchase by Cohort
WITH first_orders AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
second_orders AS (
    SELECT
        o.customer_id,
        MIN(o.order_date) AS second_order_date
    FROM orders o
    JOIN first_orders fo ON o.customer_id = fo.customer_id
    WHERE o.status = 'completed'
      AND o.order_date > fo.first_order_date
    GROUP BY o.customer_id
)
SELECT
    fo.cohort_month,
    COUNT(DISTINCT fo.customer_id) AS total_customers,
    COUNT(DISTINCT so.customer_id) AS customers_with_repeat,
    ROUND(AVG(julianday(so.second_order_date) - julianday(fo.first_order_date)), 1) AS avg_days_to_second_purchase,
    MIN(julianday(so.second_order_date) - julianday(fo.first_order_date)) AS min_days,
    MAX(julianday(so.second_order_date) - julianday(fo.first_order_date)) AS max_days
FROM first_orders fo
LEFT JOIN second_orders so ON fo.customer_id = so.customer_id
GROUP BY fo.cohort_month
ORDER BY fo.cohort_month;


-- 8. Cohort Quality Score
-- Composite metric combining retention, LTV, and frequency
WITH first_purchase AS (
    SELECT
        customer_id,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
cohort_metrics AS (
    SELECT
        fp.cohort_month,
        COUNT(DISTINCT fp.customer_id) AS cohort_size,
        COUNT(DISTINCT CASE
            WHEN julianday('now') - julianday(o.order_date) <= 90
            THEN o.customer_id
        END) AS active_last_90d,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(o.total_amount) AS total_revenue
    FROM first_purchase fp
    JOIN orders o ON fp.customer_id = o.customer_id AND o.status = 'completed'
    GROUP BY fp.cohort_month
)
SELECT
    cohort_month,
    cohort_size,
    ROUND(active_last_90d * 100.0 / cohort_size, 2) AS retention_90d_pct,
    ROUND(total_orders * 1.0 / cohort_size, 2) AS orders_per_customer,
    ROUND(total_revenue / cohort_size, 2) AS ltv,
    -- Quality score (weighted average of normalized metrics)
    ROUND(
        (active_last_90d * 100.0 / cohort_size * 0.3) +
        (total_orders * 1.0 / cohort_size * 10 * 0.3) +
        (total_revenue / cohort_size / 10 * 0.4),
        2
    ) AS quality_score
FROM cohort_metrics
ORDER BY quality_score DESC;


-- 9. Cohort Channel Analysis
WITH first_purchase AS (
    SELECT
        customer_id,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT
    fp.cohort_month,
    o.payment_method AS channel,
    COUNT(DISTINCT fp.customer_id) AS customers,
    SUM(o.total_amount) AS revenue,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value
FROM first_purchase fp
JOIN orders o ON fp.customer_id = o.customer_id AND o.status = 'completed'
GROUP BY fp.cohort_month, o.payment_method
ORDER BY fp.cohort_month, customers DESC;


-- 10. Cohort Comparison Dashboard Query
WITH first_purchase AS (
    SELECT
        customer_id,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month,
        MIN(order_date) AS first_order_date
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
cohort_summary AS (
    SELECT
        fp.cohort_month,
        COUNT(DISTINCT fp.customer_id) AS acquired,
        COUNT(DISTINCT CASE WHEN o.order_date > fp.first_order_date THEN o.customer_id END) AS retained,
        SUM(o.total_amount) AS total_revenue,
        COUNT(o.order_id) AS total_orders
    FROM first_purchase fp
    JOIN orders o ON fp.customer_id = o.customer_id AND o.status = 'completed'
    GROUP BY fp.cohort_month
)
SELECT
    cohort_month,
    acquired AS customers_acquired,
    retained AS customers_retained,
    ROUND(retained * 100.0 / acquired, 2) AS retention_rate,
    total_orders,
    ROUND(total_orders * 1.0 / acquired, 2) AS orders_per_customer,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(total_revenue / acquired, 2) AS revenue_per_customer,
    ROUND(total_revenue / total_orders, 2) AS avg_order_value
FROM cohort_summary
ORDER BY cohort_month;
