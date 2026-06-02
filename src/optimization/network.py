import pandas as pd
import numpy as np
from pathlib import Path
from scipy.spatial import distance_matrix

from src.data.synthetic import generate_mock_pwcs
from src.config import DATA_DIR

def compute_reach_matrices(gdf, r1_min=5, r2_min=10):

    print("Computing matrices...")
    dist_matrix_km = distance_matrix(gdf[['X', 'Y']], gdf[['X', 'Y']]) / 1000.0 # pairwise distances in km
    
    r1_min = r1_min / 60 # 5 min in h
    r2_min = r2_min / 60 # 10 min in h

    gdf['r1_km'] = gdf['speed_limit_kph'] * gdf['congestion_scaler'] * r1_min
    gdf['r2_km'] = gdf['speed_limit_kph'] * gdf['congestion_scaler'] * r2_min

    nr_points = len(gdf)

    # compute coverage matrices for r1 and r2 
    # i(row) is MSOA and j(column) is the potential police site
    # row i represents which sites j cover MSOA i
    rm_r1 = np.zeros((nr_points, nr_points), dtype=bool)
    rm_r2 = np.zeros((nr_points, nr_points), dtype=bool)

    for j in range(nr_points):
        r1_window = gdf.loc[j, 'r1_km']
        r2_window = gdf.loc[j, 'r2_km']

        for i in range(nr_points):
            distance = dist_matrix_km[i, j]
            if distance <= r1_window: rm_r1[i, j] = True
            elif distance <= r2_window: rm_r2[i, j] = True
    
    return rm_r1, rm_r2

def compute_radii():
    