-- ============================================================
-- PRODUCT PERFORMANCE QUERIES
-- Product metrics, inventory analysis, and profitability
-- ============================================================

-- 1. Top Products by Revenue
SELECT
    p.product_id,
    p.name AS product_name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * oi.unit_price) AS total_revenue,
    ROUND(AVG(oi.unit_price), 2) AS avg_selling_price,
    COUNT(DISTINCT o.order_id) AS order_count,
    RANK() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS revenue_rank
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed'
GROUP BY p.product_id, p.name, p.category
ORDER BY total_revenue DESC
LIMIT 20;


-- 2. Product Profit Margin Analysis
SELECT
    p.product_id,
    p.name AS product_name,
    p.category,
    p.price AS list_price,
    p.cost,
    ROUND((p.price - p.cost) * 100.0 / p.price, 2) AS list_margin_pct,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * oi.unit_price) AS revenue,
    SUM(oi.quantity * p.cost) AS total_cost,
    SUM(oi.quantity * (oi.unit_price - p.cost)) AS gross_profit,
    ROUND(
        SUM(oi.quantity * (oi.unit_price - p.cost)) * 100.0 /
        NULLIF(SUM(oi.quantity * oi.unit_price), 0),
        2
    ) AS actual_margin_pct
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed'
GROUP BY p.product_id, p.name, p.category, p.price, p.cost
HAVING SUM(oi.quantity) > 0
ORDER BY gross_profit DESC;


-- 3. Category Performance Comparison
WITH category_metrics AS (
    SELECT
        p.category,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price) AS revenue,
        SUM(oi.quantity * (oi.unit_price - p.cost)) AS profit,
        COUNT(DISTINCT o.order_id) AS orders,
        COUNT(DISTINCT o.customer_id) AS customers
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed'
    GROUP BY p.category
)
SELECT
    category,
    units_sold,
    revenue,
    profit,
    orders,
    customers,
    ROUND(revenue * 100.0 / SUM(revenue) OVER (), 2) AS revenue_share_pct,
    ROUND(profit * 100.0 / revenue, 2) AS margin_pct,
    ROUND(revenue / customers, 2) AS revenue_per_customer
FROM category_metrics
ORDER BY revenue DESC;


-- 4. Product Sales Trend (Monthly)
SELECT
    strftime('%Y-%m', o.order_date) AS month,
    p.category,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * oi.unit_price) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed'
GROUP BY strftime('%Y-%m', o.order_date), p.category
ORDER BY month, category;


-- 5. Product Affinity Analysis (Frequently Bought Together)
WITH order_products AS (
    SELECT
        o.order_id,
        p.product_id,
        p.name AS product_name
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.status = 'completed'
)
SELECT
    op1.product_name AS product_1,
    op2.product_name AS product_2,
    COUNT(*) AS times_bought_together,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(DISTINCT order_id) FROM order_products WHERE product_name = op1.product_name),
        2
    ) AS affinity_pct
FROM order_products op1
JOIN order_products op2
    ON op1.order_id = op2.order_id
    AND op1.product_id < op2.product_id
GROUP BY op1.product_name, op2.product_name
HAVING COUNT(*) >= 5
ORDER BY times_bought_together DESC
LIMIT 20;


-- 6. Slow Moving Products
SELECT
    p.product_id,
    p.name AS product_name,
    p.category,
    p.stock_quantity AS current_stock,
    COALESCE(SUM(oi.quantity), 0) AS total_sold_90d,
    CASE
        WHEN COALESCE(SUM(oi.quantity), 0) = 0 THEN 'No Sales'
        WHEN p.stock_quantity / (SUM(oi.quantity) / 90.0) > 180 THEN 'Overstocked'
        WHEN p.stock_quantity / (SUM(oi.quantity) / 90.0) > 90 THEN 'Slow Moving'
        ELSE 'Normal'
    END AS inventory_status
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id
    AND o.status = 'completed'
    AND o.order_date >= date('now', '-90 days')
WHERE p.is_active = 1
GROUP BY p.product_id, p.name, p.category, p.stock_quantity
ORDER BY total_sold_90d ASC;


-- 7. Price Sensitivity Analysis
WITH price_bands AS (
    SELECT
        p.product_id,
        p.name,
        p.price,
        CASE
            WHEN p.price < 25 THEN '$0-25'
            WHEN p.price < 50 THEN '$25-50'
            WHEN p.price < 100 THEN '$50-100'
            WHEN p.price < 200 THEN '$100-200'
            ELSE '$200+'
        END AS price_band,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed'
    GROUP BY p.product_id, p.name, p.price
)
SELECT
    price_band,
    COUNT(DISTINCT product_id) AS products,
    SUM(units_sold) AS total_units,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(units_sold), 2) AS avg_units_per_product,
    ROUND(SUM(revenue) * 100.0 / (SELECT SUM(revenue) FROM price_bands), 2) AS revenue_share_pct
FROM price_bands
GROUP BY price_band
ORDER BY
    CASE price_band
        WHEN '$0-25' THEN 1
        WHEN '$25-50' THEN 2
        WHEN '$50-100' THEN 3
        WHEN '$100-200' THEN 4
        ELSE 5
    END;


-- 8. Product Return Rate Analysis (if we had returns data)
-- Simulated with cancelled orders
SELECT
    p.product_id,
    p.name AS product_name,
    p.category,
    COUNT(CASE WHEN o.status = 'completed' THEN 1 END) AS completed_orders,
    COUNT(CASE WHEN o.status = 'cancelled' THEN 1 END) AS cancelled_orders,
    ROUND(
        COUNT(CASE WHEN o.status = 'cancelled' THEN 1 END) * 100.0 /
        NULLIF(COUNT(*), 0),
        2
    ) AS cancellation_rate
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY p.product_id, p.name, p.category
HAVING COUNT(*) >= 10
ORDER BY cancellation_rate DESC;


-- 9. New Product Performance (First 30 Days)
WITH new_products AS (
    SELECT
        p.product_id,
        p.name,
        p.category,
        p.created_at AS launch_date,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price) AS revenue,
        COUNT(DISTINCT o.order_id) AS orders
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
        AND o.status = 'completed'
        AND o.order_date BETWEEN p.created_at AND date(p.created_at, '+30 days')
    GROUP BY p.product_id, p.name, p.category, p.created_at
)
SELECT
    product_id,
    name,
    category,
    launch_date,
    units_sold,
    revenue,
    orders,
    RANK() OVER (ORDER BY revenue DESC) AS launch_performance_rank
FROM new_products
ORDER BY launch_date DESC, revenue DESC;


-- 10. Product Revenue Contribution (ABC Analysis)
WITH product_revenue AS (
    SELECT
        p.product_id,
        p.name,
        p.category,
        SUM(oi.quantity * oi.unit_price) AS revenue,
        SUM(SUM(oi.quantity * oi.unit_price)) OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS cumulative_revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed'
    GROUP BY p.product_id, p.name, p.category
),
total_revenue AS (
    SELECT SUM(revenue) AS total FROM product_revenue
)
SELECT
    pr.product_id,
    pr.name,
    pr.category,
    pr.revenue,
    ROUND(pr.cumulative_revenue * 100.0 / tr.total, 2) AS cumulative_pct,
    CASE
        WHEN pr.cumulative_revenue * 100.0 / tr.total <= 80 THEN 'A - High Value'
        WHEN pr.cumulative_revenue * 100.0 / tr.total <= 95 THEN 'B - Medium Value'
        ELSE 'C - Low Value'
    END AS abc_class
FROM product_revenue pr
CROSS JOIN total_revenue tr
ORDER BY pr.revenue DESC;
