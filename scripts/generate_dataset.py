import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def generate_synthetic_dataset(n_samples: int = 10000) -> pd.DataFrame:
    np.random.seed(42)
    random.seed(42)
    
    n_users = 500
    user_ids = [f"user_{i:04d}" for i in range(n_users)]
    
    categories = [
        'groceries', 'restaurants', 'gas_station', 'online_shopping',
        'entertainment', 'utilities', 'healthcare', 'travel'
    ]
    
    locations = [
        'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
        'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'Austin'
    ]
    
    data = []
    
    start_date = datetime.now() - timedelta(days=180)
    
    for i in range(n_samples):
        user_id = random.choice(user_ids)
        timestamp = start_date + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        is_fraud = 0
        
        if random.random() < 0.05:
            is_fraud = 1
            amount = random.uniform(500, 5000)
            category = random.choice(categories)
            location = random.choice(locations)
        else:
            hour = timestamp.hour
            if 6 <= hour <= 22:
                amount = random.normalvariate(75, 50)
            else:
                amount = random.normalvariate(30, 20)
            
            amount = max(1, min(amount, 1000))
            
            category = random.choice(categories)
            location = random.choice(locations[:5])
        
        data.append({
            'transaction_id': f"tx_{i:08d}",
            'user_id': user_id,
            'amount': round(amount, 2),
            'timestamp': timestamp,
            'merchant_category': category,
            'location': location,
            'is_fraud': is_fraud
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df


if __name__ == "__main__":
    print("Generating synthetic transaction dataset...")
    df = generate_synthetic_dataset(10000)
    
    df.to_csv('data/transactions.csv', index=False)
    print(f"Dataset created with {len(df)} transactions")
    print(f"Fraud cases: {df['is_fraud'].sum()} ({df['is_fraud'].mean()*100:.2f}%)")
    print("\nSample data:")
    print(df.head(10))
