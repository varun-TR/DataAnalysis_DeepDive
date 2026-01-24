"""
A/B Test Data Generator
Generates realistic synthetic data for A/B testing analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_ab_test_data(n_users=100000, seed=42):
    """
    Generate synthetic A/B test data for e-commerce checkout experiment

    Parameters:
    -----------
    n_users : int
        Total number of users in the experiment
    seed : int
        Random seed for reproducibility

    Returns:
    --------
    pd.DataFrame
        DataFrame containing experiment data
    """
    np.random.seed(seed)

    # Experiment parameters
    control_conversion_rate = 0.112  # 11.2% baseline
    treatment_lift = 0.232  # 23.2% relative lift
    treatment_conversion_rate = control_conversion_rate * (1 + treatment_lift)

    # Generate user IDs
    user_ids = [f"user_{i:06d}" for i in range(n_users)]

    # Randomly assign to control (0) or treatment (1)
    groups = np.random.choice(['control', 'treatment'], size=n_users)

    # Generate device types with realistic distribution
    device_probs = {'mobile': 0.55, 'desktop': 0.35, 'tablet': 0.10}
    devices = np.random.choice(
        list(device_probs.keys()),
        size=n_users,
        p=list(device_probs.values())
    )

    # Generate user segments
    segment_probs = {'new': 0.40, 'returning': 0.35, 'loyal': 0.25}
    segments = np.random.choice(
        list(segment_probs.keys()),
        size=n_users,
        p=list(segment_probs.values())
    )

    # Generate timestamps over 14 days
    start_date = datetime(2024, 1, 1)
    timestamps = [
        start_date + timedelta(
            days=np.random.randint(0, 14),
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60)
        )
        for _ in range(n_users)
    ]

    # Generate conversions based on group and segment
    # Different segments have different conversion rates
    segment_multipliers = {'new': 0.8, 'returning': 1.0, 'loyal': 1.3}
    device_multipliers = {'mobile': 0.85, 'desktop': 1.1, 'tablet': 0.95}

    conversions = []
    for i in range(n_users):
        base_rate = control_conversion_rate if groups[i] == 'control' else treatment_conversion_rate
        adjusted_rate = base_rate * segment_multipliers[segments[i]] * device_multipliers[devices[i]]
        adjusted_rate = min(adjusted_rate, 0.99)  # Cap at 99%
        conversions.append(np.random.binomial(1, adjusted_rate))

    # Generate session duration (seconds)
    session_durations = np.random.exponential(180, n_users) + 30  # Mean ~180s, min 30s
    session_durations = np.clip(session_durations, 30, 1800)  # Cap at 30 min

    # Generate page views
    page_views = np.random.poisson(5, n_users) + 1

    # Generate revenue for converted users
    revenues = []
    for i in range(n_users):
        if conversions[i] == 1:
            # Log-normal distribution for order values
            base_revenue = np.random.lognormal(4.5, 0.8)  # Mean ~$100
            if segments[i] == 'loyal':
                base_revenue *= 1.5
            revenues.append(round(base_revenue, 2))
        else:
            revenues.append(0.0)

    # Create DataFrame
    df = pd.DataFrame({
        'user_id': user_ids,
        'timestamp': timestamps,
        'group': groups,
        'device': devices,
        'user_segment': segments,
        'converted': conversions,
        'session_duration_sec': np.round(session_durations, 1),
        'page_views': page_views,
        'revenue': revenues
    })

    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)

    return df


def main():
    """Generate and save A/B test data"""
    print("Generating A/B Test Data...")
    print("=" * 50)

    # Create data directory
    os.makedirs('data', exist_ok=True)

    # Generate data
    df = generate_ab_test_data(n_users=100000)

    # Save to CSV
    output_path = 'data/ab_test_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Data saved to: {output_path}")

    # Print summary statistics
    print("\nData Summary:")
    print(f"  Total Users: {len(df):,}")
    print(f"  Control Group: {(df['group'] == 'control').sum():,}")
    print(f"  Treatment Group: {(df['group'] == 'treatment').sum():,}")
    print(f"  Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}")

    print("\nConversion Rates:")
    for group in ['control', 'treatment']:
        group_df = df[df['group'] == group]
        conv_rate = group_df['converted'].mean() * 100
        print(f"  {group.capitalize()}: {conv_rate:.2f}%")

    print("\nDevice Distribution:")
    print(df['device'].value_counts(normalize=True).to_string())

    print("\nUser Segment Distribution:")
    print(df['user_segment'].value_counts(normalize=True).to_string())

    print("\n" + "=" * 50)
    print("Data generation complete!")


if __name__ == "__main__":
    main()
