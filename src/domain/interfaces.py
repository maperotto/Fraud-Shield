from abc import ABC, abstractmethod
from typing import List
import pandas as pd
from src.domain.entities import Transaction, FraudPrediction


class IFeatureExtractor(ABC):
    
    @abstractmethod
    def extract_features(self, transaction: Transaction, history: pd.DataFrame) -> dict:
        pass


class IFraudDetector(ABC):
    
    @abstractmethod
    def predict(self, features: dict) -> FraudPrediction:
        pass
    
    @abstractmethod
    def train(self, data: pd.DataFrame) -> None:
        pass
    
    @abstractmethod
    def save_model(self, path: str) -> None:
        pass
    
    @abstractmethod
    def load_model(self, path: str) -> None:
        pass


class ITransactionRepository(ABC):
    
    @abstractmethod
    def get_user_history(self, user_id: str, limit: int) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def save_transaction(self, transaction: Transaction) -> None:
        pass
