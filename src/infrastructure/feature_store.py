from typing import Dict, Optional
from src.infrastructure.database import FraudDatabase


class FeatureStore:
    
    def __init__(self, database: FraudDatabase):
        self.db = database
    
    def get_user_features(self, user_id: str) -> Dict[str, float]:
        stats = self.db.get_user_stats(user_id)
        
        if not stats:
            return {
                'historical_avg_amount': 0.0,
                'historical_transaction_count': 0,
                'historical_fraud_rate': 0.0,
                'user_exists': False
            }
        
        fraud_rate = 0.0
        if stats['total_transactions'] > 0:
            fraud_rate = stats['fraud_count'] / stats['total_transactions']
        
        return {
            'historical_avg_amount': stats['avg_amount'] or 0.0,
            'historical_transaction_count': stats['total_transactions'],
            'historical_fraud_rate': fraud_rate,
            'user_exists': True
        }
    
    def calculate_risk_indicators(self, user_id: str, current_amount: float) -> Dict[str, float]:
        features = self.get_user_features(user_id)
        
        if not features['user_exists']:
            return {
                'amount_deviation_ratio': 0.0,
                'is_new_user': 1.0,
                'user_trust_score': 0.5
            }
        
        avg = features['historical_avg_amount']
        deviation_ratio = 0.0
        if avg > 0:
            deviation_ratio = abs(current_amount - avg) / avg
        
        fraud_rate = features['historical_fraud_rate']
        trust_score = max(0.0, min(1.0, 1.0 - fraud_rate))
        
        return {
            'amount_deviation_ratio': deviation_ratio,
            'is_new_user': 0.0,
            'user_trust_score': trust_score
        }
