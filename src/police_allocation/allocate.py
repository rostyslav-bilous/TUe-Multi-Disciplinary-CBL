import pandas as pd
import numpy as np

from generate_mock_pwcs import generate_mock_pwcs
from compute_reach_matrices import compute_reach_matrices
from choose_next_site import choose_next_site, calculate_twec

def allocate(num_units):
    df_lsoas = generate_mock_pwcs(num_lsoas=10, width=15)
    rm_r1, rm_r2, dist_matrix_km = compute_reach_matrices(df_lsoas)

    num_lsoas = len(df_lsoas)
    allocation = {
        "n": np.zeros(num_lsoas, dtype=int),
        "m": np.zeros(num_lsoas, dtype=int)
    }

    chosen_sites = []
    twec = 0.0
    p = 0.1
    q = 0.4
    for i in range(num_units):
        allocation, winner_site, twec = choose_next_site(df_lsoas, rm_r1, rm_r2, allocation, p, q)
        chosen_sites.append(winner_site)

    theoretical_max_twec = np.sum(df_lsoas['crime_weight'].values)
    efficiency = twec / theoretical_max_twec
    return allocation, chosen_sites, df_lsoas, dist_matrix_km, twec, theoretical_max_twec, efficiency

if __name__ == "__main__":
    num_units = 3
    allocation, chosen_sites, df_lsoas, dist_matrix_km, twec, theoretical_max_twec, efficiency = allocate(num_units)

    print("--------------Mock Inputs---------------")
    print(f"Number of LSOAs: {len(df_lsoas)}")
    print(f"Number of Police units: {num_units}")
    print(f"Grid: by default now 15x15km")
    print("----------------Results-----------------")
    # print(f'Coverage: {allocation}')
    print(f'Police Sites: {chosen_sites}')
    print(f'Current Network TWEC: {twec:.2f}')
    print(f'Theoretical Max TWEC: {theoretical_max_twec:.2f}')
    print(f'Efficiency: {efficiency:.1%}')


    print("-----------------LSOAs-----------------")
    print(df_lsoas)

    # print(dist_matrix_km)