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
from src.core.rate_limiter import rate_limit
from src.core.decorators import timing_decorator
from src.infrastructure.database import FraudDatabase
from src.infrastructure.feature_store import FeatureStore
from src.infrastructure.fallback import FallbackFraudDetector
from src.infrastructure.report_generator import ReportGenerator
import os

analyze_bp = Blueprint('analyze', __name__)

logger = setup_logger(__name__)

detector = FraudDetector()
extractor = FeatureExtractor()
repository = InMemoryTransactionRepository()
dashboard_gen = DashboardGenerator()
database = FraudDatabase()
feature_store = FeatureStore(database)
fallback_detector = FallbackFraudDetector()
report_gen = ReportGenerator(database)

model_loaded = False
model_path = os.getenv('MODEL_PATH', 'models/fraud_detector.pkl')
if os.path.exists(model_path):
    try:
        detector.load_model(model_path)
        model_loaded = True
        logger.info(f"Model loaded successfully from {model_path}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        logger.warning("Will use fallback rule-based detection")
else:
    logger.warning(f"Model not found at {model_path}, using fallback detection")


@analyze_bp.route('/v1/analyze', methods=['POST'])
@rate_limit
@timing_decorator
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
        
        store_features = feature_store.get_user_features(transaction.user_id)
        risk_indicators = feature_store.calculate_risk_indicators(
            transaction.user_id,
            transaction.amount
        )
        features.update(risk_indicators)
        
        transaction_data = {
            'transaction_id': transaction.transaction_id,
            'user_id': transaction.user_id,
            'amount': transaction.amount,
            'merchant_category': transaction.merchant_category,
            'location': transaction.location
        }
        
        if model_loaded:
            try:
                prediction = detector.predict(features)
                prediction.transaction_id = transaction.transaction_id
            except Exception as e:
                logger.error(f"ML model prediction failed: {e}, using fallback")
                prediction = fallback_detector.predict_with_rules(features, transaction_data)
        else:
            prediction = fallback_detector.predict_with_rules(features, transaction_data)
        
        logger.info(
            f"Analysis complete: {transaction.transaction_id} - "
            f"Fraud={prediction.is_fraud}, Score={prediction.confidence_score:.4f}, "
            f"Risk={prediction.risk_level}"
        )
        
        analysis_record = {
            'transaction_id': transaction.transaction_id,
            'user_id': transaction.user_id,
            'amount': transaction.amount,
            'merchant_category': transaction.merchant_category,
            'location': transaction.location,
            'timestamp': transaction.timestamp.isoformat(),
            'is_fraud': prediction.is_fraud,
            'confidence_score': prediction.confidence_score,
            'risk_level': prediction.risk_level,
            'analysis_timestamp': datetime.now().isoformat(),
            'features': features
        }
        
        database.save_analysis(analysis_record)
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
        logger.error(f"Value error during analysis: {str(e)}")
        return jsonify({
            'error': 'Model error',
            'message': str(e)
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@analyze_bp.route('/v1/dashboard', methods=['GET'])
def get_dashboard():
    try:
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
        return jsonify({
            'error': 'Failed to generate dashboard',
            'message': str(e)
        }), 500


@analyze_bp.route('/v1/report', methods=['GET'])
def get_incident_report():
    try:
        logger.info("Generating incident report")
        report_path = report_gen.generate_incident_report()
        logger.info(f"Report generated successfully: {report_path}")
        
        return send_file(
            report_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'fraud_incident_report_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to generate report',
            'message': str(e)
        }), 500


@analyze_bp.route('/v1/stats', methods=['GET'])
def get_statistics():
    try:
        stats = database.get_total_stats()
        
        return jsonify({
            'total_analyzed': stats.get('total_analyzed', 0),
            'total_frauds': stats.get('total_frauds', 0),
            'fraud_rate': round(stats.get('total_frauds', 0) / max(stats.get('total_analyzed', 1), 1) * 100, 2),
            'total_fraud_amount': round(stats.get('total_fraud_amount', 0), 2),
            'avg_confidence': round(stats.get('avg_confidence', 0), 4)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to retrieve statistics: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve statistics',
            'message': str(e)
        }), 500
