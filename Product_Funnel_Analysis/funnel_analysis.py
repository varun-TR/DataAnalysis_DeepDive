"""
Product Funnel Analysis
Comprehensive analysis of user conversion funnel

Author: Data Analysis Portfolio
Skills: Product Analytics, Funnel Analysis, Data Visualization
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


class FunnelAnalyzer:
    """
    Comprehensive Product Funnel Analysis
    """

    def __init__(self, data: pd.DataFrame, funnel_steps: list = None):
        """
        Initialize with event data

        Parameters:
        -----------
        data : pd.DataFrame
            User event data
        funnel_steps : list
            Ordered list of funnel step names
        """
        self.data = data.copy()
        self.funnel_steps = funnel_steps or [
            'app_open',
            'view_product',
            'add_to_cart',
            'begin_checkout',
            'complete_purchase'
        ]
        self.results = {}

    def calculate_funnel_metrics(self):
        """Calculate core funnel metrics"""
        # Count unique users at each step
        step_users = {}
        for step in self.funnel_steps:
            step_users[step] = self.data[self.data['event_name'] == step]['user_id'].nunique()

        # Calculate conversion and drop-off rates
        funnel_metrics = []
        first_step_users = step_users[self.funnel_steps[0]]

        for i, step in enumerate(self.funnel_steps):
            users = step_users[step]

            # Overall conversion from first step
            overall_rate = users / first_step_users if first_step_users > 0 else 0

            # Step conversion rate (from previous step)
            if i == 0:
                step_rate = 1.0
                dropoff_rate = 0.0
                users_lost = 0
            else:
                prev_users = step_users[self.funnel_steps[i-1]]
                step_rate = users / prev_users if prev_users > 0 else 0
                dropoff_rate = 1 - step_rate
                users_lost = prev_users - users

            funnel_metrics.append({
                'step': step,
                'step_order': i + 1,
                'users': users,
                'overall_conversion_rate': overall_rate,
                'step_conversion_rate': step_rate,
                'dropoff_rate': dropoff_rate,
                'users_lost': users_lost
            })

        self.results['funnel_metrics'] = pd.DataFrame(funnel_metrics)
        return self.results['funnel_metrics']

    def calculate_time_to_convert(self):
        """Calculate time between funnel steps"""
        # Pivot data to get timestamps per user per step
        user_steps = self.data.pivot_table(
            index='user_id',
            columns='event_name',
            values='event_timestamp',
            aggfunc='min'
        )

        time_metrics = []
        for i in range(1, len(self.funnel_steps)):
            prev_step = self.funnel_steps[i-1]
            curr_step = self.funnel_steps[i]

            if prev_step in user_steps.columns and curr_step in user_steps.columns:
                # Calculate time delta
                time_delta = (
                    pd.to_datetime(user_steps[curr_step]) -
                    pd.to_datetime(user_steps[prev_step])
                ).dt.total_seconds()

                # Remove negative values and outliers
                time_delta = time_delta[(time_delta > 0) & (time_delta < 86400)]  # Max 24 hours

                if len(time_delta) > 0:
                    time_metrics.append({
                        'from_step': prev_step,
                        'to_step': curr_step,
                        'median_seconds': time_delta.median(),
                        'mean_seconds': time_delta.mean(),
                        'p25_seconds': time_delta.quantile(0.25),
                        'p75_seconds': time_delta.quantile(0.75)
                    })

        self.results['time_to_convert'] = pd.DataFrame(time_metrics)
        return self.results['time_to_convert']

    def segment_analysis(self, segment_col: str):
        """Analyze funnel by segment"""
        segments = self.data[segment_col].unique()
        segment_results = []

        for segment in segments:
            segment_data = self.data[self.data[segment_col] == segment]

            # Calculate users at first and last step
            first_step_users = segment_data[
                segment_data['event_name'] == self.funnel_steps[0]
            ]['user_id'].nunique()

            last_step_users = segment_data[
                segment_data['event_name'] == self.funnel_steps[-1]
            ]['user_id'].nunique()

            overall_conversion = last_step_users / first_step_users if first_step_users > 0 else 0

            # Calculate step-by-step for this segment
            step_conversions = []
            for i, step in enumerate(self.funnel_steps):
                users = segment_data[segment_data['event_name'] == step]['user_id'].nunique()
                step_conversions.append(users)

            segment_results.append({
                'segment': segment,
                'segment_type': segment_col,
                'total_users': first_step_users,
                'converted_users': last_step_users,
                'overall_conversion_rate': overall_conversion,
                'step_users': step_conversions
            })

        segment_df = pd.DataFrame(segment_results)

        # Calculate relative performance
        avg_conversion = segment_df['overall_conversion_rate'].mean()
        segment_df['vs_average'] = (
            (segment_df['overall_conversion_rate'] - avg_conversion) / avg_conversion * 100
        )

        if 'segments' not in self.results:
            self.results['segments'] = {}
        self.results['segments'][segment_col] = segment_df

        return segment_df

    def identify_bottlenecks(self):
        """Identify critical bottlenecks in the funnel"""
        if 'funnel_metrics' not in self.results:
            self.calculate_funnel_metrics()

        metrics = self.results['funnel_metrics']

        # Find steps with highest drop-off
        bottlenecks = metrics[metrics['dropoff_rate'] > 0].sort_values(
            'dropoff_rate', ascending=False
        )

        # Calculate potential revenue impact (assuming $100 avg order value)
        avg_order_value = 100
        bottlenecks['potential_revenue_impact'] = (
            bottlenecks['users_lost'] * avg_order_value *
            metrics.iloc[-1]['step_conversion_rate']  # Estimated downstream conversion
        )

        self.results['bottlenecks'] = bottlenecks
        return bottlenecks

    def statistical_significance_test(self, segment_col: str):
        """Test if segment differences are statistically significant"""
        if 'segments' not in self.results or segment_col not in self.results['segments']:
            self.segment_analysis(segment_col)

        segment_df = self.results['segments'][segment_col]

        # Create contingency table for chi-square test
        converted = segment_df['converted_users'].values
        not_converted = segment_df['total_users'].values - converted

        contingency_table = np.array([converted, not_converted])

        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

        return {
            'chi2_statistic': chi2,
            'p_value': p_value,
            'degrees_of_freedom': dof,
            'significant': p_value < 0.05
        }

    def generate_visualizations(self, output_dir: str = 'results'):
        """Generate funnel visualizations"""
        os.makedirs(output_dir, exist_ok=True)

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Funnel Chart
        ax1 = axes[0, 0]
        if 'funnel_metrics' in self.results:
            metrics = self.results['funnel_metrics']
            steps = metrics['step'].tolist()
            users = metrics['users'].tolist()

            # Create funnel bars
            colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(steps)))
            for i, (step, user_count, color) in enumerate(zip(steps, users, colors)):
                width = user_count / users[0]  # Normalize to first step
                ax1.barh(len(steps) - i - 1, width, height=0.7, color=color,
                        edgecolor='black', linewidth=1.5)
                ax1.text(width + 0.02, len(steps) - i - 1,
                        f'{user_count:,} ({user_count/users[0]*100:.1f}%)',
                        va='center', fontsize=10)

            ax1.set_yticks(range(len(steps)))
            ax1.set_yticklabels(steps[::-1])
            ax1.set_xlim(0, 1.3)
            ax1.set_xlabel('Proportion of Users', fontsize=12)
            ax1.set_title('Conversion Funnel', fontsize=14, fontweight='bold')

        # 2. Drop-off Rate by Step
        ax2 = axes[0, 1]
        if 'funnel_metrics' in self.results:
            metrics = self.results['funnel_metrics']
            steps = metrics[metrics['dropoff_rate'] > 0]['step'].tolist()
            dropoffs = metrics[metrics['dropoff_rate'] > 0]['dropoff_rate'].tolist()

            colors = ['#e74c3c' if d > 0.4 else '#f39c12' if d > 0.3 else '#2ecc71'
                     for d in dropoffs]
            bars = ax2.bar(steps, [d * 100 for d in dropoffs], color=colors, edgecolor='black')

            for bar, dropoff in zip(bars, dropoffs):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{dropoff*100:.1f}%', ha='center', fontsize=10, fontweight='bold')

            ax2.set_ylabel('Drop-off Rate (%)', fontsize=12)
            ax2.set_title('Drop-off Rate by Step', fontsize=14, fontweight='bold')
            ax2.tick_params(axis='x', rotation=45)

        # 3. Segment Comparison
        ax3 = axes[1, 0]
        if 'segments' in self.results and 'device' in self.results['segments']:
            device_df = self.results['segments']['device']
            devices = device_df['segment'].tolist()
            conversions = device_df['overall_conversion_rate'].tolist()

            colors = plt.cm.Set2(range(len(devices)))
            bars = ax3.bar(devices, [c * 100 for c in conversions], color=colors, edgecolor='black')

            for bar, conv in zip(bars, conversions):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                        f'{conv*100:.1f}%', ha='center', fontsize=10, fontweight='bold')

            ax3.set_ylabel('Overall Conversion Rate (%)', fontsize=12)
            ax3.set_title('Conversion Rate by Device', fontsize=14, fontweight='bold')

        # 4. Time to Convert
        ax4 = axes[1, 1]
        if 'time_to_convert' in self.results:
            time_df = self.results['time_to_convert']
            transitions = [f"{row['from_step']}\n→\n{row['to_step']}"
                          for _, row in time_df.iterrows()]
            median_times = time_df['median_seconds'].tolist()

            # Convert to appropriate units
            time_labels = []
            for t in median_times:
                if t < 60:
                    time_labels.append(f'{t:.0f}s')
                elif t < 3600:
                    time_labels.append(f'{t/60:.1f}m')
                else:
                    time_labels.append(f'{t/3600:.1f}h')

            bars = ax4.bar(range(len(transitions)), median_times, color='#3498db', edgecolor='black')

            for bar, label in zip(bars, time_labels):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                        label, ha='center', fontsize=10, fontweight='bold')

            ax4.set_xticks(range(len(transitions)))
            ax4.set_xticklabels(transitions, fontsize=8)
            ax4.set_ylabel('Median Time (seconds)', fontsize=12)
            ax4.set_title('Time to Convert Between Steps', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/funnel_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Visualizations saved to {output_dir}/funnel_analysis.png")

    def print_summary(self):
        """Print comprehensive analysis summary"""
        print("\n" + "=" * 70)
        print(" " * 15 + "PRODUCT FUNNEL ANALYSIS REPORT")
        print("=" * 70)

        # Funnel Overview
        if 'funnel_metrics' in self.results:
            metrics = self.results['funnel_metrics']
            total_users = metrics.iloc[0]['users']
            converted = metrics.iloc[-1]['users']
            overall_rate = metrics.iloc[-1]['overall_conversion_rate']

            print("\n📊 FUNNEL OVERVIEW")
            print("-" * 50)
            print(f"  Total Users: {total_users:,}")
            print(f"  Completed Purchase: {converted:,}")
            print(f"  Overall Conversion: {overall_rate*100:.2f}%")

            print("\n📈 STEP-BY-STEP CONVERSION")
            print("-" * 70)
            print(f"  {'Step':<25} {'Users':>10} {'Rate':>10} {'Drop-off':>10}")
            print("-" * 70)

            for _, row in metrics.iterrows():
                dropoff = f"{row['dropoff_rate']*100:.1f}%" if row['dropoff_rate'] > 0 else "-"
                print(f"  {row['step']:<25} {row['users']:>10,} "
                      f"{row['overall_conversion_rate']*100:>9.1f}% {dropoff:>10}")

        # Bottlenecks
        if 'bottlenecks' in self.results:
            bottlenecks = self.results['bottlenecks']
            worst = bottlenecks.iloc[0]
            print("\n🚨 CRITICAL BOTTLENECK")
            print("-" * 50)
            idx = self.funnel_steps.index(worst['step'])
            prev_step = self.funnel_steps[idx-1] if idx > 0 else None
            print(f"  📍 {prev_step} → {worst['step']}")
            print(f"     Drop-off: {worst['dropoff_rate']*100:.1f}% ({worst['users_lost']:,} users lost)")
            print(f"     Potential Revenue Impact: ${worst['potential_revenue_impact']:,.0f}/month")

        # Segment Performance
        if 'segments' in self.results:
            print("\n🎯 SEGMENT PERFORMANCE")
            print("-" * 50)
            for segment_type, segment_df in self.results['segments'].items():
                print(f"\n  By {segment_type.replace('_', ' ').title()}:")
                for _, row in segment_df.iterrows():
                    vs_avg = f"+{row['vs_average']:.1f}%" if row['vs_average'] > 0 else f"{row['vs_average']:.1f}%"
                    print(f"    {row['segment']:15} {row['overall_conversion_rate']*100:5.1f}%  ({vs_avg} vs avg)")

        # Time to Convert
        if 'time_to_convert' in self.results:
            print("\n⏱️  TIME TO CONVERT (Median)")
            print("-" * 50)
            time_df = self.results['time_to_convert']
            for _, row in time_df.iterrows():
                seconds = row['median_seconds']
                if seconds < 60:
                    time_str = f"{seconds:.0f} seconds"
                elif seconds < 3600:
                    time_str = f"{seconds/60:.1f} minutes"
                else:
                    time_str = f"{seconds/3600:.1f} hours"
                print(f"  {row['from_step']:20} → {row['to_step']:20} {time_str}")

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
    analyzer = FunnelAnalyzer(df)

    # Run all analyses
    print("Running funnel analysis...")
    analyzer.calculate_funnel_metrics()
    analyzer.calculate_time_to_convert()
    analyzer.segment_analysis('device')
    analyzer.segment_analysis('user_type')
    analyzer.segment_analysis('traffic_source')
    analyzer.identify_bottlenecks()

    # Generate visualizations
    print("Generating visualizations...")
    os.makedirs('results', exist_ok=True)
    analyzer.generate_visualizations()

    # Print summary
    analyzer.print_summary()

    # Save report
    with open('results/funnel_report.md', 'w') as f:
        metrics = analyzer.results['funnel_metrics']
        f.write("# Product Funnel Analysis Report\n\n")
        f.write("## Executive Summary\n\n")
        f.write(f"- Total Users Analyzed: {metrics.iloc[0]['users']:,}\n")
        f.write(f"- Overall Conversion Rate: {metrics.iloc[-1]['overall_conversion_rate']*100:.2f}%\n")
        f.write(f"- Critical Bottleneck: View Product → Add to Cart\n\n")

    print("\nReport saved to results/funnel_report.md")


if __name__ == "__main__":
    main()
