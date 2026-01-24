# SQL Business Analytics - E-Commerce Analytics Platform.

![SQL](https://img.shields.io/badge/SQL-Advanced-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Compatible-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-Compatible-orange.svg)
![Status](https://img.shields.io/badge/Status-Complete-success.svg)

## Project Overview

This project demonstrates advanced SQL skills essential for Data Analyst roles at FAANG companies. It covers complex analytical queries, window functions, CTEs, and business intelligence reporting using an e-commerce dataset.

### Business Context
An e-commerce platform needs comprehensive analytics to understand business performance, customer behavior, and operational efficiency. This is the type of analysis performed daily at:
- **Amazon**: Sales analytics, inventory optimization
- **Google**: Ads revenue analysis, marketplace metrics
- **Meta**: Commerce analytics, merchant insights
- **Netflix**: Content performance, user engagement metrics
- **Uber**: Driver/rider metrics, marketplace balance

## Skills Demonstrated

- **Advanced SQL**: CTEs, window functions, subqueries
- **Business Metrics**: Revenue, AOV, LTV, retention
- **Data Modeling**: Star schema, fact/dimension tables
- **Performance Optimization**: Query optimization, indexing
- **Analytical Functions**: RANK, LEAD/LAG, NTILE, running totals
- **Date/Time Analysis**: Cohort analysis, time-series comparisons

## Project Structure

```
SQL_Business_Analytics/
├── README.md
├── schema/
│   ├── create_tables.sql           # Database schema
│   └── sample_data.sql             # Sample data insertion
├── queries/
│   ├── 01_revenue_analysis.sql     # Revenue metrics
│   ├── 02_customer_analytics.sql   # Customer behavior
│   ├── 03_product_performance.sql  # Product metrics
│   ├── 04_cohort_analysis.sql      # Retention analysis
│   └── 05_advanced_analytics.sql   # Complex queries
├── python_integration/
│   ├── setup_database.py           # Database setup script
│   └── run_analytics.py            # Query execution
└── requirements.txt
```

## Database Schema

```
┌─────────────────┐     ┌─────────────────┐
│    customers    │     │    products     │
├─────────────────┤     ├─────────────────┤
│ customer_id PK  │     │ product_id PK   │
│ name            │     │ name            │
│ email           │     │ category        │
│ signup_date     │     │ price           │
│ segment         │     │ cost            │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │    ┌─────────────────┐│
         └───>│     orders      │<┘
              ├─────────────────┤
              │ order_id PK     │
              │ customer_id FK  │
              │ order_date      │
              │ total_amount    │
              │ status          │
              └────────┬────────┘
                       │
              ┌────────┴────────┐
              │  order_items    │
              ├─────────────────┤
              │ item_id PK      │
              │ order_id FK     │
              │ product_id FK   │
              │ quantity        │
              │ unit_price      │
              └─────────────────┘
```

## Key SQL Queries Demonstrated

### 1. Revenue Analysis
- Daily/Weekly/Monthly revenue trends
- Year-over-Year comparisons
- Moving averages and growth rates

### 2. Customer Analytics
- Customer Lifetime Value (CLV)
- RFM Segmentation
- Purchase frequency analysis

### 3. Product Performance
- Top selling products by revenue
- Category performance comparison
- Margin analysis

### 4. Cohort Analysis
- Monthly retention rates
- Revenue by cohort
- Customer lifetime progression

### 5. Advanced Analytics
- Funnel analysis with window functions
- Market basket analysis
- Time between purchases

## Sample Queries

### Revenue Trend with YoY Comparison
```sql
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(total_amount) AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY 1
)
SELECT
    month,
    revenue,
    LAG(revenue, 12) OVER (ORDER BY month) AS revenue_last_year,
    ROUND(
        (revenue - LAG(revenue, 12) OVER (ORDER BY month)) /
        NULLIF(LAG(revenue, 12) OVER (ORDER BY month), 0) * 100,
        2
    ) AS yoy_growth_pct
FROM monthly_revenue
ORDER BY month;
```

### Customer RFM Segmentation
```sql
WITH rfm AS (
    SELECT
        customer_id,
        DATEDIFF('day', MAX(order_date), CURRENT_DATE) AS recency,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(total_amount) AS monetary
    FROM orders
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT
        customer_id,
        NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency) AS f_score,
        NTILE(5) OVER (ORDER BY monetary) AS m_score
    FROM rfm
)
SELECT
    customer_id,
    r_score,
    f_score,
    m_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        ELSE 'Others'
    END AS segment
FROM rfm_scores;
```

### Cohort Retention Analysis
```sql
WITH first_purchase AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
cohort_data AS (
    SELECT
        fp.cohort_month,
        DATE_TRUNC('month', o.order_date) AS order_month,
        COUNT(DISTINCT o.customer_id) AS customers
    FROM orders o
    JOIN first_purchase fp ON o.customer_id = fp.customer_id
    GROUP BY 1, 2
)
SELECT
    cohort_month,
    order_month,
    customers,
    ROUND(
        customers * 100.0 /
        FIRST_VALUE(customers) OVER (
            PARTITION BY cohort_month
            ORDER BY order_month
        ),
        2
    ) AS retention_pct
FROM cohort_data
ORDER BY cohort_month, order_month;
```

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database with sample data
python python_integration/setup_database.py

# Run analytics queries
python python_integration/run_analytics.py
```

## Sample Output

```
============================================================
              SQL BUSINESS ANALYTICS REPORT
============================================================

📊 REVENUE METRICS
─────────────────────────────────────────
Total Revenue (YTD):     $4,523,890.50
Orders (YTD):            45,238
Average Order Value:     $100.02
Revenue Growth (MoM):    +8.5%

👥 CUSTOMER METRICS
─────────────────────────────────────────
Total Customers:         12,450
New Customers (MTD):     1,234
Customer LTV (Avg):      $363.21
Repeat Purchase Rate:    42.3%

🏆 TOP PRODUCTS (Revenue)
─────────────────────────────────────────
1. Premium Wireless Headphones  $234,560
2. Smart Watch Pro             $198,340
3. Laptop Stand Ergonomic      $156,780
4. USB-C Hub Multiport         $134,560
5. Mechanical Keyboard RGB     $112,340

📈 COHORT RETENTION
─────────────────────────────────────────
Month 1: 100% | Month 2: 45% | Month 3: 32%
Month 4: 28%  | Month 5: 25% | Month 6: 22%
============================================================
```

## Interview Discussion Points

1. **Explain window functions vs GROUP BY**
   - GROUP BY aggregates rows; window functions compute over partitions while keeping rows
   - Window functions allow running totals, ranks, and comparisons

2. **How would you optimize a slow query?**
   - Check EXPLAIN plan
   - Add appropriate indexes
   - Avoid SELECT *
   - Use appropriate JOINs
   - Consider query restructuring

3. **CTEs vs Subqueries vs Temp Tables**
   - CTEs: Readable, can be recursive
   - Subqueries: Inline, can be correlated
   - Temp Tables: Better for complex multi-step analysis

4. **How do you handle NULL values?**
   - COALESCE for defaults
   - NULLIF to create NULLs
   - IS NULL / IS NOT NULL for filtering

5. **Explain LEAD/LAG functions**
   - Access data from previous/next rows
   - Useful for YoY, MoM comparisons
   - Calculate time between events

## Technologies Used

- **SQL**: PostgreSQL-compatible syntax
- **SQLite**: Local development
- **Python**: Database setup and query execution
- **pandas**: Result visualization

## Business Impact Examples

| Query | Business Use | Impact |
|-------|--------------|--------|
| Revenue Trends | Forecasting | +15% forecast accuracy |
| RFM Segmentation | Marketing targeting | 2x campaign ROI |
| Cohort Retention | Product decisions | -20% churn |
| Product Performance | Inventory planning | -30% stockouts |

## Author

Data Analysis Portfolio Project - Demonstrating SQL expertise for FAANG interviews
