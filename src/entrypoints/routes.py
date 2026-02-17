from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from pydantic import ValidationError
from src.entrypoints.schemas import TransactionRequest, FraudAnalysisResponse
from src.domain.entities import Transaction
from src.core.fraud_detector import FraudDetector
from src.core.feature_engineering import FeatureExtractor
from src.core.repository import InMemoryTransactionRepository
from src.core.dashboard import DashboardGenerator
from src.core.logger import setup_logger
from src.core.exceptions import ModelNotTrainedException, InvalidTransactionException
import os

analyze_bp = Blueprint('analyze', __name__)

logger = setup_logger(__name__)

detector = FraudDetector()
extractor = FeatureExtractor()
repository = InMemoryTransactionRepository()
dashboard_gen = DashboardGenerator()

model_path = os.getenv('MODEL_PATH', 'models/fraud_detector.pkl')
if os.path.exists(model_path):
    detector.load_model(model_path)
    logger.info(f"Model loaded successfully from {model_path}")
else:
    logger.warning(f"Model not found at {model_path}")


@analyze_bp.route('/v1/analyze', methods=['POST'])
def analyze_transaction():
    try:
        data = request.get_json()
        logger.info(f"Received analysis request for transaction: {data.get('transaction_id', 'unknown')}")
        
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
        logger.debug(f"Retrieved {len(history)} historical transactions for user {transaction.user_id}")
        
        features = extractor.extract_features(transaction, history)
        
        prediction = detector.predict(features)
        prediction.transaction_id = transaction.transaction_id
        
        logger.info(
            f"Analysis complete: {transaction.transaction_id} - "
            f"Fraud={prediction.is_fraud}, Score={prediction.confidence_score:.4f}, "
            f"Risk={prediction.risk_level}"
        )
        
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
        logger.warning(f"Validation error: {e.errors()}")
        return jsonify({
            'error': 'Validation failed',
            'details': e.errors()
        }), 400
    
    except ValueError as e:
        logger.info("Generating fraud analysis dashboard")
        chart_path = dashboard_gen.generate_fraud_analysis_chart()
        logger.info(f"Dashboard generated successfully: {chart_path}")
        
        return send_file(
            chart_path,
            mimetype='image/png',
            as_attachment=True,
            download_name='fraud_analysis_dashboard.png'
        )
        
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {str(e)}")
        return jsonify({
            'error': 'Data not found',
            'message': str(e)
        }), 404
        
    except Exception as e:
        logger.error(f"Dashboard generation failed: {str(e)}", exc_info=True)
    try:
        chart_path = dashboard_gen.generate_fraud_analysis_chart()
        
        return send_file(
            chart_path,
            mimetype='image/png',
            as_attachment=True,
            download_name='fraud_analysis_dashboard.png'
        )
        
    except FileNotFoundError as e:
        return jsonify({
            'error': 'Data not found',
            'message': str(e)
        }), 404
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate dashboard',
            'message': str(e)
        }), 500
