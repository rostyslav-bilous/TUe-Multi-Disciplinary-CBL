import numpy as np
import pandas as pd

def generate_mock_pwcs(num_lsoas=30, seed=123):
    
    np.random.seed(seed)
    lsoa_ids = [f'LSOA_{i}' for i in range(num_lsoas)]
    pwc_x = np.random.uniform(500000, 515000, num_lsoas) # 15x15km grid
    pwc_y = np.random.uniform(180000, 195000, num_lsoas)
    
    weights = np.random.choice(
        [0.05, 0.2, 0.8], 
        size=num_lsoas, 
        p=[0.45,0.35,0.2] 
    )

    speed_limits = np.full(num_lsoas, 50)
    congestion_scalers = np.full(num_lsoas, 1)

    df = pd.DataFrame({
        'lsoa_id': lsoa_ids,
        'pwc_x': pwc_x,
        'pwc_y': pwc_y,
        'crime_weight': weights,
        'speed_limit_kph': speed_limits,
        'congestion_scaler': congestion_scalers
    })

    return df

if __name__ == "__main__":
    mock_data = generate_mock_pwcs(num_lsoas=30)
    print(mock_data.head())

    
