<div align="center">

# Atliq Sales Intelligence Platform

### End-to-End Business Intelligence Solution

[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![Tableau](https://img.shields.io/badge/Tableau-E97627?style=for-the-badge&logo=tableau&logoColor=white)](https://tableau.com)
[![SQL](https://img.shields.io/badge/SQL-Analytics-blue?style=for-the-badge)](https://mysql.com)

</div>

---

## Executive Summary

Built a comprehensive sales analytics platform for Atliq, processing **$118M+ in revenue data** across multiple market segments. The solution combines SQL-based data analysis with interactive Tableau visualizations to enable data-driven decision making.

---

## Business Impact

| Metric | Value |
|--------|-------|
| **Total Revenue Analyzed** | $118,405.20K |
| **Sales Volume** | 141,310 units |
| **Markets Covered** | Multiple geographic regions |
| **Analysis Depth** | Revenue, quantity, trends, markets |

---

## Live Dashboard

**[View Interactive Dashboard on Tableau Public](https://public.tableau.com/app/profile/varun.t.r./viz/Dashboard1_17187019071190/Dashboard1)**

---

## Problem Statement

Atliq's sales team needed:
- Centralized view of revenue performance across markets
- Historical trend analysis for forecasting
- Sales quantity tracking and analysis
- Market-wise performance comparison

---

## Solution Architecture

### Database Schema

```
                    ┌─────────────────┐
                    │   transactions  │
                    │   (Fact Table)  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   customers   │   │   markets     │   │   products    │
│  (Dimension)  │   │  (Dimension)  │   │  (Dimension)  │
└───────────────┘   └───────────────┘   └───────────────┘
                             │
                             ▼
                    ┌───────────────┐
                    │     date      │
                    │  (Dimension)  │
                    └───────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| Database | MySQL |
| Data Analysis | SQL |
| Visualization | Tableau |
| Data Model | Star Schema |

---

## Key Analysis Questions Answered

### 1. Revenue by Market
```sql
-- Breakdown of revenue generated from each geographic market
SELECT market, SUM(sales_amount) as total_revenue
FROM transactions
GROUP BY market
ORDER BY total_revenue DESC;
```

### 2. Total Revenue Calculation
```sql
-- Aggregated revenue across all transactions
SELECT SUM(sales_amount) as total_revenue
FROM transactions;
-- Result: $118,405.20K
```

### 3. Sales Quantity Analysis
```sql
-- Total units sold across all markets
SELECT SUM(sales_qty) as total_quantity
FROM transactions;
-- Result: 141,310 units
```

### 4. Revenue Trend by Year
```sql
-- Year-over-year revenue analysis
SELECT YEAR(order_date), SUM(sales_amount)
FROM transactions
GROUP BY YEAR(order_date)
ORDER BY 1;
```

---

## Dashboard Features

### KPI Summary Cards
- Total Revenue
- Total Sales Quantity
- Number of Customers
- Number of Products

### Visualizations
- **Revenue by Market:** Bar chart showing market performance
- **Revenue Trend:** Line chart showing temporal patterns
- **Top Customers:** Ranked list of highest-value customers
- **Product Performance:** Analysis of best-selling products

### Interactive Filters
- Date range selector
- Market filter
- Customer segment filter
- Product category filter

---

## Installation & Setup

### Prerequisites
- MySQL Server 8.0+
- Tableau Desktop or Tableau Public
- Git

### Steps

1. **Clone Repository**
```bash
git clone https://github.com/varun-TR/Atliq_sales_insights.git
cd Atliq_sales_insights
```

2. **Database Setup**
```bash
# Import the database
mysql -u root -p < db_dump.sql

# Or restore from backup
mysql -u root -p atliq_sales < backup.sql
```

3. **Run Analysis Queries**
```bash
# Execute SQL analysis
mysql -u root -p atliq_sales < Analysis.sql
```

4. **Connect Tableau**
- Open Tableau Desktop
- Connect to MySQL database
- Import the workbook or create new visualizations

---

## Project Structure

```
Atliq_sales_insights/
├── README.md
├── Analysis.sql          # SQL analysis queries
├── data/
│   ├── customers.csv
│   ├── markets.csv
│   ├── products.csv
│   └── transactions.csv
├── sql/
│   └── schema.sql        # Database schema
└── tableau/
    └── dashboard.twb     # Tableau workbook
```

---

## Skills Demonstrated

- **Database Design:** Star schema implementation
- **SQL Analytics:** Complex queries for business insights
- **Data Modeling:** Dimension and fact table design
- **ETL Process:** Data extraction and transformation
- **Dashboard Development:** Interactive Tableau visualizations
- **Business Intelligence:** Revenue analysis and forecasting

---

## Results & Insights

### Key Findings

1. **Market Concentration:** Top 3 markets contribute to 60%+ of revenue
2. **Seasonal Patterns:** Identified quarterly sales cycles
3. **Customer Segmentation:** High-value customers account for significant revenue share
4. **Product Mix:** Core products drive majority of sales volume

### Business Recommendations

- Focus resources on high-performing markets
- Develop retention strategies for top customers
- Optimize inventory for best-selling products
- Plan for seasonal demand variations

---

## Credits

Dataset sourced from [Code Basics](https://codebasics.io/resources/end-to-end-sales-insights-project-using-tableau)

---

## License

This project is open source and available for educational purposes.

---

<div align="center">

**Part of [Data Analysis Portfolio](../README.md)**

</div>
