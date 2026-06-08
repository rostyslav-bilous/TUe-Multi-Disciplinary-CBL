import pandas as pd
import numpy as np
import argparse
from pathlib import Path

from src.data.synthetic import generate_mock_pwcs
from src.optimization.network import compute_reach_matrices
from src.optimization.site_selection import choose_next_site, repick_site,calculate_twec
from src.data.loaders import load_gpkg
from src.config import DATA_DIR

def allocate(num_units, gdf_cents, substitution, df_tiers, output_file_name):
     # load speeds table
    df_speeds = pd.read_csv(DATA_DIR / 'speeds' / 'UK_speeds.csv')
    # join cents and speeds table
    gdf_cents = gdf_cents.merge(df_speeds, on="MSOA21CD", how='left') 
    # load tiers table
    df_weights = df_tiers[['msoa_code', 'final_weight', 'tier_adjusted']].rename(columns={'msoa_code': 'MSOA21CD', 'final_weight': 'weight'})
    # join cents and tiers table
    gdf_cents = gdf_cents.merge(df_weights, on="MSOA21CD", how='left')

    # calculate reach matrices
    rm_r1, rm_r2 = compute_reach_matrices(gdf_cents)

    print(f"Allocating {num_units} units...")
    num_lsoas = len(gdf_cents)
    allocation = {
        "n": np.zeros(num_lsoas, dtype=int),
        "m": np.zeros(num_lsoas, dtype=int)
    }

    chosen_sites = [] # indices in reach matrices, not MSOA codes
    twec = 0.0
    p = 0.1
    q = 0.4
    for i in range(num_units):
        allocation, winner_site, twec = choose_next_site(gdf_cents, rm_r1, rm_r2, allocation, p, q)
        chosen_sites.append(winner_site)

        if substitution:
            # find a better site because some allocations might be no longer justified
            allocation, winner_site, loser_list_idx, twec = repick_site(gdf_cents, rm_r1, rm_r2, allocation, chosen_sites, p, q)
            chosen_sites[loser_list_idx] = winner_site # winner_site is an index in reach matrices

    theoretical_max_twec = np.sum(gdf_cents['weight'].values)
    efficiency = twec / theoretical_max_twec
    site_codes = gdf_cents.iloc[chosen_sites]['MSOA21CD'].tolist() # convert the list of matrix indices into MSOA codes

    # save chosen site codes
    if output_file_name:
        save_path = DATA_DIR / "allocation" / f'{output_file_name}.txt'
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            for site in site_codes:
                f.write(f'{site}\n')

    return gdf_cents, allocation, chosen_sites, site_codes, twec, theoretical_max_twec, efficiency
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--area_file_name')
    parser.add_argument('-p', '--police_units')
    parser.add_argument('-s', '--substitution', action='store_true')
    parser.add_argument('-o', '--output_name')
    parser.add_argument('-t', '--tiers_file_name')
    args = parser.parse_args()

    # load area
    if not args.area_file_name:
        num_lsoas = 10
        width = 15
        gdf_cents = generate_mock_pwcs(num_lsoas=num_lsoas, width=width)
    else:
        gdf_cents = load_gpkg(DATA_DIR / f"{args.area_file_name}.gpkg", "population_centroids")

    # load tiers
    df_tiers = pd.read_csv(DATA_DIR / 'monthly_tiers' / f'{args.tiers_file_name}.csv')

    # define num of police units
    num_units = args.police_units or 10
    num_units = int(num_units)
    
    # run allocation
    gdf_cents, allocation, chosen_sites, site_codes, twec, theoretical_max_twec, efficiency = allocate(num_units, gdf_cents, args.substitution, df_tiers, args.output_name)

    print("--------------Test Inputs---------------")
    if not args.area_file_name:
        print(f"Grid: {width}x{width}km")
    print(f"Number of MSOAs: {len(gdf_cents)}")
    print(f"Number of Police units: {num_units}")
    print("----------------Results-----------------")
    # print(f'Coverage: {allocation}')
    print(f'Police Sites (index): {chosen_sites}')
    print(f'Police Sites (code): {site_codes}')
    print(f'Current Network TWEC: {twec:.2f}')
    print(f'Theoretical Max TWEC: {theoretical_max_twec:.2f}')
    print(f'Efficiency: {efficiency:.1%}')


    print("------------------Data-------------------")
    print(gdf_cents)