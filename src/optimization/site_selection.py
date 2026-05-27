import numpy as np
import pandas as pd
import copy

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
    best_candidate = None # index
    
    current_twec = calculate_twec(allocation, weights, p, q)

    for i in range(nr_msoas):
        # add site i's coverage
        allocation = allocate_site(allocation, rm_r1, rm_r2, i)

        # simulate
        new_twec = calculate_twec(allocation, weights, p, q)
        delta_twec = new_twec - current_twec
        if  delta_twec > max_delta_twec:
            max_delta_twec = delta_twec
            best_candidate = i

        # backtrack
        allocation = deallocate_site(allocation, rm_r1, rm_r2, i)

    # finalize the allocation of best candidate
    allocation = allocate_site(allocation, rm_r1, rm_r2, best_candidate)
    twec = calculate_twec(allocation, weights, p, q)

    return allocation, best_candidate, twec



def repick_site(gdf, rm_r1, rm_r2, allocation, chosen_sites, p=0.1, q=0.4):
    weights = gdf['weight'].values
    current_twec = calculate_twec(allocation, weights, p, q)
    max_delta_twec = -1
    best_candidate = None
    loser = None
    loser_list_idx = -1

    for list_idx, site in enumerate(chosen_sites):
        # remove site's coverage
        allocation = deallocate_site(allocation, rm_r1, rm_r2, site)

        allocation, candidate, new_twec = choose_next_site(gdf, rm_r1, rm_r2, allocation, p, q)
        delta_twec = new_twec - current_twec
        if delta_twec > max_delta_twec:
            max_delta_twec = delta_twec
            best_candidate = candidate
            loser = site
            loser_list_idx = list_idx

        # deallocate candidate site (undo simulated allocation)
        allocation = deallocate_site(allocation, rm_r1, rm_r2, candidate)
        # backtrack - readd site's coverage
        allocation = allocate_site(allocation, rm_r1, rm_r2, site)

    # finilize the replacement - remove loser, add best_candidate
    allocation = deallocate_site(allocation, rm_r1, rm_r2, loser)
    allocation = allocate_site(allocation, rm_r1, rm_r2, best_candidate)

    twec = calculate_twec(allocation, weights, p, q)

    return allocation, best_candidate, loser_list_idx, twec



def allocate_site(allocation, rm_r1, rm_r2, i):
    affected_r1 = rm_r1[:, i]   
    affected_r2 = rm_r2[:, i]
    allocation['n'] += affected_r1
    allocation['m'] += affected_r2
    return allocation



def deallocate_site(allocation, rm_r1, rm_r2, i):
    affected_r1 = rm_r1[:, i]   
    affected_r2 = rm_r2[:, i]
    allocation['n'] -= affected_r1
    allocation['m'] -= affected_r2
    return allocation



def calculate_twec(allocation, weights, p, q):

    n = allocation['n']
    m = allocation['m']

    wec = (1.0 - (p**n) * (q**m)) * weights # weighted expected coverage per LSOA (renamed C*Weight to WEC to be more precise)
    twec = np.sum(wec) # total weighted expected coverage
    return twec
