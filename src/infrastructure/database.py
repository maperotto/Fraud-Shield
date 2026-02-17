import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os
from contextlib import contextmanager


class FraudDatabase:
    
    def __init__(self, db_path: str = 'data/fraud_shield.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_tables()
        self._optimize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        return conn
    
    @contextmanager
    def _transaction(self):
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _create_tables(self) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fraud_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL UNIQUE,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                merchant_category TEXT,
                location TEXT,
                timestamp TEXT NOT NULL,
                is_fraud BOOLEAN NOT NULL,
                confidence_score REAL NOT NULL CHECK(confidence_score >= 0 AND confidence_score <= 1),
                risk_level TEXT NOT NULL CHECK(risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
                analysis_timestamp TEXT NOT NULL,
                model_version TEXT DEFAULT 'v1.0',
                features TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_statistics (
                user_id TEXT PRIMARY KEY,
                total_transactions INTEGER DEFAULT 0 CHECK(total_transactions >= 0),
                total_amount REAL DEFAULT 0.0 CHECK(total_amount >= 0),
                avg_amount REAL DEFAULT 0.0 CHECK(avg_amount >= 0),
                fraud_count INTEGER DEFAULT 0 CHECK(fraud_count >= 0),
                last_transaction_date TEXT,
                updated_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_id ON fraud_analysis(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON fraud_analysis(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_is_fraud ON fraud_analysis(is_fraud)
        ''')
        
        cursor.execute('''
            if analysis_data['amount'] < 0:
                raise ValueError("Amount cannot be negative")
            
            if not 0 <= analysis_data['confidence_score'] <= 1:
                raise ValueError("Confidence score must be between 0 and 1")
            
            if analysis_data['risk_level'] not in ['LOW', 'MEDIUM', 'HIGH']:
                raise ValueError("Invalid risk level")
            
            with self._transaction() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO fraud_analysis 
                    (transaction_id, user_id, amount, merchant_category, location, 
                     timestamp, is_fraud, confidence_score, risk_level, 
                     analysis_timestamp, features)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    analysis_data['transaction_id'],
                    analysis_data['user_id'],
                    analysis_data['amount'],
                    analysis_data.get('merchant_category'),
                    analysis_data.get('location'),
                    analysis_data['timestamp'],
                    analysis_data['is_fraud'],
                    analysis_data['confidence_score'],
                    analysis_data['risk_level'],
                    analysis_data['analysis_timestamp'],
                    str(analysis_data.get('features', {}))
                ))
                
                self._update_user_statistics(
                    cursor,
                    analysis_data['user_id'],
                    analysis_data['amount'],
                    analysis_data['is_fraud']
                )
            
            return True
            
        except ValueError as e:
            raise e    analysis_data['confidence_score'],
                analysis_data['risk_level'],
                analysis_data['analysis_timestamp'],
                str(analysis_data.get('features', {}))
            ))
            
            self._update_user_statistics(
                cursor,
                analysis_data['user_id'],
                analysis_data['amount'],
                analysis_data['is_fraud']
            )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Database error: {e}")
            return False
    
    def _update_user_statistics(self, cursor, user_id: str, amount: float, is_fraud: bool) -> None:
        cursor.execute('''
            INSERT INTO user_statistics (user_id, total_transactions, total_amount, 
                                        fraud_count, updated_at)
            VALUES (?, 1, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                total_transactions = total_transactions + 1,
                total_amount = total_amount + ?,
                fraud_count = fraud_count + ?,
                updated_at = ?
        ''', (
            user_id,
            amount,
            1 if is_fraud else 0,
            datetime.now().isoformat(),
            amount,
            1 if is_fraud else 0,
            datetime.now().isoformat()
        ))
        
        cursor.execute('''
            UPDATE user_statistics 
            SET avg_amount = total_amount / total_transactions
            WHERE user_id = ?
        ''', (user_id,))
    
    def get_user_stats(self, user_id: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_statistics WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_fraud_count_by_hour(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(*) as total,
                SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) as fraud_count
            FROM fraud_analysis
            GROUP BY hour
            ORDER BY hour
        ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_recent_frauds(self, limit: int = 100) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM fraud_analysis 
            WHERE is_fraud = 1
            ORDER BY analysis_timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_total_stats(self) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_analyzed,
                SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) as total_frauds,
                AVG(confidence_score) as avg_confidence,
                SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END) as total_fraud_amount
            FROM fraud_analysis
        ''')
        
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}
