"""Utilities to perform sanity check."""

import numpy as np

def bootstrap(arr, n):
    """Bootstrap sample by a given times.
    
    Args:
        arr (array-like): original sample.
        n (int): Number of bootstrapped samples.
    
    Return:
        bootstrapped (list): list of bootstrapped samples.
    """
    bootstrapped = []
    for i in range(n):
        bootstrapped.append(np.random.choice(arr, size=len(arr), replace=True))

    return bootstrapped
