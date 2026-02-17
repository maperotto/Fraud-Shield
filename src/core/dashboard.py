import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime


class DashboardGenerator:
    
    def __init__(self, output_dir: str = 'data'):
        self.output_dir = output_dir
        
    def generate_fraud_analysis_chart(self, transactions_path: str = 'data/transactions.csv') -> str:
        if not os.path.exists(transactions_path):
            raise FileNotFoundError(f"Transaction data not found at {transactions_path}")
        
        df = pd.read_csv(transactions_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Fraud Shield - Transaction Analysis Dashboard', fontsize=16, fontweight='bold')
        
        fraud_counts = df['is_fraud'].value_counts()
        colors = ['#2ecc71', '#e74c3c']
        axes[0, 0].pie(
            fraud_counts.values,
            labels=['Legitimate', 'Fraud'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        axes[0, 0].set_title('Transaction Distribution')
        
        df['hour'] = df['timestamp'].dt.hour
        hourly_fraud = df.groupby(['hour', 'is_fraud']).size().unstack(fill_value=0)
        hourly_fraud.plot(kind='bar', ax=axes[0, 1], color=colors, width=0.8)
        axes[0, 1].set_title('Fraud Cases by Hour of Day')
        axes[0, 1].set_xlabel('Hour')
        axes[0, 1].set_ylabel('Count')
        axes[0, 1].legend(['Legitimate', 'Fraud'])
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        fraud_amounts = df[df['is_fraud'] == 1]['amount']
        legit_amounts = df[df['is_fraud'] == 0]['amount']
        
        axes[1, 0].hist([legit_amounts, fraud_amounts], bins=30, color=colors, label=['Legitimate', 'Fraud'], alpha=0.7)
        axes[1, 0].set_title('Amount Distribution')
        axes[1, 0].set_xlabel('Transaction Amount')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].legend()
        axes[1, 0].grid(axis='y', alpha=0.3)
        
        category_fraud = df.groupby('merchant_category')['is_fraud'].agg(['sum', 'count'])
        category_fraud['rate'] = (category_fraud['sum'] / category_fraud['count'] * 100).round(2)
        category_fraud = category_fraud.sort_values('rate', ascending=False)
        
        axes[1, 1].barh(category_fraud.index, category_fraud['rate'], color='#3498db')
        axes[1, 1].set_title('Fraud Rate by Category')
        axes[1, 1].set_xlabel('Fraud Rate (%)')
        axes[1, 1].grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(self.output_dir, f'dashboard_{timestamp}.png')
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
