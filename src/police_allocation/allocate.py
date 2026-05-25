import pandas as pd
import numpy as np
import argparse

from src.preprocessing.generate_mock_pwcs import generate_mock_pwcs
from src.preprocessing.compute_reach_matrices import compute_reach_matrices
from src.police_allocation.choose_next_site import choose_next_site, calculate_twec

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

    theoretical_max_twec = np.sum(gdf['crime_weight'].values)
    efficiency = twec / theoretical_max_twec
    return allocation, chosen_sites, gdf, dist_matrix_km, twec, theoretical_max_twec, efficiency

if __name__ == "__main__":
    # only for testing purpose
    num_lsoas = 10
    num_units = 3
    width = 15
    gdf = generate_mock_pwcs(num_lsoas=num_lsoas, width=width)
    allocation, chosen_sites, gdf, dist_matrix_km, twec, theoretical_max_twec, efficiency = allocate(num_units, gdf)

    print("--------------Test Inputs---------------")
    print(f"Grid: {width}x{width}km")
    print(f"Number of MSOAs: {len(gdf)}")
    print(f"Number of Police units: {num_units}")
    print("----------------Results-----------------")
    # print(f'Coverage: {allocation}')
    print(f'Police Sites: {chosen_sites}')
    print(f'Current Network TWEC: {twec:.2f}')
    print(f'Theoretical Max TWEC: {theoretical_max_twec:.2f}')
    print(f'Efficiency: {efficiency:.1%}')


    print("-----------------LSOAs-----------------")
    print(gdf)