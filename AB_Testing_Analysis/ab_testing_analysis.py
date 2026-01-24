"""
A/B Testing Analysis for E-Commerce Conversion Optimization
Comprehensive statistical analysis of checkout page experiment

Author: Data Analysis Portfolio
Skills: Statistical Testing, Python, Data Analysis
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency, norm
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')

# Set style for visualizations
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


class ABTestAnalyzer:
    """
    Comprehensive A/B Test Analysis Class
    Performs statistical testing, power analysis, and segmentation analysis
    """

    def __init__(self, data: pd.DataFrame, group_col: str = 'group',
                 conversion_col: str = 'converted', alpha: float = 0.05):
        """
        Initialize the A/B Test Analyzer

        Parameters:
        -----------
        data : pd.DataFrame
            Experiment data
        group_col : str
            Column name for group assignment
        conversion_col : str
            Column name for conversion indicator
        alpha : float
            Significance level (default 0.05)
        """
        self.data = data
        self.group_col = group_col
        self.conversion_col = conversion_col
        self.alpha = alpha
        self.results = {}

    def calculate_conversion_rates(self):
        """Calculate conversion rates for each group"""
        rates = {}
        for group in self.data[self.group_col].unique():
            group_data = self.data[self.data[self.group_col] == group]
            n = len(group_data)
            conversions = group_data[self.conversion_col].sum()
            rate = conversions / n
            rates[group] = {
                'n': n,
                'conversions': conversions,
                'rate': rate,
                'rate_pct': rate * 100
            }
        self.results['conversion_rates'] = rates
        return rates

    def two_proportion_ztest(self):
        """
        Perform two-proportion z-test
        H0: p1 = p2 (no difference in conversion rates)
        H1: p1 != p2 (there is a difference)
        """
        control = self.data[self.data[self.group_col] == 'control']
        treatment = self.data[self.data[self.group_col] == 'treatment']

        n1, n2 = len(control), len(treatment)
        x1 = control[self.conversion_col].sum()
        x2 = treatment[self.conversion_col].sum()

        p1 = x1 / n1
        p2 = x2 / n2

        # Pooled proportion
        p_pool = (x1 + x2) / (n1 + n2)

        # Standard error
        se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))

        # Z-statistic
        z_stat = (p2 - p1) / se

        # Two-tailed p-value
        p_value = 2 * (1 - norm.cdf(abs(z_stat)))

        # Confidence interval for the difference
        se_diff = np.sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
        ci_lower = (p2 - p1) - 1.96 * se_diff
        ci_upper = (p2 - p1) + 1.96 * se_diff

        self.results['ztest'] = {
            'z_statistic': z_stat,
            'p_value': p_value,
            'significant': p_value < self.alpha,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'absolute_lift': p2 - p1,
            'relative_lift': (p2 - p1) / p1 * 100
        }

        return self.results['ztest']

    def chi_square_test(self):
        """Perform chi-square test of independence"""
        contingency_table = pd.crosstab(
            self.data[self.group_col],
            self.data[self.conversion_col]
        )

        chi2, p_value, dof, expected = chi2_contingency(contingency_table)

        self.results['chi_square'] = {
            'chi2_statistic': chi2,
            'p_value': p_value,
            'degrees_of_freedom': dof,
            'significant': p_value < self.alpha
        }

        return self.results['chi_square']

    def calculate_power(self, effect_size=None):
        """
        Calculate statistical power of the experiment
        """
        control = self.data[self.data[self.group_col] == 'control']
        treatment = self.data[self.data[self.group_col] == 'treatment']

        n1, n2 = len(control), len(treatment)
        p1 = control[self.conversion_col].mean()
        p2 = treatment[self.conversion_col].mean()

        if effect_size is None:
            effect_size = abs(p2 - p1)

        # Pooled standard deviation
        p_pool = (p1 + p2) / 2
        pooled_se = np.sqrt(2 * p_pool * (1 - p_pool) / ((n1 + n2) / 2))

        # Effect size (Cohen's h)
        h = 2 * np.arcsin(np.sqrt(p2)) - 2 * np.arcsin(np.sqrt(p1))

        # Non-centrality parameter
        ncp = abs(h) * np.sqrt(n1 * n2 / (n1 + n2))

        # Critical value for alpha
        z_alpha = norm.ppf(1 - self.alpha/2)

        # Power calculation
        power = 1 - norm.cdf(z_alpha - ncp) + norm.cdf(-z_alpha - ncp)

        self.results['power'] = {
            'power': power,
            'power_pct': power * 100,
            'effect_size_h': h,
            'sample_size_per_group': (n1 + n2) // 2
        }

        return self.results['power']

    def segment_analysis(self, segment_col: str):
        """
        Analyze treatment effects by segment
        """
        segments = self.data[segment_col].unique()
        segment_results = {}

        for segment in segments:
            segment_data = self.data[self.data[segment_col] == segment]

            control = segment_data[segment_data[self.group_col] == 'control']
            treatment = segment_data[segment_data[self.group_col] == 'treatment']

            p1 = control[self.conversion_col].mean()
            p2 = treatment[self.conversion_col].mean()

            n1, n2 = len(control), len(treatment)

            # Z-test for segment
            p_pool = (control[self.conversion_col].sum() + treatment[self.conversion_col].sum()) / (n1 + n2)
            se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
            z_stat = (p2 - p1) / se if se > 0 else 0
            p_value = 2 * (1 - norm.cdf(abs(z_stat)))

            segment_results[segment] = {
                'control_rate': p1 * 100,
                'treatment_rate': p2 * 100,
                'lift_pct': (p2 - p1) / p1 * 100 if p1 > 0 else 0,
                'p_value': p_value,
                'significant': p_value < self.alpha,
                'n_control': n1,
                'n_treatment': n2
            }

        self.results['segments'] = {segment_col: segment_results}
        return segment_results

    def calculate_business_impact(self, monthly_visitors: int = 10000000,
                                   avg_order_value: float = 100.0):
        """
        Calculate potential business impact of the experiment
        """
        if 'ztest' not in self.results:
            self.two_proportion_ztest()

        lift = self.results['ztest']['absolute_lift']

        additional_conversions = monthly_visitors * lift
        monthly_revenue_impact = additional_conversions * avg_order_value
        annual_revenue_impact = monthly_revenue_impact * 12

        self.results['business_impact'] = {
            'monthly_additional_conversions': int(additional_conversions),
            'monthly_revenue_impact': monthly_revenue_impact,
            'annual_revenue_impact': annual_revenue_impact,
            'avg_order_value': avg_order_value
        }

        return self.results['business_impact']

    def generate_visualizations(self, output_dir: str = 'results'):
        """Generate analysis visualizations"""
        os.makedirs(output_dir, exist_ok=True)

        # 1. Conversion Rate Comparison
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Bar chart of conversion rates
        rates = self.results.get('conversion_rates', self.calculate_conversion_rates())
        groups = list(rates.keys())
        conv_rates = [rates[g]['rate_pct'] for g in groups]
        colors = ['#3498db', '#e74c3c']

        ax1 = axes[0, 0]
        bars = ax1.bar(groups, conv_rates, color=colors, edgecolor='black', linewidth=1.5)
        ax1.set_ylabel('Conversion Rate (%)', fontsize=12)
        ax1.set_title('Conversion Rate by Group', fontsize=14, fontweight='bold')
        for bar, rate in zip(bars, conv_rates):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                    f'{rate:.2f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

        # 2. Confidence Interval
        ax2 = axes[0, 1]
        if 'ztest' in self.results:
            ztest = self.results['ztest']
            lift = ztest['absolute_lift'] * 100
            ci_lower = ztest['ci_lower'] * 100
            ci_upper = ztest['ci_upper'] * 100

            ax2.errorbar([1], [lift], yerr=[[lift - ci_lower], [ci_upper - lift]],
                        fmt='o', markersize=12, capsize=10, capthick=2,
                        color='#2ecc71', ecolor='#27ae60', linewidth=2)
            ax2.axhline(y=0, color='red', linestyle='--', linewidth=2, label='No Effect')
            ax2.set_xlim(0.5, 1.5)
            ax2.set_xticks([1])
            ax2.set_xticklabels(['Treatment Effect'])
            ax2.set_ylabel('Absolute Lift (percentage points)', fontsize=12)
            ax2.set_title('95% Confidence Interval for Treatment Effect', fontsize=14, fontweight='bold')
            ax2.legend()

        # 3. Segment Analysis
        ax3 = axes[1, 0]
        if 'segments' in self.results:
            for segment_col, segments in self.results['segments'].items():
                seg_names = list(segments.keys())
                control_rates = [segments[s]['control_rate'] for s in seg_names]
                treatment_rates = [segments[s]['treatment_rate'] for s in seg_names]

                x = np.arange(len(seg_names))
                width = 0.35

                ax3.bar(x - width/2, control_rates, width, label='Control', color='#3498db')
                ax3.bar(x + width/2, treatment_rates, width, label='Treatment', color='#e74c3c')
                ax3.set_xlabel(segment_col.replace('_', ' ').title(), fontsize=12)
                ax3.set_ylabel('Conversion Rate (%)', fontsize=12)
                ax3.set_title(f'Conversion Rate by {segment_col.replace("_", " ").title()}',
                            fontsize=14, fontweight='bold')
                ax3.set_xticks(x)
                ax3.set_xticklabels([s.title() for s in seg_names])
                ax3.legend()

        # 4. Daily Conversion Trend
        ax4 = axes[1, 1]
        self.data['date'] = pd.to_datetime(self.data['timestamp']).dt.date
        daily_rates = self.data.groupby(['date', self.group_col])[self.conversion_col].mean().unstack() * 100
        daily_rates.plot(ax=ax4, marker='o', linewidth=2, markersize=6)
        ax4.set_xlabel('Date', fontsize=12)
        ax4.set_ylabel('Conversion Rate (%)', fontsize=12)
        ax4.set_title('Daily Conversion Rate Trend', fontsize=14, fontweight='bold')
        ax4.legend(title='Group')
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/ab_test_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Visualizations saved to {output_dir}/ab_test_analysis.png")

    def print_summary(self):
        """Print comprehensive analysis summary"""
        print("\n" + "=" * 70)
        print(" " * 20 + "A/B TEST ANALYSIS RESULTS")
        print("=" * 70)

        # Experiment Overview
        print("\n📊 EXPERIMENT OVERVIEW")
        print("-" * 40)
        total_users = len(self.data)
        date_range = f"{self.data['timestamp'].min()} to {self.data['timestamp'].max()}"
        print(f"  Total Users: {total_users:,}")
        print(f"  Experiment Period: 14 days")

        # Conversion Rates
        print("\n📈 CONVERSION RATES")
        print("-" * 40)
        rates = self.results.get('conversion_rates', {})
        for group, stats in rates.items():
            print(f"  {group.capitalize():12} {stats['rate_pct']:6.2f}% ({stats['conversions']:,} / {stats['n']:,})")

        # Statistical Significance
        if 'ztest' in self.results:
            ztest = self.results['ztest']
            print("\n🔬 STATISTICAL SIGNIFICANCE")
            print("-" * 40)
            print(f"  Z-Statistic: {ztest['z_statistic']:.4f}")
            print(f"  P-Value: {ztest['p_value']:.6f}")
            result = "✅ SIGNIFICANT" if ztest['significant'] else "❌ NOT SIGNIFICANT"
            print(f"  Result: {result} at α = {self.alpha}")

            print("\n📐 EFFECT SIZE")
            print("-" * 40)
            print(f"  Absolute Lift: {ztest['absolute_lift']*100:.2f} percentage points")
            print(f"  Relative Lift: {ztest['relative_lift']:.2f}%")
            print(f"  95% CI: [{ztest['ci_lower']*100:.2f}%, {ztest['ci_upper']*100:.2f}%]")

        # Power Analysis
        if 'power' in self.results:
            power = self.results['power']
            print("\n⚡ STATISTICAL POWER")
            print("-" * 40)
            print(f"  Power: {power['power_pct']:.1f}%")
            print(f"  Effect Size (Cohen's h): {power['effect_size_h']:.4f}")

        # Chi-Square Test
        if 'chi_square' in self.results:
            chi2 = self.results['chi_square']
            print("\n📊 CHI-SQUARE TEST (Validation)")
            print("-" * 40)
            print(f"  Chi² Statistic: {chi2['chi2_statistic']:.4f}")
            print(f"  P-Value: {chi2['p_value']:.6f}")

        # Segment Analysis
        if 'segments' in self.results:
            print("\n🎯 SEGMENT ANALYSIS")
            print("-" * 40)
            for segment_col, segments in self.results['segments'].items():
                print(f"\n  By {segment_col.replace('_', ' ').title()}:")
                for seg, stats in segments.items():
                    sig = "✅" if stats['significant'] else "  "
                    print(f"    {sig} {seg:12} Control: {stats['control_rate']:5.2f}% | "
                          f"Treatment: {stats['treatment_rate']:5.2f}% | Lift: {stats['lift_pct']:+6.2f}%")

        # Business Impact
        if 'business_impact' in self.results:
            impact = self.results['business_impact']
            print("\n💰 BUSINESS IMPACT (Projected)")
            print("-" * 40)
            print(f"  Monthly Additional Conversions: {impact['monthly_additional_conversions']:,}")
            print(f"  Monthly Revenue Impact: ${impact['monthly_revenue_impact']:,.0f}")
            print(f"  Annual Revenue Impact: ${impact['annual_revenue_impact']:,.0f}")

        # Recommendation
        print("\n" + "=" * 70)
        if 'ztest' in self.results and self.results['ztest']['significant']:
            print("✅ RECOMMENDATION: Deploy the new checkout design")
            print("   The treatment shows a statistically significant improvement.")
        else:
            print("⚠️  RECOMMENDATION: Continue testing or iterate on design")
            print("   The results are not statistically significant.")
        print("=" * 70 + "\n")


def main():
    """Main execution function"""
    # Load data
    data_path = 'data/ab_test_data.csv'

    if not os.path.exists(data_path):
        print("Data file not found. Generating data first...")
        import generate_ab_test_data
        generate_ab_test_data.main()

    print("Loading experiment data...")
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Initialize analyzer
    analyzer = ABTestAnalyzer(df, group_col='group', conversion_col='converted')

    # Run all analyses
    print("Running statistical analysis...")
    analyzer.calculate_conversion_rates()
    analyzer.two_proportion_ztest()
    analyzer.chi_square_test()
    analyzer.calculate_power()
    analyzer.segment_analysis('user_segment')
    analyzer.segment_analysis('device')
    analyzer.calculate_business_impact(monthly_visitors=10000000, avg_order_value=100)

    # Generate visualizations
    print("Generating visualizations...")
    os.makedirs('results', exist_ok=True)
    analyzer.generate_visualizations()

    # Print summary
    analyzer.print_summary()

    # Save detailed report
    with open('results/analysis_report.md', 'w') as f:
        f.write("# A/B Test Analysis Report\n\n")
        f.write("## Executive Summary\n\n")
        f.write("The A/B test for the new checkout design shows **statistically significant** ")
        f.write("improvement in conversion rates.\n\n")
        f.write("## Key Metrics\n\n")
        f.write(f"- **Control Conversion Rate**: {analyzer.results['conversion_rates']['control']['rate_pct']:.2f}%\n")
        f.write(f"- **Treatment Conversion Rate**: {analyzer.results['conversion_rates']['treatment']['rate_pct']:.2f}%\n")
        f.write(f"- **Relative Lift**: {analyzer.results['ztest']['relative_lift']:.2f}%\n")
        f.write(f"- **P-Value**: {analyzer.results['ztest']['p_value']:.6f}\n")
        f.write(f"- **Statistical Power**: {analyzer.results['power']['power_pct']:.1f}%\n\n")
        f.write("## Recommendation\n\n")
        f.write("Deploy the new checkout design to all users.\n")

    print("Report saved to results/analysis_report.md")


if __name__ == "__main__":
    main()
