from flask import Flask, jsonify
from flask_cors import CORS
from src.entrypoints.config import Config
from src.entrypoints.routes import analyze_bp
from src.core.logger import setup_logger
from src.infrastructure.database import FraudDatabase
import os

logger = setup_logger(__name__)


def create_app() -> Flask:
    # Configure Flask with correct template and static folders
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    app = Flask(__name__,
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(Config)
    
    CORS(app, resources={
        r"/v1/*": {
            "origins": "*",
            "methods": ["GET", "POST"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    app.register_blueprint(analyze_bp)
    
    logger.info("Fraud Shield API initialized")
    
    @app.route('/health', methods=['GET'])
    def health_check():
        health_status = {
            'status': 'healthy',
            'service': 'fraud-shield',
            'version': '1.0.0'
        }
        
        try:
            db = FraudDatabase()
            stats = db.get_total_stats()
            health_status['database'] = 'connected'
            health_status['total_analyzed'] = stats.get('total_analyzed', 0)
        except Exception as e:
            health_status['database'] = 'error'
            health_status['database_error'] = str(e)
            return jsonify(health_status), 503
        
        model_path = os.getenv('MODEL_PATH', 'models/fraud_detector.pkl')
        health_status['model_loaded'] = os.path.exists(model_path)
        
        return jsonify(health_status), 200
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['FLASK_DEBUG']
    )
