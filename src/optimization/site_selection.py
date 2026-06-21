import numpy as np
import pandas as pd
import copy

# chooses the next police site to maximize TWEC gain
def choose_next_site(gdf, rm_r1, rm_r2, allocation, p=0.1, q=0.4):
    '''
    allocation = {
        "n": np.array of r1 unit counts for MSAOs,
        "m": np.array of r2 unit counts for MSAOs
    }
    '''

    nr_msoas = len(gdf)
    weights = gdf['final_weight'].values

    max_delta_twec = -1
    best_candidate = None # index in reach matrices
    
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



'''
repick_site aims to find one best replacement for the set of already chosen sites.

Computes the current TWEC.
For each site in chosen_sites, it:
    removes that site,
    searches all possible replacement sites via choose_next_site(...),
    measures the net TWEC change relative to the original allocation.

It keeps the best overall swap across all chosen sites.

If the best option is to keep the removed site, that is allowed:
    choose_next_site evaluates every site, including the removed one,
    if the best replacement is the same site, the delta becomes 0,
    max_delta_twec starts at -1, so a 0 delta will be accepted.
'''
def repick_site(gdf, rm_r1, rm_r2, allocation, chosen_sites, p=0.1, q=0.4):
    weights = gdf['final_weight'].values
    current_twec = calculate_twec(allocation, weights, p, q)
    max_delta_twec = -1
    best_candidate = None # index in reach matrices
    loser = None # index in reach matrices
    loser_list_idx = -1 # list index (position) in chosen_sites

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

    wec = (1.0 - (p**n) * (q**m)) * weights # weighted expected coverage per MSOA (renamed C*Weight to WEC to be more precise)
    twec = np.sum(wec) # total weighted expected coverage
    return twec
