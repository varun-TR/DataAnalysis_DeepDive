<div align="center">

# Coffee Shop Sales Intelligence

### Data-Driven Revenue Optimization

[![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![Excel](https://img.shields.io/badge/Excel-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)](https://microsoft.com/excel)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

</div>

---

## Executive Summary

Developed a comprehensive sales analytics solution for a coffee retail business, delivering **actionable insights that contributed to 10% revenue growth**. The project analyzes customer purchasing patterns, product performance, and regional market dynamics to optimize inventory management and marketing strategies.

---

## Business Impact

| Metric | Achievement |
|--------|-------------|
| **Revenue Growth** | 10% increase |
| **Inventory Optimization** | Data-driven stocking decisions |
| **Market Insights** | Regional performance clarity |
| **Customer Understanding** | Purchasing pattern analysis |

---

## Business Problem

The coffee shop needed to:
- Understand customer purchasing behavior
- Optimize inventory across product types and sizes
- Identify top-performing markets and products
- Develop targeted marketing strategies
- Reduce waste and improve margins

---

## Key Findings

### Market Performance

| Market | Performance |
|--------|-------------|
| **USA** | Largest sales market |
| **Other Regions** | Growth opportunities identified |

### Product Insights

| Finding | Detail |
|---------|--------|
| **Popular Size** | 0.2 kg packages (especially Arabica) |
| **Trend Alert** | Declining Arabica, increasing Robusta demand |
| **Opportunity** | Adjust product mix based on trends |

### Customer Segmentation

- High-frequency buyers (loyalty program candidates)
- Bulk purchasers (B2B opportunities)
- Seasonal buyers (targeted campaigns)
- New customers (onboarding optimization)

---

## Technical Implementation

### Data Pipeline

```
Raw Sales Data
      │
      ▼
SQL Data Extraction & Cleaning
      │
      ▼
SQL Transformation Queries
      │
      ▼
Python Additional Processing
      │
      ▼
Excel Dashboard & Analysis
      │
      ▼
Actionable Insights
```

### Technologies Used

| Layer | Technology |
|-------|------------|
| Data Collection | SQL |
| Data Cleaning | SQL, Python |
| Transformation | SQL |
| Analysis | Excel, Python |
| Visualization | Excel Dashboards |

---

## Analysis Framework

### 1. Sales Analysis
```sql
-- Revenue by coffee type
SELECT coffee_type,
       SUM(sales_amount) as revenue,
       COUNT(*) as transactions
FROM sales
GROUP BY coffee_type
ORDER BY revenue DESC;
```

### 2. Customer Analysis
```sql
-- Customer purchase frequency
SELECT customer_id,
       COUNT(*) as purchase_count,
       SUM(sales_amount) as total_spent,
       AVG(sales_amount) as avg_order_value
FROM sales
GROUP BY customer_id
ORDER BY total_spent DESC;
```

### 3. Product Mix Analysis
```sql
-- Package size preferences by coffee type
SELECT coffee_type,
       package_size,
       COUNT(*) as units_sold
FROM sales
GROUP BY coffee_type, package_size
ORDER BY coffee_type, units_sold DESC;
```

### 4. Regional Analysis
```sql
-- Sales by region
SELECT region,
       SUM(sales_amount) as revenue,
       COUNT(DISTINCT customer_id) as customers
FROM sales
GROUP BY region
ORDER BY revenue DESC;
```

---

## Dashboard Components

### Excel Dashboard Features

#### KPI Cards
- Total Revenue
- Total Orders
- Average Order Value
- Customer Count

#### Charts & Visualizations
- **Revenue by Region:** Geographic performance
- **Product Mix:** Coffee type distribution
- **Size Analysis:** Package size preferences
- **Trend Line:** Monthly/quarterly sales trend
- **Customer Segments:** Purchasing behavior groups

#### Interactive Elements
- Date slicer
- Region filter
- Product filter
- Customer segment filter

---

## Strategic Recommendations

### Inventory Management
1. **Increase Robusta Stock:** Rising demand trend
2. **0.2kg Package Focus:** Most popular size
3. **Regional Allocation:** Prioritize USA inventory
4. **Seasonal Adjustment:** Plan for demand peaks

### Marketing Strategy
1. **USA Market:** Maintain strong presence
2. **Loyalty Program:** Target high-frequency buyers
3. **Robusta Promotion:** Capitalize on trend
4. **Bundle Offers:** Popular size combinations

### Operational Improvements
1. **Demand Forecasting:** Reduce stockouts
2. **Supplier Negotiation:** Volume-based pricing
3. **Waste Reduction:** Better inventory turnover
4. **Customer Retention:** Personalized offers

---

## Project Structure

```
coffee_shop_insights/
├── README.md
├── data/
│   ├── raw_sales_data.csv
│   └── cleaned_data.csv
├── sql/
│   ├── data_cleaning.sql
│   └── analysis_queries.sql
├── notebooks/
│   └── coffee_analysis.ipynb
└── dashboards/
    └── coffee_sales_dashboard.xlsx
```

---

## Skills Demonstrated

- **SQL Analytics:** Complex queries for business insights
- **Data Cleaning:** ETL and data quality management
- **Excel Expertise:** Advanced dashboards and analysis
- **Business Analysis:** Translating data to recommendations
- **Revenue Optimization:** Identifying growth opportunities
- **Customer Analytics:** Segmentation and behavior analysis
- **Inventory Analysis:** Stock optimization strategies

---

## Results Summary

### Before Analysis
- Ad-hoc inventory decisions
- Limited customer understanding
- Reactive marketing approach
- Undefined regional strategy

### After Implementation
- **10% Revenue Growth**
- Data-driven inventory management
- Customer segmentation model
- Targeted marketing campaigns
- Clear regional priorities

---

## Methodology

1. **Data Collection:** Gathered sales, customer, and product data
2. **Data Cleaning:** Removed duplicates, handled missing values
3. **Exploration:** Identified patterns and anomalies
4. **Analysis:** Deep dive into key business questions
5. **Visualization:** Created actionable dashboards
6. **Recommendations:** Developed strategic action items
7. **Validation:** Tracked impact of implemented changes

---

<div align="center">

**Part of [Data Analysis Portfolio](../README.md)**

</div>
