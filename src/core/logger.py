import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, log_level: str = 'INFO') -> logging.Logger:
    logger = logging.getLogger(name)
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    os.makedirs('logs', exist_ok=True)
    file_handler = RotatingFileHandler(
        'logs/fraud_shield.log',
        maxBytes=10485760,
        backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
