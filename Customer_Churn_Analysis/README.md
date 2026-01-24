# Customer Churn Analysis & Prediction.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-green.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange.svg)
![Status](https://img.shields.io/badge/Status-Complete-success.svg)

## Project Overview

This project demonstrates customer churn analysis skills essential for Data Analyst roles at subscription-based companies. The analysis identifies key churn drivers and builds a predictive model to proactively retain at-risk customers.

### Business Context
A SaaS company wants to understand why customers are churning and predict which customers are likely to churn in the next 30 days. This analysis is critical at:
- **Netflix**: Reducing subscriber churn
- **Spotify**: Retaining premium users
- **Amazon**: Maintaining Prime membership
- **Salesforce**: Enterprise SaaS retention

## Skills Demonstrated

- **Exploratory Data Analysis (EDA)**: Understanding customer behavior patterns
- **Cohort Analysis**: Tracking customer retention over time
- **Feature Engineering**: Creating predictive features from raw data
- **Machine Learning**: Logistic regression, random forest for churn prediction
- **Statistical Analysis**: Chi-square tests, correlation analysis
- **Business Metrics**: Churn rate, CLV, retention rate
- **Data Visualization**: Matplotlib, Seaborn dashboards

## Project Structure

```
Customer_Churn_Analysis/
├── README.md
├── churn_analysis.py               # Main analysis script
├── generate_churn_data.py          # Synthetic data generation
├── churn_prediction_model.py       # ML model training
├── data/
│   └── customer_data.csv           # Customer data
├── results/
│   ├── churn_analysis_report.md
│   └── visualizations/
└── requirements.txt
```

## Key Findings

### Churn Drivers (Top 5)

| Factor | Churn Impact | Action |
|--------|--------------|--------|
| No support tickets in 30 days | +45% churn risk | Proactive outreach |
| Monthly (vs Annual) billing | +38% churn risk | Promote annual plans |
| < 3 logins in past week | +35% churn risk | Re-engagement campaign |
| No feature adoption in 14 days | +32% churn risk | Feature education |
| Payment failure | +65% churn risk | Payment recovery flow |

### Overall Metrics

| Metric | Value |
|--------|-------|
| Overall Churn Rate | 18.5% |
| Monthly Recurring Revenue at Risk | $1.2M |
| Model Accuracy | 87.3% |
| Model Precision | 82.1% |
| Model Recall | 79.5% |

## Methodology

### 1. Data Exploration
- Customer demographics and subscription details
- Usage patterns and engagement metrics
- Support interactions and satisfaction scores
- Payment history and billing issues

### 2. Feature Engineering
```python
# Key engineered features
features = [
    'days_since_last_login',
    'login_frequency_7d',
    'feature_adoption_score',
    'support_tickets_30d',
    'payment_failures_90d',
    'contract_tenure_months',
    'plan_upgrade_history',
    'nps_score'
]
```

### 3. Cohort Analysis
- Track retention by signup month
- Identify seasonal patterns
- Compare cohorts by acquisition channel

### 4. Predictive Modeling
- Logistic Regression (interpretable baseline)
- Random Forest (best performance)
- Feature importance analysis
- SHAP values for explainability

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Generate synthetic data
python generate_churn_data.py

# Run exploratory analysis
python churn_analysis.py

# Train prediction model
python churn_prediction_model.py
```

## Sample Output

```
============================================================
              CUSTOMER CHURN ANALYSIS REPORT
============================================================

OVERALL METRICS:
  Total Customers: 50,000
  Churned Customers: 9,250 (18.5%)
  Active Customers: 40,750 (81.5%)
  Monthly Revenue at Risk: $1,203,450

TOP CHURN PREDICTORS:
  1. payment_failure_flag     (Importance: 0.234)
  2. days_since_last_login    (Importance: 0.198)
  3. support_tickets_30d      (Importance: 0.156)
  4. monthly_billing_flag     (Importance: 0.143)
  5. feature_adoption_score   (Importance: 0.121)

MODEL PERFORMANCE:
  Accuracy:  87.3%
  Precision: 82.1%
  Recall:    79.5%
  F1-Score:  80.8%
  AUC-ROC:   0.912

HIGH-RISK CUSTOMERS IDENTIFIED: 2,847
  Estimated Saveable Revenue: $456,780/month
============================================================
```

## Cohort Analysis Results

```
Retention by Month After Signup:
Month 1:  95.2%
Month 2:  89.1%
Month 3:  84.7%
Month 6:  72.3%
Month 12: 58.9%
```

## Business Recommendations

### Immediate Actions
1. **Payment Recovery**: Implement dunning management for failed payments
2. **Re-engagement**: Automated email sequences for inactive users
3. **Annual Promotion**: Offer 20% discount for annual billing conversion

### Long-term Strategies
1. **Customer Health Score**: Implement real-time health monitoring
2. **Proactive Support**: Reach out before customers contact support
3. **Feature Education**: In-app tutorials for underutilized features

## Interview Discussion Points

1. **How would you handle imbalanced classes in churn prediction?**
   - SMOTE for oversampling minority class
   - Class weights in model training
   - Precision-recall tradeoff analysis

2. **What metrics would you optimize for?**
   - Recall to catch more churners (false negatives are costly)
   - Balance with precision to avoid alert fatigue

3. **How would you validate the model in production?**
   - A/B test retention interventions on predicted churners
   - Monitor lift in retention rate
   - Track false positive/negative rates over time

4. **How do you explain the model to stakeholders?**
   - Feature importance plots
   - SHAP values for individual predictions
   - Business-friendly language for technical concepts

## Technologies Used

- **Python 3.8+**
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning
- **matplotlib/seaborn**: Visualization
- **shap**: Model interpretability

## Author

Data Analysis Portfolio Project - Demonstrating churn analysis expertise for FAANG interviews
