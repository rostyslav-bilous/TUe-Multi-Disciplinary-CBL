import pandas as pd
import numpy as np
import argparse
from pathlib import Path

from src.data.synthetic import generate_mock_pwcs
from src.optimization.network import compute_reach_matrices
from src.optimization.site_selection import choose_next_site, repick_site,calculate_twec
from src.data.loaders import load_gpkg
from src.config import DATA_DIR

def allocate(num_units, gdf, substitution, file_name):
    rm_r1, rm_r2 = compute_reach_matrices(gdf)

    print(f"Allocating {num_units} units...")
    num_lsoas = len(gdf)
    allocation = {
        "n": np.zeros(num_lsoas, dtype=int),
        "m": np.zeros(num_lsoas, dtype=int)
    }

    chosen_sites = [] # indices in reach matrices, not MSOA codes
    twec = 0.0
    p = 0.1
    q = 0.4
    for i in range(num_units):
        allocation, winner_site, twec = choose_next_site(gdf, rm_r1, rm_r2, allocation, p, q)
        chosen_sites.append(winner_site)

        if substitution:
            # find a better site because some allocations might be no longer justified
            allocation, winner_site, loser_list_idx, twec = repick_site(gdf, rm_r1, rm_r2, allocation, chosen_sites, p, q)
            chosen_sites[loser_list_idx] = winner_site # winner_site is an index in reach matrices

    theoretical_max_twec = np.sum(gdf['weight'].values)
    efficiency = twec / theoretical_max_twec
    site_codes = gdf.iloc[chosen_sites]['MSOA21CD'].tolist() # convert the list of matrix indices into MSOA codes

    # save chosen site codes
    if file_name:
        save_path = DATA_DIR / "allocation" / f'{file_name}.txt'
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            for site in site_codes:
                f.write(f'{site}\n')

    return allocation, chosen_sites, site_codes, twec, theoretical_max_twec, efficiency
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    parser.add_argument('-p', '--police_units')
    parser.add_argument('-s','--substitution', action='store_true')
    parser.add_argument('-o', '--output_name')
    args = parser.parse_args()

    if not args.file:
        num_lsoas = 10
        width = 15
        gdf = generate_mock_pwcs(num_lsoas=num_lsoas, width=width)
    else:
        gdf = load_gpkg(DATA_DIR / f"{args.file}.gpkg", "population_centroids")

    num_points = len(gdf)
    # WEIGHTS - to be replaced
    # np.random.seed(123)
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

    num_units = args.police_units or 10
    num_units = int(num_units)
    
    allocation, chosen_sites, site_codes, twec, theoretical_max_twec, efficiency = allocate(num_units, gdf, args.substitution, args.output_name)

    print("--------------Test Inputs---------------")
    if not args.file:
        print(f"Grid: {width}x{width}km")
    print(f"Number of MSOAs: {len(gdf)}")
    print(f"Number of Police units: {num_units}")
    print("----------------Results-----------------")
    # print(f'Coverage: {allocation}')
    print(f'Police Sites (index): {chosen_sites}')
    print(f'Police Sites (code): {site_codes}')
    print(f'Current Network TWEC: {twec:.2f}')
    print(f'Theoretical Max TWEC: {theoretical_max_twec:.2f}')
    print(f'Efficiency: {efficiency:.1%}')


    print("------------------Data-------------------")
    print(gdf)