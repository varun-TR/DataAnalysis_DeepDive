<div align="center">

# Customer & Market Performance Dashboard

### Enterprise Business Intelligence with Star Schema Architecture

[![Excel](https://img.shields.io/badge/Excel-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)](https://microsoft.com/excel)
[![DAX](https://img.shields.io/badge/DAX-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://docs.microsoft.com/dax)
[![Power Query](https://img.shields.io/badge/Power_Query-5C2D91?style=for-the-badge&logo=microsoft&logoColor=white)](https://powerquery.microsoft.com)

</div>

---

## Executive Summary

Architected a **comprehensive business intelligence solution** using Excel's advanced analytics capabilities. The project implements a star-schema data warehouse model to enable multi-dimensional analysis of customer behavior, market performance, and sales KPIs through interactive dashboards.

---

## Technical Highlights

| Component | Implementation |
|-----------|----------------|
| **Data Model** | Star Schema (Dimensions + Facts) |
| **ETL Engine** | Power Query |
| **Calculations** | DAX Measures |
| **Analysis** | Pivot Tables |
| **Visualization** | Excel Dashboards |

---

## Business Problem

Organizations need to:
- Track customer performance metrics over time
- Analyze market penetration and growth
- Monitor key performance indicators (KPIs)
- Enable self-service analytics for business users
- Maintain single source of truth for reporting

---

## Solution Architecture

### Star Schema Design

```
                        ┌─────────────────────┐
                        │   fact_monthly_     │
                        │   sales             │
                        │   ────────────      │
                        │   • customer_id     │
                        │   • market_id       │
                        │   • product_id      │
                        │   • date_id         │
                        │   • quantity        │
                        │   • revenue         │
                        └──────────┬──────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│ dim_customers │         │  dim_markets  │         │ dim_products  │
│ ────────────  │         │ ────────────  │         │ ────────────  │
│ • customer_id │         │ • market_id   │         │ • product_id  │
│ • name        │         │ • region      │         │ • name        │
│ • segment     │         │ • country     │         │ • category    │
│ • tier        │         │ • zone        │         │ • sub_category│
└───────────────┘         └───────────────┘         └───────────────┘
```

### Data Flow

```
Source Data (CSV/Excel)
        │
        ▼
   Power Query ETL
   • Data cleaning
   • Transformations
   • Type conversions
        │
        ▼
   Data Model
   • Relationships
   • Star schema
        │
        ▼
   DAX Calculations
   • Measures
   • KPIs
        │
        ▼
   Pivot Tables & Dashboard
```

---

## Dimension Tables

### dim_customers
| Column | Description |
|--------|-------------|
| customer_id | Unique identifier |
| customer_name | Company name |
| customer_segment | B2B, B2C, Enterprise |
| customer_tier | Gold, Silver, Bronze |
| acquisition_date | Customer since |

### dim_markets
| Column | Description |
|--------|-------------|
| market_id | Unique identifier |
| market_name | Geographic market |
| region | Regional grouping |
| country | Country name |
| zone | Sales zone |

### dim_products
| Column | Description |
|--------|-------------|
| product_id | Unique identifier |
| product_name | Product title |
| category | Product category |
| sub_category | Product subcategory |
| unit_price | Standard price |

---

## Fact Table

### fact_monthly_sales
| Column | Description |
|--------|-------------|
| transaction_id | Unique identifier |
| customer_id | FK to customers |
| market_id | FK to markets |
| product_id | FK to products |
| date | Transaction date |
| quantity | Units sold |
| revenue | Sales amount |
| cost | Product cost |

---

## DAX Measures

### Revenue Metrics
```dax
Total Revenue = SUM(fact_monthly_sales[revenue])

Revenue YoY Growth =
DIVIDE(
    [Total Revenue] - CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('dim_date'[date])),
    CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('dim_date'[date]))
)

Revenue MTD = TOTALMTD([Total Revenue], 'dim_date'[date])
```

### Customer Metrics
```dax
Total Customers = DISTINCTCOUNT(fact_monthly_sales[customer_id])

New Customers =
CALCULATE(
    [Total Customers],
    FILTER(dim_customers, dim_customers[acquisition_date] >= [Period Start])
)

Customer Retention Rate =
DIVIDE(
    [Returning Customers],
    CALCULATE([Total Customers], PREVIOUSMONTH('dim_date'[date]))
)
```

### Performance Metrics
```dax
Avg Order Value = DIVIDE([Total Revenue], [Total Orders])

Revenue Per Customer = DIVIDE([Total Revenue], [Total Customers])

Market Share = DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL(dim_markets)))
```

---

## Dashboard Components

### KPI Summary Panel
- Total Revenue (with YoY comparison)
- Customer Count (with trend)
- Average Order Value
- Market Coverage

### Customer Performance
- **Segment Analysis:** Revenue by customer segment
- **Tier Distribution:** Customer tier breakdown
- **Top Customers:** Ranked by revenue/volume
- **Retention Metrics:** Churn and retention rates

### Market Performance
- **Regional Heatmap:** Performance by region
- **Market Comparison:** Side-by-side analysis
- **Growth Matrix:** Market growth vs share
- **Zone Performance:** Sales zone metrics

### Product Analysis
- **Category Mix:** Revenue by category
- **Top Products:** Best sellers
- **Cross-sell Matrix:** Product affinity
- **Price Analysis:** Margin by product

---

## Power Query Transformations

### Data Cleaning Steps
```powerquery
// Remove duplicates
= Table.Distinct(Source, {"transaction_id"})

// Handle null values
= Table.ReplaceValue(#"Previous Step", null, 0, Replacer.ReplaceValue, {"quantity"})

// Data type conversion
= Table.TransformColumnTypes(#"Previous Step", {{"date", type date}, {"revenue", Currency.Type}})

// Add calculated columns
= Table.AddColumn(#"Previous Step", "fiscal_quarter", each Date.QuarterOfYear([date]))
```

---

## Project Structure

```
customer-market_performance_report/
├── README.md
├── data/
│   ├── dim_customers.csv
│   ├── dim_markets.csv
│   ├── dim_products.csv
│   └── fact_monthly_sales.csv
├── workbooks/
│   ├── data_model.xlsx
│   └── dashboard.xlsx
└── documentation/
    ├── data_dictionary.md
    └── dax_measures.md
```

---

## Skills Demonstrated

- **Data Warehouse Design:** Star schema architecture
- **ETL Development:** Power Query transformations
- **DAX Formulas:** Complex calculations and measures
- **Data Modeling:** Relationships and hierarchies
- **Dashboard Design:** Interactive Excel dashboards
- **KPI Development:** Business metric definition
- **Self-Service BI:** User-friendly analytics tools

---

## Business Value

### Before Implementation
- Manual report generation
- Inconsistent metrics
- Time-consuming analysis
- Limited drill-down capability

### After Implementation
- Automated reporting
- Single source of truth
- Real-time KPI tracking
- Self-service analytics
- Multi-dimensional analysis

---

## Best Practices Applied

1. **Star Schema:** Optimized for analytical queries
2. **Dimension Tables:** Descriptive attributes separated
3. **Fact Table:** Transactional data centralized
4. **DAX Measures:** Reusable calculations
5. **Power Query:** Repeatable ETL process
6. **Data Validation:** Quality checks implemented

---

<div align="center">

**Part of [Data Analysis Portfolio](../README.md)**

</div>
