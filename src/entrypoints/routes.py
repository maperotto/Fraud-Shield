from flask import Blueprint, request, jsonify
from datetime import datetime
from pydantic import ValidationError
from src.entrypoints.schemas import TransactionRequest, FraudAnalysisResponse
from src.domain.entities import Transaction
from src.core.fraud_detector import FraudDetector
from src.core.feature_engineering import FeatureExtractor
from src.core.repository import InMemoryTransactionRepository
import os

analyze_bp = Blueprint('analyze', __name__)

detector = FraudDetector()
extractor = FeatureExtractor()
repository = InMemoryTransactionRepository()

model_path = os.getenv('MODEL_PATH', 'models/fraud_detector.pkl')
if os.path.exists(model_path):
    detector.load_model(model_path)


@analyze_bp.route('/v1/analyze', methods=['POST'])
def analyze_transaction():
    try:
        data = request.get_json()
        
        transaction_req = TransactionRequest(**data)
        
        transaction = Transaction(
            transaction_id=transaction_req.transaction_id,
            amount=transaction_req.amount,
            timestamp=datetime.fromisoformat(transaction_req.timestamp.replace('Z', '+00:00')),
            merchant_category=transaction_req.merchant_category,
            location=transaction_req.location,
            user_id=transaction_req.user_id
        )
        
        history = repository.get_user_history(transaction.user_id, limit=100)
        
        features = extractor.extract_features(transaction, history)
        
        prediction = detector.predict(features)
        prediction.transaction_id = transaction.transaction_id
        
        repository.save_transaction(transaction)
        
        response = FraudAnalysisResponse(
            transaction_id=prediction.transaction_id,
            is_fraud=prediction.is_fraud,
            confidence_score=prediction.confidence_score,
            risk_level=prediction.risk_level,
            analysis_timestamp=datetime.now().isoformat()
        )
        
        return jsonify(response.model_dump()), 200
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation failed',
            'details': e.errors()
        }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500
