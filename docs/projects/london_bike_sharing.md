<div align="center">

# London Bike Sharing Analysis

### Urban Mobility Patterns & Demand Forecasting

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Tableau](https://img.shields.io/badge/Tableau-E97627?style=for-the-badge&logo=tableau&logoColor=white)](https://tableau.com)
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org)

</div>

---

## Executive Summary

Comprehensive analysis of London's bike-sharing system to uncover **usage patterns, seasonal trends, and demand drivers**. The project combines Python-based data processing with Tableau visualization to provide actionable insights for urban mobility optimization.

---

## Business Context

Urban bike-sharing systems are critical for:
- Reducing traffic congestion
- Promoting sustainable transportation
- Providing first/last mile connectivity
- Supporting public health initiatives

Understanding usage patterns enables better:
- Resource allocation
- Station placement decisions
- Maintenance scheduling
- Demand forecasting

---

## Analysis Objectives

1. **Pattern Recognition:** Identify daily, weekly, and seasonal usage patterns
2. **Demand Drivers:** Understand factors affecting bike-sharing demand
3. **Weather Impact:** Analyze correlation between weather and ridership
4. **Peak Analysis:** Identify high-demand periods and locations
5. **Trend Forecasting:** Project future demand based on historical patterns

---

## Technical Implementation

### Data Pipeline

```
Raw Data (Multiple Sources)
        │
        ▼
    Data Merging (Python)
        │
        ▼
   Data Cleaning & Transformation
        │
        ▼
   Feature Engineering
        │
        ▼
   Cleaned Dataset (CSV/Excel)
        │
        ▼
   Tableau Visualization
        │
        ▼
   Interactive Dashboard
```

### Technologies Used

| Component | Technology |
|-----------|------------|
| Data Processing | Python, Pandas |
| Development | Jupyter Notebook |
| Data Storage | CSV, Excel, Hyper |
| Visualization | Tableau |

---

## Key Analysis Dimensions

### Temporal Analysis
- **Hourly Patterns:** Peak commute hours vs off-peak
- **Daily Trends:** Weekday vs weekend usage
- **Seasonal Variation:** Impact of seasons on ridership
- **Year-over-Year:** Growth trends and anomalies

### Weather Correlation
- Temperature impact on ridership
- Rain/precipitation effects
- Wind speed influence
- Seasonal weather patterns

### Geographic Patterns
- High-demand stations
- Route popularity
- Area-wise distribution
- Connectivity analysis

---

## Data Processing Steps

### 1. Data Collection
```python
import pandas as pd

# Load multiple data sources
bike_data = pd.read_csv('london_bikes.csv')
weather_data = pd.read_csv('weather_data.csv')
```

### 2. Data Cleaning
```python
# Handle missing values
df = df.dropna(subset=['critical_columns'])
df['column'] = df['column'].fillna(df['column'].median())

# Remove outliers
df = df[df['rides'] < df['rides'].quantile(0.99)]
```

### 3. Feature Engineering
```python
# Extract temporal features
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek
df['month'] = df['timestamp'].dt.month
df['is_weekend'] = df['day_of_week'].isin([5, 6])
```

### 4. Data Export
```python
# Export cleaned data for visualization
df.to_csv('london_bikes_cleaned.csv', index=False)
df.to_excel('london_bikes_cleaned.xlsx', index=False)
```

---

## Key Findings

### Usage Patterns

| Pattern | Insight |
|---------|---------|
| **Morning Peak** | 7-9 AM (commute to work) |
| **Evening Peak** | 5-7 PM (commute from work) |
| **Weekend Pattern** | Later start, leisure-focused |
| **Seasonal High** | Summer months (May-August) |
| **Seasonal Low** | Winter months (December-February) |

### Weather Impact

- **Temperature:** Strong positive correlation with ridership
- **Rain:** Significant negative impact (30-50% reduction)
- **Wind:** Moderate negative impact above threshold
- **Optimal Conditions:** 15-25°C, no rain, light wind

### Demand Insights

- Weekday usage driven by commuters
- Weekend usage driven by leisure/tourism
- Holiday periods show unique patterns
- Weather sensitivity varies by user segment

---

## Dashboard Features

### Interactive Visualizations
- **Heatmap:** Hour vs Day usage intensity
- **Time Series:** Trend lines with seasonality
- **Weather Correlation:** Scatter plots with regression
- **Geographic Map:** Station-level demand

### Filters & Controls
- Date range selector
- Weather condition filter
- Day type (weekday/weekend)
- Hour range slider

---

## Project Structure

```
london_bike_sharing/
├── README.md
├── notebooks/
│   └── london_bikes_analysis.ipynb
├── data/
│   ├── raw/
│   │   └── london_merged.csv
│   └── processed/
│       ├── london_bikes_cleaned.csv
│       └── london_bikes_cleaned.xlsx
├── tableau/
│   ├── london_bikes.twb
│   └── london_bikes.hyper
└── outputs/
    └── visualizations/
```

---

## Installation & Usage

### Prerequisites
```bash
pip install pandas numpy jupyter openpyxl
```

### Run Analysis
```bash
# Clone repository
git clone https://github.com/varun-TR/london_bike_sharing.git
cd london_bike_sharing

# Launch Jupyter
jupyter notebook notebooks/london_bikes_analysis.ipynb
```

---

## Skills Demonstrated

- **Data Engineering:** ETL pipeline development
- **Python Programming:** Pandas, data manipulation
- **Statistical Analysis:** Correlation, trend analysis
- **Time Series Analysis:** Temporal pattern recognition
- **Data Visualization:** Tableau dashboard development
- **Urban Analytics:** Mobility pattern analysis
- **Feature Engineering:** Creating derived variables

---

## Business Applications

This analysis methodology can be applied to:
- Bike fleet optimization
- Station capacity planning
- Dynamic pricing strategies
- Maintenance scheduling
- Marketing campaign timing
- Infrastructure investment decisions

---

## Future Enhancements

- Machine learning demand forecasting
- Real-time dashboard integration
- Predictive maintenance modeling
- Route optimization analysis

---

<div align="center">

**Part of [Data Analysis Portfolio](../README.md)**

</div>
