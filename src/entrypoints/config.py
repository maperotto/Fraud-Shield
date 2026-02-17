import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/fraud_detector.pkl')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
