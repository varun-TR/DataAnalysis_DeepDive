"""
Product Funnel Segmentation Analysis
Deep-dive analysis of funnel performance across segments

Author: Data Analysis Portfolio
Skills: Segmentation, Statistical Analysis, Product Analytics
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')


class SegmentationAnalyzer:
    """
    Deep-dive segmentation analysis for product funnel
    """

    def __init__(self, data: pd.DataFrame, funnel_steps: list = None):
        """Initialize with event data"""
        self.data = data.copy()
        self.funnel_steps = funnel_steps or [
            'app_open',
            'view_product',
            'add_to_cart',
            'begin_checkout',
            'complete_purchase'
        ]
        self.results = {}

    def multi_dimensional_analysis(self, dimensions: list):
        """Analyze conversion across multiple dimensions"""
        results = []

        # Get unique combinations
        grouped = self.data.groupby(dimensions)

        for group_key, group_data in grouped:
            if isinstance(group_key, str):
                group_key = (group_key,)

            first_step_users = group_data[
                group_data['event_name'] == self.funnel_steps[0]
            ]['user_id'].nunique()

            last_step_users = group_data[
                group_data['event_name'] == self.funnel_steps[-1]
            ]['user_id'].nunique()

            if first_step_users > 0:
                conversion = last_step_users / first_step_users
            else:
                conversion = 0

            result = {dim: val for dim, val in zip(dimensions, group_key)}
            result.update({
                'users': first_step_users,
                'conversions': last_step_users,
                'conversion_rate': conversion
            })
            results.append(result)

        return pd.DataFrame(results)

    def cohort_analysis(self):
        """Analyze funnel by user cohort (first visit date)"""
        # Get first visit date per user
        user_first_visit = self.data.groupby('user_id')['event_timestamp'].min().reset_index()
        user_first_visit.columns = ['user_id', 'first_visit']
        user_first_visit['cohort'] = pd.to_datetime(user_first_visit['first_visit']).dt.to_period('W')

        # Merge back to data
        data_with_cohort = self.data.merge(user_first_visit[['user_id', 'cohort']], on='user_id')

        # Calculate conversion by cohort
        cohort_results = []
        for cohort in data_with_cohort['cohort'].unique():
            cohort_data = data_with_cohort[data_with_cohort['cohort'] == cohort]

            first_users = cohort_data[
                cohort_data['event_name'] == self.funnel_steps[0]
            ]['user_id'].nunique()

            last_users = cohort_data[
                cohort_data['event_name'] == self.funnel_steps[-1]
            ]['user_id'].nunique()

            cohort_results.append({
                'cohort': str(cohort),
                'users': first_users,
                'conversions': last_users,
                'conversion_rate': last_users / first_users if first_users > 0 else 0
            })

        self.results['cohort'] = pd.DataFrame(cohort_results).sort_values('cohort')
        return self.results['cohort']

    def time_based_analysis(self):
        """Analyze funnel by time of day and day of week"""
        # Hour of day analysis
        hourly_results = []
        for hour in range(24):
            hour_data = self.data[self.data['hour_of_day'] == hour]

            first_users = hour_data[
                hour_data['event_name'] == self.funnel_steps[0]
            ]['user_id'].nunique()

            last_users = hour_data[
                hour_data['event_name'] == self.funnel_steps[-1]
            ]['user_id'].nunique()

            hourly_results.append({
                'hour': hour,
                'users': first_users,
                'conversions': last_users,
                'conversion_rate': last_users / first_users if first_users > 0 else 0
            })

        self.results['hourly'] = pd.DataFrame(hourly_results)

        # Day of week analysis
        daily_results = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for day in days:
            day_data = self.data[self.data['day_of_week'] == day]

            first_users = day_data[
                day_data['event_name'] == self.funnel_steps[0]
            ]['user_id'].nunique()

            last_users = day_data[
                day_data['event_name'] == self.funnel_steps[-1]
            ]['user_id'].nunique()

            daily_results.append({
                'day': day,
                'users': first_users,
                'conversions': last_users,
                'conversion_rate': last_users / first_users if first_users > 0 else 0
            })

        self.results['daily'] = pd.DataFrame(daily_results)

        return self.results['hourly'], self.results['daily']

    def product_category_analysis(self):
        """Analyze conversion by product category"""
        # Focus on users who viewed products
        product_users = self.data[self.data['event_name'].isin([
            'view_product', 'add_to_cart', 'begin_checkout', 'complete_purchase'
        ])]

        category_results = []
        for category in product_users['product_category'].unique():
            cat_data = product_users[product_users['product_category'] == category]

            view_users = cat_data[
                cat_data['event_name'] == 'view_product'
            ]['user_id'].nunique()

            purchase_users = cat_data[
                cat_data['event_name'] == 'complete_purchase'
            ]['user_id'].nunique()

            add_cart_users = cat_data[
                cat_data['event_name'] == 'add_to_cart'
            ]['user_id'].nunique()

            category_results.append({
                'category': category,
                'views': view_users,
                'add_to_cart': add_cart_users,
                'purchases': purchase_users,
                'view_to_cart_rate': add_cart_users / view_users if view_users > 0 else 0,
                'cart_to_purchase_rate': purchase_users / add_cart_users if add_cart_users > 0 else 0,
                'overall_conversion': purchase_users / view_users if view_users > 0 else 0
            })

        self.results['product_category'] = pd.DataFrame(category_results)
        return self.results['product_category']

    def calculate_lift_opportunities(self):
        """Calculate potential lift from bringing segments to best-in-class"""
        opportunities = []

        # Device analysis
        device_analysis = self.multi_dimensional_analysis(['device'])
        best_device_rate = device_analysis['conversion_rate'].max()

        for _, row in device_analysis.iterrows():
            if row['conversion_rate'] < best_device_rate:
                potential_lift = (best_device_rate - row['conversion_rate']) * row['users']
                opportunities.append({
                    'segment': f"Device: {row['device']}",
                    'current_rate': row['conversion_rate'],
                    'target_rate': best_device_rate,
                    'potential_additional_conversions': int(potential_lift),
                    'potential_revenue': potential_lift * 100  # Assuming $100 AOV
                })

        # User type analysis
        user_type_analysis = self.multi_dimensional_analysis(['user_type'])
        best_user_rate = user_type_analysis['conversion_rate'].max()

        for _, row in user_type_analysis.iterrows():
            if row['conversion_rate'] < best_user_rate:
                potential_lift = (best_user_rate - row['conversion_rate']) * row['users']
                opportunities.append({
                    'segment': f"User Type: {row['user_type']}",
                    'current_rate': row['conversion_rate'],
                    'target_rate': best_user_rate,
                    'potential_additional_conversions': int(potential_lift),
                    'potential_revenue': potential_lift * 100
                })

        self.results['opportunities'] = pd.DataFrame(opportunities).sort_values(
            'potential_revenue', ascending=False
        )

        return self.results['opportunities']

    def generate_visualizations(self, output_dir: str = 'results'):
        """Generate segmentation visualizations"""
        os.makedirs(output_dir, exist_ok=True)

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Hourly Conversion Pattern
        ax1 = axes[0, 0]
        if 'hourly' in self.results:
            hourly = self.results['hourly']
            ax1.plot(hourly['hour'], hourly['conversion_rate'] * 100,
                    marker='o', linewidth=2, color='#3498db')
            ax1.fill_between(hourly['hour'], 0, hourly['conversion_rate'] * 100,
                           alpha=0.3, color='#3498db')
            ax1.set_xlabel('Hour of Day', fontsize=12)
            ax1.set_ylabel('Conversion Rate (%)', fontsize=12)
            ax1.set_title('Conversion Rate by Hour of Day', fontsize=14, fontweight='bold')
            ax1.set_xticks(range(0, 24, 2))

        # 2. Day of Week Pattern
        ax2 = axes[0, 1]
        if 'daily' in self.results:
            daily = self.results['daily']
            colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(daily)))
            bars = ax2.bar(daily['day'], daily['conversion_rate'] * 100, color=colors, edgecolor='black')
            ax2.set_ylabel('Conversion Rate (%)', fontsize=12)
            ax2.set_title('Conversion Rate by Day of Week', fontsize=14, fontweight='bold')
            ax2.tick_params(axis='x', rotation=45)

        # 3. Product Category Performance
        ax3 = axes[1, 0]
        if 'product_category' in self.results:
            cat_df = self.results['product_category']
            x = np.arange(len(cat_df))
            width = 0.35

            ax3.bar(x - width/2, cat_df['view_to_cart_rate'] * 100, width,
                   label='View → Cart', color='#3498db', edgecolor='black')
            ax3.bar(x + width/2, cat_df['cart_to_purchase_rate'] * 100, width,
                   label='Cart → Purchase', color='#2ecc71', edgecolor='black')

            ax3.set_xticks(x)
            ax3.set_xticklabels(cat_df['category'], rotation=45)
            ax3.set_ylabel('Conversion Rate (%)', fontsize=12)
            ax3.set_title('Conversion by Product Category', fontsize=14, fontweight='bold')
            ax3.legend()

        # 4. Lift Opportunities
        ax4 = axes[1, 1]
        if 'opportunities' in self.results:
            opps = self.results['opportunities'].head(5)
            y_pos = np.arange(len(opps))
            bars = ax4.barh(y_pos, opps['potential_revenue'] / 1000, color='#e74c3c', edgecolor='black')
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels(opps['segment'])
            ax4.set_xlabel('Potential Revenue ($K)', fontsize=12)
            ax4.set_title('Top Revenue Opportunities by Segment', fontsize=14, fontweight='bold')
            ax4.invert_yaxis()

        plt.tight_layout()
        plt.savefig(f'{output_dir}/segmentation_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Visualizations saved to {output_dir}/segmentation_analysis.png")

    def print_summary(self):
        """Print segmentation analysis summary"""
        print("\n" + "=" * 70)
        print(" " * 12 + "PRODUCT FUNNEL SEGMENTATION ANALYSIS")
        print("=" * 70)

        # Time-based insights
        if 'hourly' in self.results:
            hourly = self.results['hourly']
            best_hour = hourly.loc[hourly['conversion_rate'].idxmax()]
            worst_hour = hourly.loc[hourly['conversion_rate'].idxmin()]

            print("\n⏰ TIME-BASED INSIGHTS")
            print("-" * 50)
            print(f"  Best Hour: {int(best_hour['hour'])}:00 ({best_hour['conversion_rate']*100:.1f}% conversion)")
            print(f"  Worst Hour: {int(worst_hour['hour'])}:00 ({worst_hour['conversion_rate']*100:.1f}% conversion)")

        if 'daily' in self.results:
            daily = self.results['daily']
            best_day = daily.loc[daily['conversion_rate'].idxmax()]
            worst_day = daily.loc[daily['conversion_rate'].idxmin()]
            print(f"  Best Day: {best_day['day']} ({best_day['conversion_rate']*100:.1f}% conversion)")
            print(f"  Worst Day: {worst_day['day']} ({worst_day['conversion_rate']*100:.1f}% conversion)")

        # Product category insights
        if 'product_category' in self.results:
            print("\n📦 PRODUCT CATEGORY PERFORMANCE")
            print("-" * 50)
            cat_df = self.results['product_category']
            for _, row in cat_df.sort_values('overall_conversion', ascending=False).iterrows():
                print(f"  {row['category']:15} "
                      f"View→Cart: {row['view_to_cart_rate']*100:5.1f}% | "
                      f"Cart→Purchase: {row['cart_to_purchase_rate']*100:5.1f}%")

        # Lift opportunities
        if 'opportunities' in self.results:
            print("\n💰 TOP REVENUE OPPORTUNITIES")
            print("-" * 50)
            for _, row in self.results['opportunities'].head(5).iterrows():
                print(f"  {row['segment']}")
                print(f"    Current: {row['current_rate']*100:.1f}% → Target: {row['target_rate']*100:.1f}%")
                print(f"    Potential Revenue: ${row['potential_revenue']:,.0f}")

        print("\n" + "=" * 70)


def main():
    """Main execution function"""
    data_path = 'data/user_events.csv'

    if not os.path.exists(data_path):
        print("Data file not found. Generating data first...")
        import generate_funnel_data
        generate_funnel_data.main()

    print("Loading event data...")
    df = pd.read_csv(data_path)

    # Initialize analyzer
    analyzer = SegmentationAnalyzer(df)

    # Run analyses
    print("Running segmentation analysis...")
    analyzer.cohort_analysis()
    analyzer.time_based_analysis()
    analyzer.product_category_analysis()
    analyzer.calculate_lift_opportunities()

    # Generate visualizations
    print("Generating visualizations...")
    os.makedirs('results', exist_ok=True)
    analyzer.generate_visualizations()

    # Print summary
    analyzer.print_summary()

    print("\nSegmentation analysis complete!")


if __name__ == "__main__":
    main()
