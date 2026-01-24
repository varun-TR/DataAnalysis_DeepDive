<div align="center">

# Telangana State Government Revenue Analysis

### Data-Driven Insights for Policy Optimization

[![Tableau](https://img.shields.io/badge/Tableau-E97627?style=for-the-badge&logo=tableau&logoColor=white)](https://tableau.com)
[![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![Government Data](https://img.shields.io/badge/Open_Data-Government-green?style=for-the-badge)](https://data.telangana.gov.in)

</div>

---

## Executive Summary

This project analyzes revenue patterns from **document registrations and e-stamp challans** across all 33 districts of Telangana State, utilizing official government open data. The analysis provides actionable insights for revenue optimization and policy recommendations for improving e-stamp adoption rates.

---

## Business Problem

The Telangana State government needed to:
- Understand revenue distribution across districts
- Identify top and underperforming regions
- Analyze the adoption rate of e-stamp services vs traditional document registration
- Develop strategies to increase e-stamp challan usage

---

## Key Findings

### Top Revenue-Generating Districts (FY 2019-2022)

| Rank | District | Revenue Category |
|------|----------|-----------------|
| 1 | Rangareddy | High |
| 2 | Medchal-Malkajgiri | High |
| 3 | Hyderabad | High |
| 4 | Sangareddy | Medium-High |
| 5 | Hanumakonda | Medium-High |

### Revenue Channel Analysis

- **Document Registration:** Traditional revenue stream with consistent performance
- **E-Stamp Challans:** Growing adoption with significant regional variations
- **Insight:** Districts near urban centers show higher e-stamp adoption rates

---

## Technical Implementation

### Data Pipeline

```
Data Source (Government Portal)
        │
        ▼
    Data Extraction
        │
        ▼
   Data Cleaning & Transformation (SQL)
        │
        ▼
   Tableau Data Connection
        │
        ▼
   Interactive Dashboard
```

### Technologies Used

| Component | Technology |
|-----------|------------|
| Data Source | Telangana Open Data Portal |
| Analysis | SQL Queries |
| Visualization | Tableau Desktop |
| Dashboard | Tableau Public |

---

## Analysis Dimensions

### Temporal Analysis
- **Time Period:** FY 2019-2022
- **Granularity:** Monthly, Quarterly, Annual trends
- **Patterns:** Seasonal variations, year-over-year growth

### Geographic Analysis
- **Coverage:** All 33 districts of Telangana
- **Segmentation:** Urban vs Rural districts
- **Clustering:** Revenue-based district classification

### Channel Analysis
- Document Registration Revenue
- E-Stamp Challan Revenue
- Channel migration patterns

---

## Dashboard Features

The interactive Tableau dashboard provides:

- **Geographic Heat Map:** Revenue intensity across districts
- **Trend Lines:** Revenue progression over time
- **Comparative Analysis:** Document vs E-Stamp revenue
- **Filters:** Dynamic filtering by district, time period, and revenue type
- **KPI Cards:** Key metrics at a glance

---

## Strategic Recommendations

Based on the analysis, the following policy recommendations were developed:

1. **E-Stamp Promotion Campaigns**
   - Target low-adoption districts with awareness programs
   - Incentivize digital payment methods

2. **Infrastructure Investment**
   - Improve digital infrastructure in rural districts
   - Establish more e-stamp facilitation centers

3. **Performance Monitoring**
   - Implement district-wise KPI tracking
   - Monthly review of adoption metrics

4. **Best Practice Sharing**
   - Document success factors from top-performing districts
   - Replicate strategies in underperforming regions

---

## Skills Demonstrated

- Government/Public Sector Data Analysis
- Revenue Forecasting & Trend Analysis
- Geographic Data Visualization
- Policy Impact Assessment
- Executive Dashboard Development
- Data-Driven Decision Making

---

## Data Source

**Official Source:** [Telangana Open Data Portal](https://data.telangana.gov.in)

*All data used in this analysis is publicly available government data released under open data initiatives.*

---

## Project Structure

```
TS_analysis/
├── README.md
├── data/
│   └── raw_data.csv
├── sql/
│   └── analysis_queries.sql
└── tableau/
    └── dashboard.twb
```

---

## View Dashboard

[View Interactive Dashboard on Tableau Public](https://public.tableau.com/app/profile/varun.t.r.)

---

<div align="center">

**Part of [Data Analysis Portfolio](../README.md)**

</div>
