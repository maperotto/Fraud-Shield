import requests
import random
import time
from datetime import datetime, timedelta
import json


class TransactionStreamSimulator:
    
    def __init__(self, api_url: str = 'http://localhost:5000'):
        self.api_url = api_url
        self.transaction_counter = 0
        
        self.users = [f"user_{i:04d}" for i in range(50)]
        
        self.categories = [
            'groceries', 'restaurants', 'gas_station', 'online_shopping',
            'entertainment', 'utilities', 'healthcare', 'travel', 'electronics'
        ]
        
        self.locations = [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
            'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'Austin',
            'Miami', 'Seattle', 'Boston', 'Denver', 'Atlanta'
        ]
    
    def generate_transaction(self) -> dict:
        self.transaction_counter += 1
        user_id = random.choice(self.users)
        
        is_fraud_simulation = random.random() < 0.08
        
        if is_fraud_simulation:
            amount = random.uniform(800, 4000)
            category = random.choice(self.categories)
            location = random.choice(self.locations)
        else:
            hour = datetime.now().hour
            if 9 <= hour <= 22:
                amount = abs(random.normalvariate(120, 60))
            else:
                amount = abs(random.normalvariate(40, 25))
            
            amount = max(5, min(amount, 800))
            category = random.choices(
                self.categories,
                weights=[0.25, 0.20, 0.15, 0.15, 0.10, 0.05, 0.05, 0.03, 0.02]
            )[0]
            location = random.choice(self.locations[:8])
        
        transaction = {
            'transaction_id': f"stream_tx_{self.transaction_counter:08d}",
            'user_id': user_id,
            'amount': round(amount, 2),
            'timestamp': datetime.now().isoformat(),
            'merchant_category': category,
            'location': location
        }
        
        return transaction
    
    def send_transaction(self, transaction: dict) -> dict:
        try:
            response = requests.post(
                f"{self.api_url}/v1/analyze",
                json=transaction,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f"Status {response.status_code}", 'details': response.text}
                
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            return {'error': 'Connection failed - Is the API running?'}
        except Exception as e:
            return {'error': str(e)}
    
    def run_stream(self, duration_seconds: int = 60, transactions_per_second: float = 1.0):
        print(f"Starting transaction stream simulation...")
        print(f"Target: {transactions_per_second} tx/sec for {duration_seconds} seconds")
        print(f"API endpoint: {self.api_url}")
        print("-" * 80)
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        total_sent = 0
        total_frauds_detected = 0
        total_errors = 0
        
        interval = 1.0 / transactions_per_second
        
        while time.time() < end_time:
            iteration_start = time.time()
            
            transaction = self.generate_transaction()
            result = self.send_transaction(transaction)
            
            total_sent += 1
            
            if 'error' in result:
                total_errors += 1
                status_symbol = '❌'
                status_text = f"ERROR: {result['error']}"
            else:
                is_fraud = result.get('is_fraud', False)
                confidence = result.get('confidence_score', 0)
                risk = result.get('risk_level', 'UNKNOWN')
                
                if is_fraud:
                    total_frauds_detected += 1
                    status_symbol = '🚨'
                    status_text = f"FRAUD | Risk: {risk} | Confidence: {confidence:.3f}"
                else:
                    status_symbol = '✅'
                    status_text = f"LEGIT | Risk: {risk} | Confidence: {confidence:.3f}"
            
            print(f"{status_symbol} TX {total_sent:04d} | ${transaction['amount']:>8.2f} | "
                  f"{transaction['user_id']:12s} | {status_text}")
            
            elapsed = time.time() - iteration_start
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)
        
        total_duration = time.time() - start_time
        actual_tps = total_sent / total_duration
        fraud_rate = (total_frauds_detected / total_sent * 100) if total_sent > 0 else 0
        
        print("-" * 80)
        print(f"\n📊 Simulation Complete")
        print(f"   Duration: {total_duration:.2f}s")
        print(f"   Transactions Sent: {total_sent}")
        print(f"   Actual TPS: {actual_tps:.2f}")
        print(f"   Frauds Detected: {total_frauds_detected} ({fraud_rate:.1f}%)")
        print(f"   Errors: {total_errors}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fraud Shield Transaction Stream Simulator')
    parser.add_argument('--url', default='http://localhost:5000', help='API base URL')
    parser.add_argument('--duration', type=int, default=30, help='Duration in seconds')
    parser.add_argument('--tps', type=float, default=2.0, help='Transactions per second')
    
    args = parser.parse_args()
    
    simulator = TransactionStreamSimulator(api_url=args.url)
    
    try:
        simulator.run_stream(
            duration_seconds=args.duration,
            transactions_per_second=args.tps
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Stream simulation interrupted by user")


if __name__ == '__main__':
    main()
