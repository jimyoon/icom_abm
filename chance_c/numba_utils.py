"""
Numba-optimized utility functions for chance-c performance improvements.
"""

import numpy as np
import numba
from typing import Tuple, Optional
from numba import prange


@numba.jit(nopython=True, cache=True)
def calculate_distances_2d(
    coords_x: np.ndarray, 
    coords_y: np.ndarray, 
    ref_x: float, 
    ref_y: float
) -> np.ndarray:
    """
    Calculate Euclidean distances from a reference point to multiple coordinates.
    
    Args:
        coords_x: Array of x-coordinates
        coords_y: Array of y-coordinates  
        ref_x: Reference x-coordinate
        ref_y: Reference y-coordinate
        
    Returns:
        Array of distances from reference point to each coordinate
    """
    n = len(coords_x)
    distances = np.empty(n, dtype=np.float64)
    
    for i in range(n):
        dx = coords_x[i] - ref_x
        dy = coords_y[i] - ref_y
        distances[i] = np.sqrt(dx * dx + dy * dy)
    
    return distances


@numba.jit(nopython=True, cache=True)
def find_nearest_neighbor(
    coords_x: np.ndarray,
    coords_y: np.ndarray,
    ref_x: float,
    ref_y: float,
    exclude_indices: Optional[np.ndarray] = None
) -> Tuple[int, float]:
    """
    Find the nearest neighbor to a reference point.
    
    Args:
        coords_x: Array of x-coordinates
        coords_y: Array of y-coordinates
        ref_x: Reference x-coordinate
        ref_y: Reference y-coordinate
        exclude_indices: Optional array of indices to exclude from search
        
    Returns:
        Tuple of (nearest_index, nearest_distance)
    """
    n = len(coords_x)
    min_distance = np.inf
    nearest_index = -1
    
    for i in range(n):
        # Skip excluded indices
        if exclude_indices is not None:
            skip = False
            for j in range(len(exclude_indices)):
                if i == exclude_indices[j]:
                    skip = True
                    break
            if skip:
                continue
        
        dx = coords_x[i] - ref_x
        dy = coords_y[i] - ref_y
        distance = np.sqrt(dx * dx + dy * dy)
        
        if distance < min_distance:
            min_distance = distance
            nearest_index = i
    
    return nearest_index, min_distance


@numba.njit(parallel=True, cache=True)
def calculate_utilities_vectorized(
    sqfeet: np.ndarray,
    age: np.ndarray, 
    stories: np.ndarray,
    baths: np.ndarray,
    residuals: np.ndarray,
    coefficients: np.ndarray
) -> np.ndarray:
    """
    Calculate utilities using vectorized operations.
    
    Args:
        sqfeet: Array of square footage values
        age: Array of age values
        stories: Array of story counts
        baths: Array of bathroom counts
        residuals: Array of residual values
        coefficients: Array of utility coefficients [intercept, sqfeet_coef, age_coef, stories_coef, baths_coef]
        
    Returns:
        Array of calculated utilities
    """
    n = len(sqfeet)
    utilities = np.empty(n, dtype=np.float64)
    for i in prange(n):
        utilities[i] = (coefficients[0] + 
                       coefficients[1] * sqfeet[i] + 
                       coefficients[2] * age[i] + 
                       coefficients[3] * stories[i] + 
                       coefficients[4] * baths[i] + 
                       residuals[i])
    return utilities


@numba.njit(parallel=True, cache=True)
def calculate_utilities_with_flood_vectorized(
    sqfeet: np.ndarray,
    age: np.ndarray, 
    stories: np.ndarray,
    baths: np.ndarray,
    flood: np.ndarray,
    residuals: np.ndarray,
    coefficients: np.ndarray
) -> np.ndarray:
    """
    Calculate utilities using vectorized operations including flood term.
    
    Args:
        sqfeet: Array of square footage values
        age: Array of age values
        stories: Array of story counts
        baths: Array of bathroom counts
        flood: Array of flood values
        residuals: Array of residual values
        coefficients: Array of utility coefficients [intercept, sqfeet_coef, age_coef, stories_coef, baths_coef, flood_coef]
        
    Returns:
        Array of calculated utilities
    """
    n = len(sqfeet)
    utilities = np.empty(n, dtype=np.float64)
    for i in prange(n):
        utilities[i] = (coefficients[0] + 
                       coefficients[1] * sqfeet[i] + 
                       coefficients[2] * age[i] + 
                       coefficients[3] * stories[i] + 
                       coefficients[4] * baths[i] + 
                       coefficients[5] * flood[i] + 
                       residuals[i])
    return utilities


@numba.njit(parallel=True, cache=True)
def calculate_cobb_douglas_utilities(
    income: np.ndarray,
    prox_cbd: np.ndarray,
    flood_risk: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray
) -> np.ndarray:
    """
    Calculate Cobb-Douglas utilities.
    
    Args:
        income: Array of income values
        prox_cbd: Array of CBD proximity values
        flood_risk: Array of flood risk values
        a: Income exponent
        b: CBD proximity exponent
        c: Flood risk exponent
        
    Returns:
        Array of calculated utilities
    """
    n = len(income)
    utilities = np.empty(n, dtype=np.float64)
    for i in prange(n):
        utilities[i] = (income[i] ** a[i]) * (prox_cbd[i] ** b[i]) * (flood_risk[i] ** c[i])
    return utilities


@numba.jit(nopython=True, cache=True)
def filter_and_sample(
    prices: np.ndarray,
    weights: np.ndarray,
    budget: float,
    n_sample: int
) -> np.ndarray:
    """
    Filter by budget and sample with weights.
    
    Args:
        prices: Array of prices
        weights: Array of weights for sampling
        budget: Budget constraint
        n_sample: Number of samples to take
        
    Returns:
        Array of sampled indices
    """
    n = len(prices)
    filtered_indices = np.empty(n, dtype=np.int64)
    count = 0
    
    # Filter by budget
    for i in range(n):
        if prices[i] <= budget:
            filtered_indices[count] = i
            count += 1
    
    if count == 0:
        # Always return a numpy array of the correct type
        return np.zeros(0, dtype=np.int64)
    
    # Get filtered arrays
    valid_indices = filtered_indices[:count]
    filtered_weights = np.empty(count, dtype=np.float64)
    
    for i in range(count):
        filtered_weights[i] = weights[valid_indices[i]]
    
    # Normalize weights
    weight_sum = 0.0
    for i in range(count):
        weight_sum += filtered_weights[i]
    
    if weight_sum == 0.0:
        return np.zeros(0, dtype=np.int64)
    
    normalized_weights = np.empty(count, dtype=np.float64)
    for i in range(count):
        normalized_weights[i] = filtered_weights[i] / weight_sum
    
    # Sample with replacement
    sample_size = min(n_sample, count)
    sampled_indices = np.empty(sample_size, dtype=np.int64)
    
    for i in range(sample_size):
        # Simple random sampling with weights
        r = np.random.random()
        cumsum = 0.0
        for j in range(count):
            cumsum += normalized_weights[j]
            if r <= cumsum:
                sampled_indices[i] = valid_indices[j]
                break
    
    return sampled_indices


@numba.jit(nopython=True, cache=True)
def find_top_candidates(
    utilities: np.ndarray,
    n_candidates: int
) -> np.ndarray:
    """
    Find top candidates based on utility values.
    
    Args:
        utilities: Array of utility values
        n_candidates: Number of top candidates to return
        
    Returns:
        Array of indices of top candidates (sorted by utility, descending)
    """
    n = len(utilities)
    n_return = min(n_candidates, n)
    
    # Create array of indices
    indices = np.arange(n, dtype=np.int64)
    
    # Simple bubble sort for top n (not most efficient but works with numba)
    for i in range(n_return):
        for j in range(n - 1 - i):
            if utilities[indices[j]] < utilities[indices[j + 1]]:
                # Swap indices
                temp = indices[j]
                indices[j] = indices[j + 1]
                indices[j + 1] = temp
    
    return indices[:n_return] 