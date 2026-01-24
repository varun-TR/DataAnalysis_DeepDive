"""
Customer Churn Data Generator
Generates realistic synthetic customer data for churn analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_customer_data(n_customers=50000, seed=42):
    """
    Generate synthetic customer data for churn analysis

    Parameters:
    -----------
    n_customers : int
        Number of customers to generate
    seed : int
        Random seed for reproducibility

    Returns:
    --------
    pd.DataFrame
        DataFrame containing customer data
    """
    np.random.seed(seed)

    # Generate customer IDs
    customer_ids = [f"CUST_{i:06d}" for i in range(n_customers)]

    # Signup dates (last 24 months)
    base_date = datetime(2024, 1, 1)
    signup_dates = [
        base_date - timedelta(days=np.random.randint(1, 730))
        for _ in range(n_customers)
    ]

    # Calculate tenure in months
    tenure_months = [(base_date - d).days / 30 for d in signup_dates]

    # Subscription plans
    plan_types = ['basic', 'standard', 'premium', 'enterprise']
    plan_probs = [0.30, 0.35, 0.25, 0.10]
    plans = np.random.choice(plan_types, size=n_customers, p=plan_probs)

    # Monthly prices by plan
    plan_prices = {'basic': 9.99, 'standard': 19.99, 'premium': 49.99, 'enterprise': 99.99}
    monthly_charges = [plan_prices[p] for p in plans]

    # Billing type (monthly vs annual)
    billing_annual = np.random.binomial(1, 0.35, n_customers)

    # Contract type
    contract_types = ['month-to-month', 'one_year', 'two_year']
    contract_probs = [0.55, 0.30, 0.15]
    contracts = np.random.choice(contract_types, size=n_customers, p=contract_probs)

    # Usage metrics
    days_since_last_login = np.random.exponential(7, n_customers)
    days_since_last_login = np.clip(days_since_last_login, 0, 90)

    login_frequency_7d = np.random.poisson(4, n_customers)
    login_frequency_7d = np.clip(login_frequency_7d, 0, 30)

    # Feature adoption (0-100 score)
    feature_adoption_score = np.random.beta(2, 2, n_customers) * 100

    # Support tickets in last 30 days
    support_tickets_30d = np.random.poisson(0.5, n_customers)
    support_tickets_30d = np.clip(support_tickets_30d, 0, 10)

    # NPS Score (-100 to 100, typically -10 to 50)
    nps_scores = np.random.normal(20, 30, n_customers)
    nps_scores = np.clip(nps_scores, -100, 100)

    # Payment failures in last 90 days
    payment_failures_90d = np.random.poisson(0.2, n_customers)
    payment_failures_90d = np.clip(payment_failures_90d, 0, 5)

    # Customer demographics
    age_groups = ['18-24', '25-34', '35-44', '45-54', '55+']
    age_probs = [0.15, 0.35, 0.25, 0.15, 0.10]
    ages = np.random.choice(age_groups, size=n_customers, p=age_probs)

    # Acquisition channel
    channels = ['organic', 'paid_search', 'social', 'referral', 'direct']
    channel_probs = [0.25, 0.30, 0.20, 0.15, 0.10]
    acquisition_channels = np.random.choice(channels, size=n_customers, p=channel_probs)

    # Total lifetime spend
    total_spend = [
        monthly_charges[i] * tenure_months[i] * (0.8 + np.random.random() * 0.4)
        for i in range(n_customers)
    ]

    # Determine churn based on various factors
    churn_probabilities = []
    for i in range(n_customers):
        base_prob = 0.10  # Base 10% churn rate

        # Increase churn probability based on risk factors
        if days_since_last_login[i] > 14:
            base_prob += 0.15
        if days_since_last_login[i] > 30:
            base_prob += 0.10

        if login_frequency_7d[i] < 2:
            base_prob += 0.10

        if feature_adoption_score[i] < 30:
            base_prob += 0.12

        if payment_failures_90d[i] > 0:
            base_prob += 0.25

        if billing_annual[i] == 0:  # Monthly billing
            base_prob += 0.08

        if contracts[i] == 'month-to-month':
            base_prob += 0.10

        if nps_scores[i] < 0:  # Detractor
            base_prob += 0.15

        if support_tickets_30d[i] > 3:
            base_prob += 0.08

        # Decrease churn for loyal, engaged customers
        if tenure_months[i] > 12:
            base_prob -= 0.05
        if tenure_months[i] > 24:
            base_prob -= 0.05

        if feature_adoption_score[i] > 70:
            base_prob -= 0.08

        if plans[i] == 'enterprise':
            base_prob -= 0.10

        # Clamp probability
        base_prob = max(0.02, min(0.85, base_prob))
        churn_probabilities.append(base_prob)

    # Generate churn outcomes
    churned = [np.random.binomial(1, p) for p in churn_probabilities]

    # Churn date for churned customers
    churn_dates = []
    for i in range(n_customers):
        if churned[i] == 1:
            days_until_churn = np.random.randint(1, 90)
            churn_dates.append(base_date - timedelta(days=days_until_churn))
        else:
            churn_dates.append(None)

    # Create DataFrame
    df = pd.DataFrame({
        'customer_id': customer_ids,
        'signup_date': signup_dates,
        'tenure_months': np.round(tenure_months, 1),
        'plan_type': plans,
        'monthly_charge': monthly_charges,
        'billing_annual': billing_annual,
        'contract_type': contracts,
        'days_since_last_login': np.round(days_since_last_login, 1),
        'login_frequency_7d': login_frequency_7d,
        'feature_adoption_score': np.round(feature_adoption_score, 1),
        'support_tickets_30d': support_tickets_30d,
        'nps_score': np.round(nps_scores, 1),
        'payment_failures_90d': payment_failures_90d,
        'age_group': ages,
        'acquisition_channel': acquisition_channels,
        'total_spend': np.round(total_spend, 2),
        'churned': churned,
        'churn_date': churn_dates,
        'churn_probability': np.round(churn_probabilities, 3)
    })

    return df


def generate_usage_events(customer_df, events_per_customer=50, seed=42):
    """Generate usage event data for customers"""
    np.random.seed(seed)

    events = []
    event_types = ['login', 'feature_use', 'export', 'share', 'settings_change']

    for _, customer in customer_df.iterrows():
        n_events = np.random.poisson(events_per_customer)

        for _ in range(n_events):
            event_date = customer['signup_date'] + timedelta(
                days=np.random.randint(0, int(customer['tenure_months'] * 30))
            )
            events.append({
                'customer_id': customer['customer_id'],
                'event_date': event_date,
                'event_type': np.random.choice(event_types)
            })

    return pd.DataFrame(events)


def main():
    """Generate and save customer churn data"""
    print("Generating Customer Churn Data...")
    print("=" * 50)

    # Create data directory
    os.makedirs('data', exist_ok=True)

    # Generate customer data
    df = generate_customer_data(n_customers=50000)

    # Save to CSV
    output_path = 'data/customer_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Customer data saved to: {output_path}")

    # Generate usage events
    print("\nGenerating usage events...")
    events_df = generate_usage_events(df.head(10000), events_per_customer=30)
    events_path = 'data/usage_events.csv'
    events_df.to_csv(events_path, index=False)
    print(f"Usage events saved to: {events_path}")

    # Print summary statistics
    print("\n" + "=" * 50)
    print("DATA SUMMARY")
    print("=" * 50)

    print(f"\nTotal Customers: {len(df):,}")
    print(f"Churned Customers: {df['churned'].sum():,} ({df['churned'].mean()*100:.1f}%)")
    print(f"Active Customers: {(~df['churned'].astype(bool)).sum():,}")

    print("\nPlan Distribution:")
    print(df['plan_type'].value_counts().to_string())

    print("\nChurn Rate by Plan:")
    churn_by_plan = df.groupby('plan_type')['churned'].mean() * 100
    print(churn_by_plan.round(1).to_string())

    print("\nChurn Rate by Contract Type:")
    churn_by_contract = df.groupby('contract_type')['churned'].mean() * 100
    print(churn_by_contract.round(1).to_string())

    print("\n" + "=" * 50)
    print("Data generation complete!")


if __name__ == "__main__":
    main()
