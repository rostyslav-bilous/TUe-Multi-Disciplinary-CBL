import pandas as pd
import numpy as np
import argparse

from src.data.synthetic import generate_mock_pwcs
from src.optimization.network import compute_reach_matrices
from src.optimization.site_selection import choose_next_site, calculate_twec
from src.data.loaders import get_spatial_data

def allocate(num_units, gdf):
    rm_r1, rm_r2, dist_matrix_km = compute_reach_matrices(gdf)

    num_lsoas = len(gdf)
    allocation = {
        "n": np.zeros(num_lsoas, dtype=int),
        "m": np.zeros(num_lsoas, dtype=int)
    }

    chosen_sites = []
    twec = 0.0
    p = 0.1
    q = 0.4
    for i in range(num_units):
        allocation, winner_site, twec = choose_next_site(gdf, rm_r1, rm_r2, allocation, p, q)
        chosen_sites.append(winner_site)

    theoretical_max_twec = np.sum(gdf['weight'].values)
    efficiency = twec / theoretical_max_twec
    return allocation, chosen_sites, dist_matrix_km, twec, theoretical_max_twec, efficiency

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file')
    args = parser.parse_args()

    if not args.file:
        num_lsoas = 10
        width = 15
        gdf = generate_mock_pwcs(num_lsoas=num_lsoas, width=width)
    else:
        gdf = get_spatial_data(f"{args.file}", layer_name="population_centroids")

    num_points = len(gdf)
    # WEIGHTS - to be replaced
    weights = np.random.choice(
        [0.1, 0.2, 0.7], 
        size=num_points, 
        p=[0.40,0.35,0.25] 
    )

    speed_limits = np.full(num_points, 30)
    congestion_scalers = np.full(num_points, 1)

    gdf['weight'] = weights
    gdf['speed_limit_kph'] = speed_limits
    gdf['congestion_scaler'] = congestion_scalers
    num_units = 100
    
    allocation, chosen_sites, dist_matrix_km, twec, theoretical_max_twec, efficiency = allocate(num_units, gdf)

    print("--------------Test Inputs---------------")
    if not args.file:
        print(f"Grid: {width}x{width}km")
    print(f"Number of MSOAs: {len(gdf)}")
    print(f"Number of Police units: {num_units}")
    print("----------------Results-----------------")
    # print(f'Coverage: {allocation}')
    print(f'Police Sites: {chosen_sites}')
    print(f'Current Network TWEC: {twec:.2f}')
    print(f'Theoretical Max TWEC: {theoretical_max_twec:.2f}')
    print(f'Efficiency: {efficiency:.1%}')


    print("------------------Data-------------------")
    print(gdf)