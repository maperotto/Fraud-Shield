import pandas as pd
from src.core.feature_engineering import FeatureExtractor
from src.core.fraud_detector import FraudDetector


def train_model():
    print("Loading transaction data...")
    df = pd.read_csv('data/transactions.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print(f"Total transactions: {len(df)}")
    print(f"Fraud cases: {df['is_fraud'].sum()}")
    
    print("\nExtracting features...")
    extractor = FeatureExtractor()
    features_df = extractor.prepare_training_data(df)
    
    print(f"Features extracted: {len(features_df.columns) - 1}")
    
    print("\nTraining model...")
    detector = FraudDetector()
    detector.train(features_df)
    
    print("\nSaving model...")
    detector.save_model('models/fraud_detector.pkl')
    
    print("Model training completed successfully!")


if __name__ == "__main__":
    train_model()
