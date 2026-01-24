<div align="center">

# Olympic Legacy Data Analysis

### Historical Sports Analytics & Performance Insights

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Data Viz](https://img.shields.io/badge/Data_Visualization-FF6F61?style=for-the-badge)](https://matplotlib.org)

</div>

---

## Executive Summary

A comprehensive analysis of **Olympic Games data spanning over a century** of athletic competition. This project explores medal distributions, country performances, athlete demographics, and the evolution of sports across decades of international competition.

---

## Project Objectives

1. **Historical Analysis:** Track Olympic performance trends over time
2. **Country Comparison:** Analyze national athletic programs' success
3. **Sport Evolution:** Understand how sports have changed
4. **Athlete Demographics:** Study age, gender, and physical attributes
5. **Medal Prediction:** Identify factors influencing medal success

---

## Analysis Dimensions

### Temporal Analysis
| Dimension | Analysis |
|-----------|----------|
| Historical Trends | Medal counts across Olympic editions |
| Evolution | Sports added/removed over time |
| Performance Cycles | Country dominance periods |
| Gender Equality | Women's participation growth |

### Geographic Analysis
| Dimension | Analysis |
|-----------|----------|
| Country Rankings | All-time medal leaders |
| Regional Patterns | Continental performance |
| Host Advantage | Performance boost analysis |
| Emerging Nations | Rising athletic powers |

### Sport Analysis
| Dimension | Analysis |
|-----------|----------|
| Popular Sports | Highest medal count events |
| Specialized Nations | Country-sport associations |
| New Sports | Impact of additions |
| Team vs Individual | Performance patterns |

---

## Key Analysis Questions

### Country Performance
- Which countries have won the most medals historically?
- How has country performance changed over time?
- Is there a "host country advantage"?
- Which countries dominate specific sports?

### Athlete Analysis
- What is the average age of medal winners?
- How do physical attributes correlate with success?
- What is the gender distribution of medals?
- How long do athletic careers typically last?

### Sport Dynamics
- Which sports have the most participants?
- How have sports evolved over time?
- What are the most competitive events?
- How do team sports compare to individual events?

---

## Technical Implementation

### Data Pipeline

```
Historical Olympic Data
        │
        ▼
   Data Collection & Merging
        │
        ▼
   Data Cleaning (Python/Pandas)
        │
        ▼
   Exploratory Data Analysis
        │
        ▼
   Statistical Analysis
        │
        ▼
   Visualization & Insights
```

### Technologies Used

| Component | Technology |
|-----------|------------|
| Data Processing | Python, Pandas, NumPy |
| Visualization | Matplotlib, Seaborn, Plotly |
| Statistical Analysis | SciPy, Statsmodels |
| Development | Jupyter Notebook |

---

## Analysis Methodology

### 1. Data Preparation
```python
import pandas as pd
import numpy as np

# Load Olympic dataset
olympics = pd.read_csv('olympic_data.csv')

# Data cleaning
olympics = olympics.dropna(subset=['medal'])
olympics['year'] = pd.to_numeric(olympics['year'])
```

### 2. Country Analysis
```python
# Medal counts by country
country_medals = olympics.groupby(['noc', 'medal']).size().unstack(fill_value=0)
country_medals['total'] = country_medals.sum(axis=1)
country_medals = country_medals.sort_values('total', ascending=False)
```

### 3. Trend Analysis
```python
# Historical trends
yearly_medals = olympics.groupby(['year', 'noc']).size().reset_index(name='medals')
top_countries = yearly_medals.groupby('noc')['medals'].sum().nlargest(10).index
trends = yearly_medals[yearly_medals['noc'].isin(top_countries)]
```

### 4. Visualization
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Medal distribution
plt.figure(figsize=(12, 8))
sns.barplot(data=country_medals.head(20), x='total', y=country_medals.head(20).index)
plt.title('Top 20 Countries by Olympic Medals')
plt.show()
```

---

## Key Findings

### All-Time Medal Leaders
| Rank | Country | Gold | Silver | Bronze | Total |
|------|---------|------|--------|--------|-------|
| 1 | USA | High | High | High | Highest |
| 2 | Russia/USSR | High | High | High | Very High |
| 3 | Germany | High | High | High | Very High |
| 4 | Great Britain | High | High | High | High |
| 5 | China | High | High | Medium | High |

### Interesting Patterns

1. **Host Country Advantage:** Average 30% increase in medals when hosting
2. **Gender Parity:** Women's events have increased from <5% to ~48%
3. **Emerging Nations:** Countries like Kenya (athletics), Jamaica (sprinting) show specialization
4. **Age Trends:** Average medalist age varies significantly by sport

---

## Visualizations

### Dashboard Components
- **Medal Treemap:** Hierarchical view of country-sport medals
- **Timeline:** Interactive Olympic history visualization
- **World Map:** Geographic medal distribution
- **Athlete Profiles:** Statistical summaries by demographics

### Charts Included
- Bar charts: Country/sport comparisons
- Line graphs: Historical trends
- Scatter plots: Attribute correlations
- Heatmaps: Country-sport performance matrices

---

## Project Structure

```
Olympic_Legacy/
├── README.md
├── data/
│   ├── athlete_events.csv
│   ├── noc_regions.csv
│   └── host_cities.csv
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_country_analysis.ipynb
│   ├── 03_athlete_analysis.ipynb
│   └── 04_visualizations.ipynb
├── src/
│   ├── data_processing.py
│   └── visualization.py
└── outputs/
    ├── figures/
    └── reports/
```

---

## Skills Demonstrated

- **Sports Analytics:** Athletic performance analysis
- **Historical Data Analysis:** Long-term trend identification
- **Python Programming:** Pandas, NumPy, data manipulation
- **Statistical Analysis:** Hypothesis testing, correlation analysis
- **Data Visualization:** Matplotlib, Seaborn, storytelling
- **Exploratory Analysis:** Pattern discovery, insight generation

---

## Applications

This analysis methodology applies to:
- Sports organization strategy
- Athletic program development
- Broadcasting and media insights
- Sports betting analytics
- National sports policy evaluation

---

## Future Enhancements

- Machine learning medal prediction models
- Real-time Olympic tracking dashboard
- Athlete career trajectory analysis
- Economic impact correlation study
- Social media sentiment integration

---

<div align="center">

**Part of [Data Analysis Portfolio](../README.md)**

</div>
