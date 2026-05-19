import pandas as pd
import numpy as np
from scipy.spatial import distance_matrix

from generate_mock_pwcs import generate_mock_pwcs

def compute_reach_matrices():

    df = generate_mock_pwcs()
    dist_matrix_km = distance_matrix(df[['pwc_x', 'pwc_y']], df[['pwc_x', 'pwc_y']]) / 1000.0 # pairwise distances in km
    
    time1 = 8 / 60 # 8 min in h
    time2 = 16 / 60 # 16 min in h

    df['r1_km'] = df['speed_limit_kph'] * df['congestion_scaler'] * time1
    df['r2_km'] = df['speed_limit_kph'] * df['congestion_scaler'] * time2

    nr_lsoas = len(df)

    # compute coverage matrices for r1 and r2 
    # i(row) is LSOA and j(column) is the potential police site
    # row i represents which sites j cover LSOA i
    rm_r1 = np.zeros((nr_lsoas, nr_lsoas), dtype=bool)
    rm_r2 = np.zeros((nr_lsoas, nr_lsoas), dtype=bool)

    for i in range(nr_lsoas):
        lsoa_r1_window = df.loc[i, 'r1_km']
        lsoa_r2_window = df.loc[i, 'r2_km']

        for j in range(nr_lsoas):
            distance = dist_matrix_km[i, j]
            if distance <= lsoa_r1_window: rm_r1[i, j] = True
            elif distance <= lsoa_r2_window: rm_r2[i, j] = True
    
    return df, rm_r1, rm_r2

print(compute_reach_matrices())

