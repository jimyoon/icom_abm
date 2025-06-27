"""
Numba-optimized utility functions for chance-c performance improvements.
"""

import numpy as np
import numba
from typing import Tuple, Optional
from numba import prange

# Pre-compile all functions to eliminate compilation overhead
print("Pre-compiling numba functions for optimal performance...")

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
def build_spatial_grid(
    coords_x: np.ndarray,
    coords_y: np.ndarray,
    grid_size: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Build a spatial grid index for fast nearest neighbor searches.
    
    Args:
        coords_x: Array of x-coordinates
        coords_y: Array of y-coordinates
        grid_size: Size of each grid cell
        
    Returns:
        Tuple of (grid_x, grid_y, grid_indices, grid_counts)
    """
    n = len(coords_x)
    
    # Find grid bounds
    min_x, max_x = coords_x.min(), coords_x.max()
    min_y, max_y = coords_y.min(), coords_y.max()
    
    # Calculate grid dimensions
    nx = int((max_x - min_x) / grid_size) + 1
    ny = int((max_y - min_y) / grid_size) + 1
    
    # Initialize grid
    grid_x = np.zeros(n, dtype=np.int64)
    grid_y = np.zeros(n, dtype=np.int64)
    grid_indices = np.zeros(n, dtype=np.int64)
    grid_counts = np.zeros(nx * ny, dtype=np.int64)
    
    # Assign points to grid cells
    for i in range(n):
        gx = int((coords_x[i] - min_x) / grid_size)
        gy = int((coords_y[i] - min_y) / grid_size)
        grid_x[i] = gx
        grid_y[i] = gy
        grid_idx = gy * nx + gx
        grid_indices[i] = grid_idx
        grid_counts[grid_idx] += 1
    
    return grid_x, grid_y, grid_indices, grid_counts


@numba.jit(nopython=True, cache=True)
def find_nearest_neighbor_spatial(
    coords_x: np.ndarray,
    coords_y: np.ndarray,
    ref_x: float,
    ref_y: float,
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    grid_indices: np.ndarray,
    grid_counts: np.ndarray,
    grid_size: float,
    exclude_indices: Optional[np.ndarray] = None
) -> Tuple[int, float]:
    """
    Find nearest neighbor using spatial grid indexing.
    
    Args:
        coords_x: Array of x-coordinates
        coords_y: Array of y-coordinates
        ref_x: Reference x-coordinate
        ref_y: Reference y-coordinate
        grid_x: Grid x-coordinates for each point
        grid_y: Grid y-coordinates for each point
        grid_indices: Grid indices for each point
        grid_counts: Count of points in each grid cell
        grid_size: Size of each grid cell
        exclude_indices: Optional array of indices to exclude
        
    Returns:
        Tuple of (nearest_index, nearest_distance)
    """
    n = len(coords_x)
    min_x, max_x = coords_x.min(), coords_x.max()
    min_y, max_y = coords_y.min(), coords_y.max()
    nx = int((max_x - min_x) / grid_size) + 1
    
    # Find reference grid cell
    ref_gx = int((ref_x - min_x) / grid_size)
    ref_gy = int((ref_y - min_y) / grid_size)
    
    min_distance = np.inf
    nearest_index = -1
    
    # Search in expanding grid cells
    search_radius = 0
    max_search_radius = max(nx, int((max_y - min_y) / grid_size) + 1)
    
    while search_radius <= max_search_radius:
        # Check if we've found a point and it's closer than the next grid cell
        if nearest_index != -1:
            next_cell_distance = search_radius * grid_size
            if min_distance < next_cell_distance:
                break
        
        # Search in current radius
        for dgx in range(-search_radius, search_radius + 1):
            for dgy in range(-search_radius, search_radius + 1):
                gx = ref_gx + dgx
                gy = ref_gy + dgy
                
                if gx < 0 or gy < 0:
                    continue
                
                grid_idx = gy * nx + gx
                if grid_idx >= len(grid_counts):
                    continue
                
                # Find points in this grid cell
                start_idx = 0
                for i in range(grid_idx):
                    start_idx += grid_counts[i]
                
                for i in range(grid_counts[grid_idx]):
                    point_idx = start_idx + i
                    if point_idx >= n:
                        continue
                    
                    # Skip excluded indices
                    if exclude_indices is not None:
                        skip = False
                        for j in range(len(exclude_indices)):
                            if point_idx == exclude_indices[j]:
                                skip = True
                                break
                        if skip:
                            continue
                    
                    dx = coords_x[point_idx] - ref_x
                    dy = coords_y[point_idx] - ref_y
                    distance = np.sqrt(dx * dx + dy * dy)
                    
                    if distance < min_distance:
                        min_distance = distance
                        nearest_index = point_idx
        
        search_radius += 1
    
    return nearest_index, min_distance


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


# Pre-compile all functions with sample data
def _warmup_numba_functions():
    """Warm up numba functions to ensure they're compiled."""
    print("Warming up numba functions...")
    
    # Sample data for warmup
    coords_x = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    coords_y = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    prices = np.array([100.0, 200.0, 300.0], dtype=np.float64)
    weights = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    utilities = np.array([0.5, 0.8, 0.3], dtype=np.float64)
    sqfeet = np.array([1000.0, 1500.0, 2000.0], dtype=np.float64)
    age = np.array([10.0, 20.0, 30.0], dtype=np.float64)
    stories = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    baths = np.array([1.0, 2.0, 2.5], dtype=np.float64)
    residuals = np.array([0.1, 0.2, 0.3], dtype=np.float64)
    coefficients = np.array([1.0, 0.1, 0.05, 0.1, 0.2], dtype=np.float64)
    income = np.array([50000.0, 75000.0, 100000.0], dtype=np.float64)
    prox_cbd = np.array([0.5, 0.7, 0.3], dtype=np.float64)
    flood_risk = np.array([0.1, 0.2, 0.05], dtype=np.float64)
    a = np.full_like(income, 0.4)
    b = np.full_like(income, 0.4)
    c = np.full_like(income, 0.2)
    
    # Warm up all functions
    _ = calculate_distances_2d(coords_x, coords_y, 0.0, 0.0)
    _ = find_nearest_neighbor(coords_x, coords_y, 0.0, 0.0)
    _ = calculate_utilities_vectorized(sqfeet, age, stories, baths, residuals, coefficients)
    _ = calculate_cobb_douglas_utilities(income, prox_cbd, flood_risk, a, b, c)
    _ = filter_and_sample(prices, weights, 250.0, 2)
    _ = find_top_candidates(utilities, 2)
    
    # Warm up spatial indexing functions
    _ = build_spatial_grid(coords_x, coords_y, 1.0)
    _ = find_nearest_neighbor_spatial(coords_x, coords_y, 0.0, 0.0, 
                                    np.array([0, 1, 2]), np.array([0, 1, 2]), 
                                    np.array([0, 1, 2]), np.array([1, 1, 1]), 1.0)
    
    print("Numba functions warmed up successfully!")

# Warm up functions on import
_warmup_numba_functions() 