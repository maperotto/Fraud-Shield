from typing import Dict
from src.domain.entities import FraudPrediction
from src.core.logger import setup_logger

logger = setup_logger(__name__)


class FallbackFraudDetector:
    
    def __init__(self):
        self.rules = [
            self._rule_high_amount,
            self._rule_rapid_succession,
            self._rule_new_user_large_amount
        ]
    
    def predict_with_rules(self, features: Dict[str, float], transaction_data: Dict) -> FraudPrediction:
        logger.warning("Using fallback rule-based detection - ML model unavailable")
        
        fraud_score = 0.0
        triggered_rules = []
        
        for rule in self.rules:
            score, rule_name = rule(features, transaction_data)
            fraud_score += score
            if score > 0:
                triggered_rules.append(rule_name)
        
        fraud_score = min(fraud_score, 1.0)
        
        is_fraud = fraud_score >= 0.6
        
        if fraud_score >= 0.7:
            risk_level = "HIGH"
        elif fraud_score >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        logger.info(f"Fallback decision: fraud={is_fraud}, score={fraud_score:.4f}, rules={triggered_rules}")
        
        return FraudPrediction(
            transaction_id=transaction_data.get('transaction_id', ''),
            is_fraud=is_fraud,
            confidence_score=fraud_score,
            risk_level=risk_level
        )
    
    def _rule_high_amount(self, features: Dict, transaction_data: Dict) -> tuple:
        amount = transaction_data.get('amount', 0)
        
        if amount > 5000:
            return 0.4, "high_amount"
        elif amount > 2000:
            return 0.2, "elevated_amount"
        return 0.0, None
    
    def _rule_rapid_succession(self, features: Dict, transaction_data: Dict) -> tuple:
        count_1h = features.get('count_1h', 0)
        
        if count_1h >= 10:
            return 0.5, "rapid_succession"
        elif count_1h >= 5:
            return 0.3, "frequent_transactions"
        return 0.0, None
    
    def _rule_new_user_large_amount(self, features: Dict, transaction_data: Dict) -> tuple:
        is_new_user = features.get('is_new_user', 0.0) > 0.5
        amount = transaction_data.get('amount', 0)
        
        if is_new_user and amount > 1000:
            return 0.6, "new_user_high_amount"
        return 0.0, None
