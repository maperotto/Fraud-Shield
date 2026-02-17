import pandas as pd
import os
from typing import Dict
from src.domain.entities import Transaction
from src.domain.interfaces import ITransactionRepository


class InMemoryTransactionRepository(ITransactionRepository):
    
    def __init__(self):
        self.transactions: pd.DataFrame = pd.DataFrame()
        self._load_from_file()
    
    def _load_from_file(self) -> None:
        file_path = 'data/transactions.csv'
        if os.path.exists(file_path):
            self.transactions = pd.read_csv(file_path)
            self.transactions['timestamp'] = pd.to_datetime(self.transactions['timestamp'])
    
    def get_user_history(self, user_id: str, limit: int = 100) -> pd.DataFrame:
        user_transactions = self.transactions[
            self.transactions['user_id'] == user_id
        ].sort_values('timestamp', ascending=False).head(limit)
        
        return user_transactions
    
    def save_transaction(self, transaction: Transaction) -> None:
        new_row = pd.DataFrame([{
            'transaction_id': transaction.transaction_id,
            'amount': transaction.amount,
            'timestamp': transaction.timestamp,
            'merchant_category': transaction.merchant_category,
            'location': transaction.location,
            'user_id': transaction.user_id
        }])
        
        self.transactions = pd.concat([self.transactions, new_row], ignore_index=True)
