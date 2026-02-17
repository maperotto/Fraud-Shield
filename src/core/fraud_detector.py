import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Dict
from src.domain.entities import FraudPrediction
from src.domain.interfaces import IFraudDetector


class FraudDetector(IFraudDetector):
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=4,
            class_weight='balanced',
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
    
    def train(self, data: pd.DataFrame) -> None:
        if 'is_fraud' not in data.columns:
            raise ValueError("Training data must contain 'is_fraud' column")
        
        X = data.drop('is_fraud', axis=1)
        y = data['is_fraud']
        
        self.feature_names = list(X.columns)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model.fit(X_train_scaled, y_train)
        
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"Training accuracy: {train_score:.4f}")
        print(f"Test accuracy: {test_score:.4f}")
        
        self.is_trained = True
    
    def predict(self, features: Dict[str, float]) -> FraudPrediction:
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        feature_df = pd.DataFrame([features])[self.feature_names]
        
        feature_scaled = self.scaler.transform(feature_df)
        
        prediction = self.model.predict(feature_scaled)[0]
        probability = self.model.predict_proba(feature_scaled)[0]
        
        confidence_score = probability[1]
        
        if confidence_score >= 0.7:
            risk_level = "HIGH"
        elif confidence_score >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return FraudPrediction(
            transaction_id="",
            is_fraud=bool(prediction),
            confidence_score=float(confidence_score),
            risk_level=risk_level
        )
    
    def save_model(self, path: str) -> None:
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, path: str) -> None:
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
