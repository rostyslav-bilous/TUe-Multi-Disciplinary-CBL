import numpy as np
import pandas as pd
import geopandas as gpd

# was used in the initial stages of the project
def generate_mock_pwcs(num_lsoas=5, seed=None, width=15):
    
    np.random.seed(seed)
    lsoa_ids = [f'LSOA_{i}' for i in range(num_lsoas)]
    pwc_x = np.random.uniform(500000, 500000+width*1000, num_lsoas) # 15x15km grid by default
    pwc_y = np.random.uniform(180000, 180000+width*1000, num_lsoas)
    
    weights = np.random.choice(
        [0.1, 0.2, 0.7], 
        size=num_lsoas, 
        p=[0.40,0.35,0.25] 
    )

    speed_limits = np.full(num_lsoas, 50)
    congestion_scalers = np.full(num_lsoas, 1)
    geometry = gpd.points_from_xy(pwc_x, pwc_y)
    gdf = gpd.GeoDataFrame({
        'MSOA21CD': lsoa_ids,
        'X': pwc_x,
        'Y': pwc_y,
        'crime_weight': weights,
        'speed_limit_kph': speed_limits,
        'congestion_scaler': congestion_scalers,
    },
        geometry=geometry,
        crs="EPSG:27700" # meters
        )
    return gdf.to_crs("EPSG:4326")

if __name__ == "__main__":
    mock_data = generate_mock_pwcs(num_lsoas=30)
    print(mock_data.head())
