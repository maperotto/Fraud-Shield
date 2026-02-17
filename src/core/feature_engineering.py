import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict
from src.domain.entities import Transaction
from src.domain.interfaces import IFeatureExtractor


class FeatureExtractor(IFeatureExtractor):
    
    def extract_features(self, transaction: Transaction, history: pd.DataFrame) -> Dict[str, float]:
        features = {}
        
        features['amount'] = transaction.amount
        features['hour'] = transaction.timestamp.hour
        features['day_of_week'] = transaction.timestamp.weekday()
        features['is_weekend'] = 1 if transaction.timestamp.weekday() >= 5 else 0
        
        if len(history) > 0:
            features['avg_amount'] = history['amount'].mean()
            features['std_amount'] = history['amount'].std() if len(history) > 1 else 0
            features['transaction_count'] = len(history)
            
            amount_deviation = abs(transaction.amount - features['avg_amount'])
            features['amount_deviation'] = amount_deviation
            
            recent_24h = history[
                history['timestamp'] > (transaction.timestamp - timedelta(hours=24))
            ]
            features['count_24h'] = len(recent_24h)
            
            recent_1h = history[
                history['timestamp'] > (transaction.timestamp - timedelta(hours=1))
            ]
            features['count_1h'] = len(recent_1h)
            
            same_location = history[history['location'] == transaction.location]
            features['location_frequency'] = len(same_location) / len(history) if len(history) > 0 else 0
            
            same_category = history[history['merchant_category'] == transaction.merchant_category]
            features['category_frequency'] = len(same_category) / len(history) if len(history) > 0 else 0
            
            if len(history) > 0:
                time_diffs = []
                sorted_history = history.sort_values('timestamp')
                for i in range(1, len(sorted_history)):
                    diff = (sorted_history.iloc[i]['timestamp'] - sorted_history.iloc[i-1]['timestamp']).total_seconds()
                    time_diffs.append(diff)
                features['avg_time_between_tx'] = np.mean(time_diffs) if time_diffs else 0
            else:
                features['avg_time_between_tx'] = 0
        else:
            features['avg_amount'] = transaction.amount
            features['std_amount'] = 0
            features['transaction_count'] = 0
            features['amount_deviation'] = 0
            features['count_24h'] = 0
            features['count_1h'] = 0
            features['location_frequency'] = 0
            features['category_frequency'] = 0
            features['avg_time_between_tx'] = 0
        
        return features
    
    def prepare_training_data(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        feature_list = []
        
        for idx, row in transactions_df.iterrows():
            transaction = Transaction(
                transaction_id=row['transaction_id'],
                amount=row['amount'],
                timestamp=row['timestamp'],
                merchant_category=row['merchant_category'],
                location=row['location'],
                user_id=row['user_id']
            )
            
            history = transactions_df[
                (transactions_df['user_id'] == row['user_id']) & 
                (transactions_df['timestamp'] < row['timestamp'])
            ]
            
            features = self.extract_features(transaction, history)
            features['is_fraud'] = row.get('is_fraud', 0)
            feature_list.append(features)
        
        return pd.DataFrame(feature_list)
