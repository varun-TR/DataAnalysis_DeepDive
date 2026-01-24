"""
Product Funnel Data Generator
Generates realistic synthetic user event data for funnel analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_funnel_data(n_users=100000, seed=42):
    """
    Generate synthetic user event data for funnel analysis

    Parameters:
    -----------
    n_users : int
        Number of users to simulate
    seed : int
        Random seed for reproducibility

    Returns:
    --------
    pd.DataFrame
        DataFrame containing user events
    """
    np.random.seed(seed)

    # Define funnel steps and their base conversion rates
    funnel_steps = [
        ('app_open', 1.0),
        ('view_product', 0.725),
        ('add_to_cart', 0.527),
        ('begin_checkout', 0.562),
        ('complete_purchase', 0.692)
    ]

    # User attributes
    user_ids = [f"user_{i:06d}" for i in range(n_users)]

    # Device distribution
    device_probs = {'ios': 0.45, 'android': 0.40, 'web': 0.15}
    devices = np.random.choice(
        list(device_probs.keys()),
        size=n_users,
        p=list(device_probs.values())
    )

    # Device-specific conversion multipliers
    device_multipliers = {'ios': 1.15, 'android': 0.88, 'web': 1.0}

    # User type
    user_types = np.random.choice(
        ['new', 'returning'],
        size=n_users,
        p=[0.6, 0.4]
    )

    # User type multipliers
    user_type_multipliers = {'new': 0.75, 'returning': 1.35}

    # Traffic source
    traffic_sources = ['organic', 'paid_search', 'social', 'email', 'direct']
    source_probs = [0.30, 0.25, 0.20, 0.10, 0.15]
    sources = np.random.choice(traffic_sources, size=n_users, p=source_probs)

    # Source multipliers
    source_multipliers = {
        'organic': 1.1,
        'paid_search': 0.95,
        'social': 0.85,
        'email': 1.25,
        'direct': 1.0
    }

    # Geographic regions
    regions = ['North America', 'Europe', 'Asia', 'South America', 'Other']
    region_probs = [0.35, 0.30, 0.20, 0.10, 0.05]
    user_regions = np.random.choice(regions, size=n_users, p=region_probs)

    # Session start times (last 30 days)
    base_date = datetime(2024, 1, 15)
    session_starts = [
        base_date - timedelta(
            days=np.random.randint(0, 30),
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60)
        )
        for _ in range(n_users)
    ]

    # Generate events
    events = []

    for i in range(n_users):
        user_id = user_ids[i]
        device = devices[i]
        user_type = user_types[i]
        source = sources[i]
        region = user_regions[i]
        session_start = session_starts[i]

        # Calculate combined conversion modifier
        device_mod = device_multipliers[device]
        user_mod = user_type_multipliers[user_type]
        source_mod = source_multipliers[source]
        combined_mod = device_mod * user_mod * source_mod

        # Track progress through funnel
        current_time = session_start
        cumulative_rate = 1.0

        for step, base_rate in funnel_steps:
            # Adjust conversion rate
            if step == 'app_open':
                passes = True
            else:
                adjusted_rate = min(base_rate * combined_mod, 0.98)
                passes = np.random.random() < adjusted_rate

            if passes:
                # Add time delta between steps
                if step != 'app_open':
                    time_deltas = {
                        'view_product': np.random.exponential(45),  # seconds
                        'add_to_cart': np.random.exponential(180),
                        'begin_checkout': np.random.exponential(600),
                        'complete_purchase': np.random.exponential(150)
                    }
                    current_time += timedelta(seconds=time_deltas.get(step, 60))

                events.append({
                    'user_id': user_id,
                    'event_name': step,
                    'event_timestamp': current_time,
                    'device': device,
                    'user_type': user_type,
                    'traffic_source': source,
                    'region': region,
                    'session_id': f"session_{user_id}_{session_start.strftime('%Y%m%d%H%M')}"
                })
            else:
                # User dropped off
                break

    # Create DataFrame
    df = pd.DataFrame(events)

    # Add additional event properties
    df['hour_of_day'] = pd.to_datetime(df['event_timestamp']).dt.hour
    df['day_of_week'] = pd.to_datetime(df['event_timestamp']).dt.day_name()

    # Add product-related data for view_product and later events
    product_categories = ['Electronics', 'Clothing', 'Home', 'Beauty', 'Sports']
    df['product_category'] = np.random.choice(product_categories, size=len(df))

    # Add price for cart events
    df['price'] = np.where(
        df['event_name'].isin(['add_to_cart', 'begin_checkout', 'complete_purchase']),
        np.round(np.random.lognormal(4, 0.8, len(df)), 2),
        0
    )

    return df


def main():
    """Generate and save funnel data"""
    print("Generating Product Funnel Data...")
    print("=" * 50)

    # Create data directory
    os.makedirs('data', exist_ok=True)

    # Generate data
    df = generate_funnel_data(n_users=100000)

    # Save to CSV
    output_path = 'data/user_events.csv'
    df.to_csv(output_path, index=False)
    print(f"Event data saved to: {output_path}")

    # Print summary statistics
    print("\n" + "=" * 50)
    print("DATA SUMMARY")
    print("=" * 50)

    print(f"\nTotal Events: {len(df):,}")
    print(f"Unique Users: {df['user_id'].nunique():,}")

    print("\nEvents by Step:")
    event_counts = df.groupby('event_name')['user_id'].nunique()
    funnel_order = ['app_open', 'view_product', 'add_to_cart', 'begin_checkout', 'complete_purchase']
    for step in funnel_order:
        if step in event_counts.index:
            print(f"  {step:20} {event_counts[step]:,}")

    print("\nDevice Distribution:")
    print(df.groupby('device')['user_id'].nunique().to_string())

    print("\nUser Type Distribution:")
    print(df.groupby('user_type')['user_id'].nunique().to_string())

    print("\n" + "=" * 50)
    print("Data generation complete!")


if __name__ == "__main__":
    main()
