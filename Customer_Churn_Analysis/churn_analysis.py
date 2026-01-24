"""
Customer Churn Analysis
Comprehensive EDA and statistical analysis of customer churn

Author: Data Analysis Portfolio
Skills: EDA, Statistical Analysis, Data Visualization
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


class ChurnAnalyzer:
    """
    Comprehensive Customer Churn Analysis
    """

    def __init__(self, data: pd.DataFrame):
        """Initialize with customer data"""
        self.data = data.copy()
        self.results = {}
        self._preprocess_data()

    def _preprocess_data(self):
        """Preprocess and create derived features"""
        # Create binary flags
        self.data['is_monthly_billing'] = (self.data['billing_annual'] == 0).astype(int)
        self.data['is_month_to_month'] = (self.data['contract_type'] == 'month-to-month').astype(int)
        self.data['has_payment_failure'] = (self.data['payment_failures_90d'] > 0).astype(int)
        self.data['is_inactive'] = (self.data['days_since_last_login'] > 14).astype(int)
        self.data['low_engagement'] = (self.data['feature_adoption_score'] < 30).astype(int)
        self.data['is_detractor'] = (self.data['nps_score'] < 0).astype(int)

    def calculate_overall_metrics(self):
        """Calculate overall churn metrics"""
        total = len(self.data)
        churned = self.data['churned'].sum()
        active = total - churned

        churn_rate = churned / total
        mrr_at_risk = self.data[self.data['churned'] == 1]['monthly_charge'].sum()

        self.results['overall'] = {
            'total_customers': total,
            'churned_customers': churned,
            'active_customers': active,
            'churn_rate': churn_rate,
            'mrr_at_risk': mrr_at_risk
        }

        return self.results['overall']

    def analyze_churn_by_segment(self, segment_col: str):
        """Analyze churn rate by different segments"""
        segment_analysis = self.data.groupby(segment_col).agg({
            'churned': ['sum', 'count', 'mean'],
            'monthly_charge': 'mean'
        }).round(3)

        segment_analysis.columns = ['churned_count', 'total_count', 'churn_rate', 'avg_monthly_charge']
        segment_analysis['churn_rate_pct'] = segment_analysis['churn_rate'] * 100

        # Chi-square test for significance
        contingency = pd.crosstab(self.data[segment_col], self.data['churned'])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

        if segment_col not in self.results:
            self.results['segments'] = {}

        self.results['segments'][segment_col] = {
            'data': segment_analysis,
            'chi2': chi2,
            'p_value': p_value,
            'significant': p_value < 0.05
        }

        return segment_analysis

    def cohort_analysis(self):
        """Perform cohort analysis based on signup month"""
        self.data['signup_month'] = pd.to_datetime(self.data['signup_date']).dt.to_period('M')

        cohort_data = self.data.groupby('signup_month').agg({
            'churned': ['sum', 'count', 'mean'],
            'tenure_months': 'mean'
        }).round(3)

        cohort_data.columns = ['churned', 'total', 'churn_rate', 'avg_tenure']
        cohort_data['retention_rate'] = 1 - cohort_data['churn_rate']

        self.results['cohort'] = cohort_data

        return cohort_data

    def feature_correlation_analysis(self):
        """Analyze correlation between features and churn"""
        numeric_cols = [
            'tenure_months', 'monthly_charge', 'days_since_last_login',
            'login_frequency_7d', 'feature_adoption_score', 'support_tickets_30d',
            'nps_score', 'payment_failures_90d', 'total_spend',
            'is_monthly_billing', 'is_month_to_month', 'has_payment_failure',
            'is_inactive', 'low_engagement', 'is_detractor'
        ]

        correlations = {}
        for col in numeric_cols:
            if col in self.data.columns:
                corr, p_value = stats.pointbiserialr(self.data['churned'], self.data[col])
                correlations[col] = {
                    'correlation': corr,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }

        # Sort by absolute correlation
        correlations = dict(sorted(correlations.items(),
                                   key=lambda x: abs(x[1]['correlation']),
                                   reverse=True))

        self.results['correlations'] = correlations
        return correlations

    def calculate_clv(self):
        """Calculate Customer Lifetime Value metrics"""
        # Simple CLV calculation
        avg_tenure = self.data['tenure_months'].mean()
        avg_monthly_revenue = self.data['monthly_charge'].mean()
        churn_rate = self.data['churned'].mean()

        # CLV = ARPU / Churn Rate
        if churn_rate > 0:
            clv = avg_monthly_revenue / churn_rate
        else:
            clv = avg_monthly_revenue * 24  # Assume 2 years if no churn

        # CLV by segment
        clv_by_plan = self.data.groupby('plan_type').apply(
            lambda x: x['monthly_charge'].mean() / max(x['churned'].mean(), 0.01)
        ).round(2)

        self.results['clv'] = {
            'overall_clv': clv,
            'avg_monthly_revenue': avg_monthly_revenue,
            'avg_tenure_months': avg_tenure,
            'clv_by_plan': clv_by_plan.to_dict()
        }

        return self.results['clv']

    def risk_factor_analysis(self):
        """Analyze impact of individual risk factors on churn"""
        risk_factors = [
            ('has_payment_failure', 'Payment Failure'),
            ('is_inactive', 'Inactive (>14 days)'),
            ('is_monthly_billing', 'Monthly Billing'),
            ('is_month_to_month', 'Month-to-Month Contract'),
            ('low_engagement', 'Low Engagement (<30 score)'),
            ('is_detractor', 'NPS Detractor')
        ]

        risk_analysis = []
        for factor, label in risk_factors:
            if factor in self.data.columns:
                with_factor = self.data[self.data[factor] == 1]['churned'].mean()
                without_factor = self.data[self.data[factor] == 0]['churned'].mean()
                relative_risk = with_factor / max(without_factor, 0.001)

                risk_analysis.append({
                    'factor': label,
                    'churn_with': with_factor * 100,
                    'churn_without': without_factor * 100,
                    'relative_risk': relative_risk,
                    'lift_pct': (relative_risk - 1) * 100
                })

        risk_df = pd.DataFrame(risk_analysis).sort_values('relative_risk', ascending=False)
        self.results['risk_factors'] = risk_df

        return risk_df

    def generate_visualizations(self, output_dir: str = 'results'):
        """Generate analysis visualizations"""
        os.makedirs(output_dir, exist_ok=True)

        fig, axes = plt.subplots(2, 3, figsize=(18, 12))

        # 1. Churn Rate by Plan
        ax1 = axes[0, 0]
        churn_by_plan = self.data.groupby('plan_type')['churned'].mean() * 100
        colors = ['#e74c3c' if x > 20 else '#3498db' for x in churn_by_plan.values]
        bars = ax1.bar(churn_by_plan.index, churn_by_plan.values, color=colors, edgecolor='black')
        ax1.set_ylabel('Churn Rate (%)', fontsize=12)
        ax1.set_title('Churn Rate by Subscription Plan', fontsize=14, fontweight='bold')
        for bar, val in zip(bars, churn_by_plan.values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{val:.1f}%', ha='center', fontsize=10)

        # 2. Risk Factor Impact
        ax2 = axes[0, 1]
        if 'risk_factors' in self.results:
            risk_df = self.results['risk_factors']
            y_pos = np.arange(len(risk_df))
            ax2.barh(y_pos, risk_df['lift_pct'], color='#e74c3c', edgecolor='black')
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(risk_df['factor'])
            ax2.set_xlabel('Churn Lift (%)', fontsize=12)
            ax2.set_title('Risk Factor Impact on Churn', fontsize=14, fontweight='bold')
            ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.5)

        # 3. Churn by Contract Type
        ax3 = axes[0, 2]
        churn_by_contract = self.data.groupby('contract_type')['churned'].mean() * 100
        colors = sns.color_palette('RdYlGn_r', len(churn_by_contract))
        ax3.pie(churn_by_contract.values, labels=churn_by_contract.index,
               autopct='%1.1f%%', colors=colors, explode=[0.05]*len(churn_by_contract))
        ax3.set_title('Churn Distribution by Contract Type', fontsize=14, fontweight='bold')

        # 4. Days Since Login vs Churn
        ax4 = axes[1, 0]
        bins = [0, 7, 14, 30, 60, 90]
        labels = ['0-7', '8-14', '15-30', '31-60', '60+']
        self.data['login_bucket'] = pd.cut(self.data['days_since_last_login'],
                                           bins=bins, labels=labels, include_lowest=True)
        churn_by_login = self.data.groupby('login_bucket')['churned'].mean() * 100
        ax4.bar(range(len(churn_by_login)), churn_by_login.values,
               color=plt.cm.Reds(np.linspace(0.3, 0.9, len(churn_by_login))), edgecolor='black')
        ax4.set_xticks(range(len(churn_by_login)))
        ax4.set_xticklabels(labels)
        ax4.set_xlabel('Days Since Last Login', fontsize=12)
        ax4.set_ylabel('Churn Rate (%)', fontsize=12)
        ax4.set_title('Churn Rate by Login Recency', fontsize=14, fontweight='bold')

        # 5. Feature Adoption Score Distribution
        ax5 = axes[1, 1]
        churned_data = self.data[self.data['churned'] == 1]['feature_adoption_score']
        active_data = self.data[self.data['churned'] == 0]['feature_adoption_score']
        ax5.hist(active_data, bins=20, alpha=0.7, label='Active', color='#2ecc71', edgecolor='black')
        ax5.hist(churned_data, bins=20, alpha=0.7, label='Churned', color='#e74c3c', edgecolor='black')
        ax5.set_xlabel('Feature Adoption Score', fontsize=12)
        ax5.set_ylabel('Frequency', fontsize=12)
        ax5.set_title('Feature Adoption: Churned vs Active', fontsize=14, fontweight='bold')
        ax5.legend()

        # 6. Correlation Heatmap
        ax6 = axes[1, 2]
        if 'correlations' in self.results:
            corr_data = {k: v['correlation'] for k, v in list(self.results['correlations'].items())[:8]}
            corr_df = pd.DataFrame([corr_data]).T
            corr_df.columns = ['Correlation with Churn']
            sns.heatmap(corr_df, annot=True, cmap='RdYlGn_r', center=0, ax=ax6,
                       fmt='.3f', cbar_kws={'label': 'Correlation'})
            ax6.set_title('Top Feature Correlations with Churn', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/churn_analysis_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Visualizations saved to {output_dir}/churn_analysis_dashboard.png")

    def print_summary(self):
        """Print comprehensive analysis summary"""
        print("\n" + "=" * 70)
        print(" " * 15 + "CUSTOMER CHURN ANALYSIS REPORT")
        print("=" * 70)

        # Overall Metrics
        if 'overall' in self.results:
            overall = self.results['overall']
            print("\n📊 OVERALL METRICS")
            print("-" * 40)
            print(f"  Total Customers: {overall['total_customers']:,}")
            print(f"  Churned Customers: {overall['churned_customers']:,} ({overall['churn_rate']*100:.1f}%)")
            print(f"  Active Customers: {overall['active_customers']:,}")
            print(f"  Monthly Revenue at Risk: ${overall['mrr_at_risk']:,.2f}")

        # Risk Factors
        if 'risk_factors' in self.results:
            print("\n⚠️  TOP CHURN RISK FACTORS")
            print("-" * 40)
            risk_df = self.results['risk_factors']
            for _, row in risk_df.iterrows():
                print(f"  {row['factor']:30} +{row['lift_pct']:.1f}% churn risk")

        # Correlations
        if 'correlations' in self.results:
            print("\n📈 TOP CORRELATED FEATURES")
            print("-" * 40)
            for i, (feature, data) in enumerate(list(self.results['correlations'].items())[:5]):
                sign = "+" if data['correlation'] > 0 else ""
                print(f"  {i+1}. {feature:30} {sign}{data['correlation']:.3f}")

        # CLV Analysis
        if 'clv' in self.results:
            clv = self.results['clv']
            print("\n💰 CUSTOMER LIFETIME VALUE")
            print("-" * 40)
            print(f"  Overall CLV: ${clv['overall_clv']:.2f}")
            print(f"  Avg Monthly Revenue: ${clv['avg_monthly_revenue']:.2f}")
            print(f"  Avg Tenure: {clv['avg_tenure_months']:.1f} months")

        print("\n" + "=" * 70)


def main():
    """Main execution function"""
    data_path = 'data/customer_data.csv'

    if not os.path.exists(data_path):
        print("Data file not found. Generating data first...")
        import generate_churn_data
        generate_churn_data.main()

    print("Loading customer data...")
    df = pd.read_csv(data_path)

    # Initialize analyzer
    analyzer = ChurnAnalyzer(df)

    # Run all analyses
    print("Running churn analysis...")
    analyzer.calculate_overall_metrics()
    analyzer.analyze_churn_by_segment('plan_type')
    analyzer.analyze_churn_by_segment('contract_type')
    analyzer.analyze_churn_by_segment('acquisition_channel')
    analyzer.cohort_analysis()
    analyzer.feature_correlation_analysis()
    analyzer.calculate_clv()
    analyzer.risk_factor_analysis()

    # Generate visualizations
    print("Generating visualizations...")
    os.makedirs('results', exist_ok=True)
    analyzer.generate_visualizations()

    # Print summary
    analyzer.print_summary()

    # Save report
    with open('results/churn_analysis_report.md', 'w') as f:
        f.write("# Customer Churn Analysis Report\n\n")
        f.write("## Executive Summary\n\n")
        f.write(f"- Total Customers Analyzed: {len(df):,}\n")
        f.write(f"- Overall Churn Rate: {df['churned'].mean()*100:.1f}%\n")
        f.write(f"- Monthly Revenue at Risk: ${df[df['churned']==1]['monthly_charge'].sum():,.2f}\n\n")

    print("\nReport saved to results/churn_analysis_report.md")


if __name__ == "__main__":
    main()
