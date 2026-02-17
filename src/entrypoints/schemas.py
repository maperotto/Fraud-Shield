from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class TransactionRequest(BaseModel):
    transaction_id: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    timestamp: str
    merchant_category: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1, max_length=100)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Invalid timestamp format. Use ISO 8601 format')
    
    @validator('amount')
    def validate_amount(cls, v):
        if v > 1000000:
            raise ValueError('Amount exceeds maximum allowed value')
        return v


class FraudAnalysisResponse(BaseModel):
    transaction_id: str
    is_fraud: bool
    confidence_score: float
    risk_level: str
    analysis_timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "tx_00001234",
                "is_fraud": False,
                "confidence_score": 0.1234,
                "risk_level": "LOW",
                "analysis_timestamp": "2024-01-15T10:30:00"
            }
        }
