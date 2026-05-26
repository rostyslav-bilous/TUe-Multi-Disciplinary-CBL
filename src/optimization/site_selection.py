import numpy as np
import pandas as pd

def choose_next_site(gdf, rm_r1, rm_r2, allocation, p=0.1, q=0.4):
    '''
    allocation = {
        "n": np.array of r1 unit counts for LSAOs,
        "m": np.array of r2 unit counts for LSAOs
    }
    '''

    nr_msoas = len(gdf)
    weights = gdf['weight'].values

    max_delta_twec = -1
    best_candidate = None
    
    current_twec = calculate_twec(allocation, weights, p, q)

    for i in range(nr_msoas):

        # add site i's coverage
        affected_r1 = rm_r1[:, i]   
        affected_r2 = rm_r2[:, i]
        allocation['n'] += affected_r1
        allocation['m'] += affected_r2

        # simulate
        new_twec = calculate_twec(allocation, weights, p, q)
        delta_twec = new_twec - current_twec
        if  delta_twec > max_delta_twec:
            max_delta_twec = delta_twec
            best_candidate = i

        # backtrack
        allocation['n'] -= affected_r1
        allocation['m'] -= affected_r2
    
    affected_r1 = rm_r1[:, best_candidate]
    affected_r2 = rm_r2[:, best_candidate]
    allocation['n'] += affected_r1
    allocation['m'] += affected_r2
    twec = calculate_twec(allocation, weights, p, q)

    return allocation, gdf.loc[best_candidate, 'MSOA21CD'], twec


def calculate_twec(allocation, weights, p, q):

    n = allocation['n']
    m = allocation['m']

    wec = (1.0 - (p**n) * (q**m)) * weights # weighted expected coverage per LSOA (renamed C*Weight to WEC to be more precise)
    twec = np.sum(wec) # total weighted expected coverage
    return twec
