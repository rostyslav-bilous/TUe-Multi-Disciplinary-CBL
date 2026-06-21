import pandas as pd
import numpy as np
import argparse
from pathlib import Path

from src.data.synthetic import generate_mock_pwcs
from src.optimization.network import compute_reach_matrices
from src.optimization.site_selection import choose_next_site, repick_site,calculate_twec
from src.data.loaders import load_gpkg
from src.config import DATA_DIR


'''
Allocates units based on inputs:
num_units - number of police units
gdf_cents - GeoDataFrame of area's centroids
substitution - Boolean, True to use substitution
df_tiers - DataFrame of tiers/weights
prob_pr - probability of unavailability of primary units
prob_ba - probability of unavailability of backup units
window_pr - responce window in minutes of primary units
window_ba - responce window in minutes of backup units
output_file_name - (Optional) name of the file to save the allocation in 
'''
def allocate(num_units, gdf_cents, substitution, df_tiers, prob_pr, prob_ba, window_pr, window_ba, output_file_name):
     # load speeds table
    df_speeds = pd.read_csv(DATA_DIR / 'speeds' / 'UK_speeds.csv')
    # join cents and speeds table
    gdf_cents = gdf_cents.merge(df_speeds, on="MSOA21CD", how='left') 
    # load tiers table
    df_weights = df_tiers[['MSOA21CD', 'final_weight', 'tier_adjusted']]
    # join cents and tiers table
    gdf_cents = gdf_cents.merge(df_weights, on="MSOA21CD", how='left')

    # calculate reach matrices
    rm_r1, rm_r2 = compute_reach_matrices(gdf_cents, window_pr, window_ba)

    print(f"Allocating {num_units} units...")
    num_lsoas = len(gdf_cents)
    allocation = {
        "n": np.zeros(num_lsoas, dtype=int),
        "m": np.zeros(num_lsoas, dtype=int)
    }

    chosen_sites = [] # indices in reach matrices, not MSOA codes
    twec = 0.0
    p = prob_pr
    q = prob_ba
    for i in range(num_units):
        allocation, winner_site, twec = choose_next_site(gdf_cents, rm_r1, rm_r2, allocation, p, q)
        chosen_sites.append(winner_site)

        if substitution:
            # find a better site because some allocations might be no longer justified
            allocation, winner_site, loser_list_idx, twec = repick_site(gdf_cents, rm_r1, rm_r2, allocation, chosen_sites, p, q)
            chosen_sites[loser_list_idx] = winner_site # winner_site is an index in reach matrices

    theoretical_max_twec = np.sum(gdf_cents['final_weight'].values)
    efficiency = twec / theoretical_max_twec
    site_codes = gdf_cents.iloc[chosen_sites]['MSOA21CD'].tolist() # convert the list of matrix indices into MSOA codes

    # save chosen site codes
    if output_file_name:
        save_path = DATA_DIR / "allocation" / f'{output_file_name}.txt'
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            for site in site_codes:
                f.write(f'{site}\n')

    return site_codes, twec, theoretical_max_twec
