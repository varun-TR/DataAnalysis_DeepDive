"""
Customer Churn Prediction Model
Machine Learning model for predicting customer churn

Author: Data Analysis Portfolio
Skills: Machine Learning, Scikit-Learn, Feature Engineering
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve
)
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
import pickle

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')


class ChurnPredictor:
    """
    Machine Learning model for customer churn prediction
    """

    def __init__(self, data: pd.DataFrame):
        """Initialize with customer data"""
        self.data = data.copy()
        self.models = {}
        self.results = {}
        self.feature_columns = []
        self.scaler = StandardScaler()
        self.label_encoders = {}

    def prepare_features(self):
        """Prepare features for modeling"""
        # Select features
        numeric_features = [
            'tenure_months', 'monthly_charge', 'days_since_last_login',
            'login_frequency_7d', 'feature_adoption_score', 'support_tickets_30d',
            'nps_score', 'payment_failures_90d', 'total_spend'
        ]

        categorical_features = [
            'plan_type', 'contract_type', 'age_group', 'acquisition_channel'
        ]

        # Create a copy for processing
        df = self.data.copy()

        # Encode categorical variables
        for col in categorical_features:
            if col in df.columns:
                le = LabelEncoder()
                df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
                numeric_features.append(col + '_encoded')

        # Create binary flags
        df['is_monthly_billing'] = (df['billing_annual'] == 0).astype(int)
        df['is_month_to_month'] = (df['contract_type'] == 'month-to-month').astype(int)
        df['has_payment_failure'] = (df['payment_failures_90d'] > 0).astype(int)

        numeric_features.extend(['is_monthly_billing', 'is_month_to_month', 'has_payment_failure'])

        # Store feature columns
        self.feature_columns = [f for f in numeric_features if f in df.columns]

        # Prepare X and y
        X = df[self.feature_columns].fillna(0)
        y = df['churned']

        return X, y

    def train_models(self, test_size=0.2, random_state=42):
        """Train multiple models and compare performance"""
        X, y = self.prepare_features()

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Store split data
        self.X_train, self.X_test = X_train, X_test
        self.y_train, self.y_test = y_train, y_test
        self.X_train_scaled, self.X_test_scaled = X_train_scaled, X_test_scaled

        # Define models
        models_to_train = {
            'Logistic Regression': LogisticRegression(
                random_state=random_state, max_iter=1000, class_weight='balanced'
            ),
            'Random Forest': RandomForestClassifier(
                n_estimators=100, random_state=random_state,
                class_weight='balanced', n_jobs=-1
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=100, random_state=random_state
            )
        }

        # Train and evaluate each model
        for name, model in models_to_train.items():
            print(f"Training {name}...")

            # Use scaled data for logistic regression, original for tree-based
            if 'Logistic' in name:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                y_prob = model.predict_proba(X_test_scaled)[:, 1]
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_prob = model.predict_proba(X_test)[:, 1]

            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred),
                'recall': recall_score(y_test, y_pred),
                'f1': f1_score(y_test, y_pred),
                'auc_roc': roc_auc_score(y_test, y_prob),
                'confusion_matrix': confusion_matrix(y_test, y_pred)
            }

            self.models[name] = model
            self.results[name] = metrics

        return self.results

    def get_feature_importance(self, model_name='Random Forest'):
        """Get feature importance from trained model"""
        if model_name not in self.models:
            print(f"Model {model_name} not found")
            return None

        model = self.models[model_name]

        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importance = np.abs(model.coef_[0])
        else:
            return None

        # Create importance DataFrame
        importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importance
        }).sort_values('importance', ascending=False)

        return importance_df

    def identify_high_risk_customers(self, threshold=0.7, model_name='Random Forest'):
        """Identify customers at high risk of churning"""
        if model_name not in self.models:
            print(f"Model {model_name} not found")
            return None

        model = self.models[model_name]
        X, _ = self.prepare_features()

        # Get churn probabilities
        if 'Logistic' in model_name:
            X_scaled = self.scaler.transform(X)
            churn_probs = model.predict_proba(X_scaled)[:, 1]
        else:
            churn_probs = model.predict_proba(X)[:, 1]

        # Add to data
        result_df = self.data.copy()
        result_df['churn_probability_pred'] = churn_probs
        result_df['high_risk'] = (churn_probs >= threshold).astype(int)

        # Get high risk customers
        high_risk = result_df[result_df['high_risk'] == 1]

        self.results['high_risk_customers'] = {
            'count': len(high_risk),
            'total_mrr': high_risk['monthly_charge'].sum(),
            'avg_tenure': high_risk['tenure_months'].mean(),
            'data': high_risk
        }

        return high_risk

    def generate_visualizations(self, output_dir='results'):
        """Generate model evaluation visualizations"""
        os.makedirs(output_dir, exist_ok=True)

        fig, axes = plt.subplots(2, 2, figsize=(14, 12))

        # 1. Model Comparison
        ax1 = axes[0, 0]
        model_names = list(self.results.keys())
        if 'high_risk_customers' in model_names:
            model_names.remove('high_risk_customers')

        metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1', 'auc_roc']
        x = np.arange(len(metrics_to_plot))
        width = 0.25

        for i, model_name in enumerate(model_names[:3]):
            values = [self.results[model_name][m] * 100 for m in metrics_to_plot]
            ax1.bar(x + i*width, values, width, label=model_name)

        ax1.set_ylabel('Score (%)', fontsize=12)
        ax1.set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
        ax1.set_xticks(x + width)
        ax1.set_xticklabels([m.replace('_', ' ').title() for m in metrics_to_plot])
        ax1.legend()
        ax1.set_ylim(0, 100)

        # 2. ROC Curves
        ax2 = axes[0, 1]
        colors = ['#3498db', '#e74c3c', '#2ecc71']
        for i, model_name in enumerate(model_names[:3]):
            model = self.models[model_name]
            if 'Logistic' in model_name:
                y_prob = model.predict_proba(self.X_test_scaled)[:, 1]
            else:
                y_prob = model.predict_proba(self.X_test)[:, 1]

            fpr, tpr, _ = roc_curve(self.y_test, y_prob)
            auc = self.results[model_name]['auc_roc']
            ax2.plot(fpr, tpr, color=colors[i], linewidth=2,
                    label=f'{model_name} (AUC={auc:.3f})')

        ax2.plot([0, 1], [0, 1], 'k--', linewidth=1)
        ax2.set_xlabel('False Positive Rate', fontsize=12)
        ax2.set_ylabel('True Positive Rate', fontsize=12)
        ax2.set_title('ROC Curves', fontsize=14, fontweight='bold')
        ax2.legend(loc='lower right')

        # 3. Feature Importance
        ax3 = axes[1, 0]
        importance_df = self.get_feature_importance('Random Forest')
        if importance_df is not None:
            top_features = importance_df.head(10)
            y_pos = np.arange(len(top_features))
            ax3.barh(y_pos, top_features['importance'], color='#3498db', edgecolor='black')
            ax3.set_yticks(y_pos)
            ax3.set_yticklabels(top_features['feature'])
            ax3.set_xlabel('Importance', fontsize=12)
            ax3.set_title('Top 10 Feature Importance (Random Forest)', fontsize=14, fontweight='bold')
            ax3.invert_yaxis()

        # 4. Confusion Matrix (Best Model)
        ax4 = axes[1, 1]
        best_model = max(model_names, key=lambda x: self.results[x]['auc_roc'])
        cm = self.results[best_model]['confusion_matrix']
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax4,
                   xticklabels=['Active', 'Churned'],
                   yticklabels=['Active', 'Churned'])
        ax4.set_xlabel('Predicted', fontsize=12)
        ax4.set_ylabel('Actual', fontsize=12)
        ax4.set_title(f'Confusion Matrix ({best_model})', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/model_evaluation.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Visualizations saved to {output_dir}/model_evaluation.png")

    def print_summary(self):
        """Print model evaluation summary"""
        print("\n" + "=" * 70)
        print(" " * 15 + "CHURN PREDICTION MODEL RESULTS")
        print("=" * 70)

        print("\n📊 MODEL PERFORMANCE COMPARISON")
        print("-" * 60)
        print(f"{'Model':<25} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'AUC-ROC':>10}")
        print("-" * 60)

        for model_name, metrics in self.results.items():
            if model_name == 'high_risk_customers':
                continue
            print(f"{model_name:<25} {metrics['accuracy']*100:>9.1f}% "
                  f"{metrics['precision']*100:>9.1f}% {metrics['recall']*100:>9.1f}% "
                  f"{metrics['auc_roc']:>10.3f}")

        # Best model
        model_names = [k for k in self.results.keys() if k != 'high_risk_customers']
        best_model = max(model_names, key=lambda x: self.results[x]['auc_roc'])
        print(f"\n✅ Best Model: {best_model} (AUC-ROC: {self.results[best_model]['auc_roc']:.3f})")

        # Feature importance
        print("\n📈 TOP PREDICTIVE FEATURES")
        print("-" * 40)
        importance_df = self.get_feature_importance('Random Forest')
        if importance_df is not None:
            for i, row in importance_df.head(5).iterrows():
                print(f"  {row['feature']:30} {row['importance']:.4f}")

        # High risk customers
        if 'high_risk_customers' in self.results:
            hr = self.results['high_risk_customers']
            print("\n⚠️  HIGH RISK CUSTOMERS IDENTIFIED")
            print("-" * 40)
            print(f"  Count: {hr['count']:,}")
            print(f"  Monthly Revenue at Risk: ${hr['total_mrr']:,.2f}")
            print(f"  Avg Tenure: {hr['avg_tenure']:.1f} months")

        print("\n" + "=" * 70)

    def save_model(self, model_name='Random Forest', output_dir='results'):
        """Save trained model to file"""
        os.makedirs(output_dir, exist_ok=True)

        if model_name not in self.models:
            print(f"Model {model_name} not found")
            return

        model_data = {
            'model': self.models[model_name],
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'label_encoders': self.label_encoders
        }

        filepath = f'{output_dir}/churn_model.pkl'
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"Model saved to {filepath}")


def main():
    """Main execution function"""
    data_path = 'data/customer_data.csv'

    if not os.path.exists(data_path):
        print("Data file not found. Generating data first...")
        import generate_churn_data
        generate_churn_data.main()

    print("Loading customer data...")
    df = pd.read_csv(data_path)

    # Initialize predictor
    predictor = ChurnPredictor(df)

    # Train models
    print("\nTraining models...")
    predictor.train_models()

    # Identify high risk customers
    print("\nIdentifying high-risk customers...")
    predictor.identify_high_risk_customers(threshold=0.7)

    # Generate visualizations
    print("\nGenerating visualizations...")
    os.makedirs('results', exist_ok=True)
    predictor.generate_visualizations()

    # Print summary
    predictor.print_summary()

    # Save best model
    predictor.save_model('Random Forest')

    print("\nChurn prediction model training complete!")


if __name__ == "__main__":
    main()
