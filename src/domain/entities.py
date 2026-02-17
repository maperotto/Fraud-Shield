from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    transaction_id: str
    amount: float
    timestamp: datetime
    merchant_category: str
    location: str
    user_id: str
    
    def to_dict(self) -> dict:
        return {
            'transaction_id': self.transaction_id,
            'amount': self.amount,
            'timestamp': self.timestamp.isoformat(),
            'merchant_category': self.merchant_category,
            'location': self.location,
            'user_id': self.user_id
        }


@dataclass
class FraudPrediction:
    transaction_id: str
    is_fraud: bool
    confidence_score: float
    risk_level: str
    
    def to_dict(self) -> dict:
        return {
            'transaction_id': self.transaction_id,
            'is_fraud': self.is_fraud,
            'confidence_score': round(self.confidence_score, 4),
            'risk_level': self.risk_level
        }
