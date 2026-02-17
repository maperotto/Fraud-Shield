from flask import Flask
from src.entrypoints.config import Config
from src.entrypoints.routes import analyze_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.register_blueprint(analyze_bp)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return {
            'status': 'healthy',
            'service': 'fraud-shield',
            'version': '1.0.0'
        }, 200
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['FLASK_DEBUG']
    )
