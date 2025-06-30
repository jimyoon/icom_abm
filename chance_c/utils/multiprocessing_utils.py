import multiprocessing as mp
import numpy as np
import pandas as pd
import polars as pl
from typing import List, Dict, Tuple, Any
import logging
from functools import partial
from chance_c.utils.numba_utils import (
    calculate_utilities_vectorized, 
    calculate_cobb_douglas_utilities,
    calculate_utilities_with_flood_vectorized,
    filter_and_sample
)


def parallel_utility_calculation_chunk(chunk_data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, str, List[float]]) -> np.ndarray:
    """
    Calculate utilities for a chunk of data in parallel.
    
    Args:
        chunk_data: Tuple containing (income, prox_cbd, flood_risk, sqfeet, age, stories, baths, residuals, house_choice_mode, simple_anova_coefficients)
        
    Returns:
        np.ndarray: Calculated utilities for the chunk
    """
    income, prox_cbd, flood_risk, sqfeet, age, stories, baths, residuals, house_choice_mode, simple_anova_coefficients = chunk_data
    
    if house_choice_mode == 'cobb_douglas_utility':
        # For Cobb-Douglas, we need a, b, c parameters
        a = np.full_like(income, 0.4)
        b = np.full_like(income, 0.4)
        c = np.full_like(income, 0.2)
        return calculate_cobb_douglas_utilities(income, prox_cbd, flood_risk, a, b, c)
    
    elif house_choice_mode == 'simple_flood_utility':
        coefficients = np.array(simple_anova_coefficients, dtype=np.float64)
        return calculate_utilities_with_flood_vectorized(sqfeet, age, stories, baths, flood_risk, residuals, coefficients)
    
    elif house_choice_mode == 'simple_anova_utility':
        coefficients = np.array(simple_anova_coefficients, dtype=np.float64)
        return calculate_utilities_vectorized(sqfeet, age, stories, baths, residuals, coefficients)
    
    else:
        # Default to simple ANOVA
        coefficients = np.array(simple_anova_coefficients, dtype=np.float64)
        return calculate_utilities_vectorized(sqfeet, age, stories, baths, residuals, coefficients)


def parallel_household_processing_chunk(chunk_data: Tuple[List, pd.DataFrame, int, str, List[float], float]) -> List[pd.DataFrame]:
    """
    Process a chunk of households for location assignment in parallel.
    
    Args:
        chunk_data: Tuple containing (households, block_group_df, block_group_sample_size, house_choice_mode, simple_anova_coefficients, budget_reduction_perc)
        
    Returns:
        List[pd.DataFrame]: List of sampled DataFrames for each household
    """
    households, block_group_df, block_group_sample_size, house_choice_mode, simple_anova_coefficients, budget_reduction_perc = chunk_data
    
    results = []
    
    for household in households:
        # Filter by budget
        if hasattr(household, 'house_budget'):
            budget_filter = block_group_df['new_price'] <= household.house_budget
            block_group_budget = block_group_df[budget_filter].copy()
        else:
            block_group_budget = block_group_df.copy()
        
        if len(block_group_budget) == 0:
            continue
            
        # Sample block groups
        n_sample = min(block_group_sample_size, len(block_group_budget))
        prices = block_group_budget['new_price'].to_numpy(dtype=np.float64)
        weights = block_group_budget['available_units'].to_numpy(dtype=np.float64)
        indices = filter_and_sample(prices, weights, np.inf, n_sample)
        
        if len(indices) == 0:
            continue
            
        block_group_sample = block_group_budget.iloc[indices].copy()
        block_group_sample['household'] = household.name
        block_group_sample['a'] = 0.4
        block_group_sample['b'] = 0.4
        block_group_sample['c'] = 0.2
        
        # Calculate utilities
        if house_choice_mode == 'cobb_douglas_utility':
            income = block_group_sample['average_income_norm'].to_numpy(dtype=np.float64)
            prox_cbd = block_group_sample['prox_cbd_norm'].to_numpy(dtype=np.float64)
            flood_risk = block_group_sample['flood_risk_norm'].to_numpy(dtype=np.float64)
            a = block_group_sample['a'].to_numpy(dtype=np.float64)
            b = block_group_sample['b'].to_numpy(dtype=np.float64)
            c = block_group_sample['c'].to_numpy(dtype=np.float64)
            utilities = calculate_cobb_douglas_utilities(income, prox_cbd, flood_risk, a, b, c)
            block_group_sample['utility'] = utilities
            
        elif house_choice_mode == 'simple_flood_utility':
            sqfeet = block_group_sample['N_MeanSqfeet'].to_numpy(dtype=np.float64)
            age = block_group_sample['N_MeanAge'].to_numpy(dtype=np.float64)
            stories = block_group_sample['N_MeanNoOfStories'].to_numpy(dtype=np.float64)
            baths = block_group_sample['N_MeanFullBathNumber'].to_numpy(dtype=np.float64)
            flood_risk = block_group_sample['N_perc_area_flood'].to_numpy(dtype=np.float64)
            residuals = block_group_sample['residuals'].to_numpy(dtype=np.float64)
            coefficients = np.array(simple_anova_coefficients, dtype=np.float64)
            utilities = calculate_utilities_with_flood_vectorized(sqfeet, age, stories, baths, flood_risk, residuals, coefficients)
            block_group_sample['utility'] = utilities
            
        elif house_choice_mode == 'simple_anova_utility':
            sqfeet = block_group_sample['N_MeanSqfeet'].to_numpy(dtype=np.float64)
            age = block_group_sample['N_MeanAge'].to_numpy(dtype=np.float64)
            stories = block_group_sample['N_MeanNoOfStories'].to_numpy(dtype=np.float64)
            baths = block_group_sample['N_MeanFullBathNumber'].to_numpy(dtype=np.float64)
            residuals = block_group_sample['residuals'].to_numpy(dtype=np.float64)
            coefficients = np.array(simple_anova_coefficients, dtype=np.float64)
            utilities = calculate_utilities_vectorized(sqfeet, age, stories, baths, residuals, coefficients)
            block_group_sample['utility'] = utilities
            
        else:
            # Default to simple ANOVA
            sqfeet = block_group_sample['N_MeanSqfeet'].to_numpy(dtype=np.float64)
            age = block_group_sample['N_MeanAge'].to_numpy(dtype=np.float64)
            stories = block_group_sample['N_MeanNoOfStories'].to_numpy(dtype=np.float64)
            baths = block_group_sample['N_MeanFullBathNumber'].to_numpy(dtype=np.float64)
            residuals = block_group_sample['residuals'].to_numpy(dtype=np.float64)
            coefficients = np.array(simple_anova_coefficients, dtype=np.float64)
            utilities = calculate_utilities_vectorized(sqfeet, age, stories, baths, residuals, coefficients)
            block_group_sample['utility'] = utilities
        
        results.append(block_group_sample)
    
    return results


def parallel_market_matching_chunk(chunk_data: Tuple[np.ndarray, np.ndarray, np.ndarray, set]) -> Dict[str, str]:
    """
    Perform market matching for a chunk of households in parallel.
    
    Args:
        chunk_data: Tuple containing (household_geoids, household_utilities, household_names, used_geoids)
        
    Returns:
        Dict[str, str]: Dictionary mapping household names to assigned GEOIDs
    """
    household_geoids, household_utilities, household_names, used_geoids = chunk_data
    
    assignments = {}
    
    for i, household in enumerate(household_names):
        # Find all options for this household
        household_mask = household_names == household
        geoids = household_geoids[household_mask]
        utilities = household_utilities[household_mask]
        
        if len(geoids) == 0:
            continue
        
        # Sort by utility (descending) and find first available
        sorted_indices = np.argsort(utilities)[::-1]
        
        assigned = False
        for idx in sorted_indices:
            geoid = geoids[idx]
            if geoid not in used_geoids:
                assignments[household] = geoid
                used_geoids.add(geoid)
                assigned = True
                break
        
        if not assigned:
            assignments[household] = 'outmigrated'
    
    return assignments


def parallel_utility_calculation(df: pd.DataFrame, house_choice_mode: str, simple_anova_coefficients: List[float], n_processes: int = None) -> np.ndarray:
    """
    Calculate utilities for a DataFrame in parallel.
    
    Args:
        df: DataFrame containing housing data
        house_choice_mode: Mode for utility calculation
        simple_anova_coefficients: Coefficients for ANOVA utility
        n_processes: Number of processes to use (defaults to CPU count)
        
    Returns:
        np.ndarray: Calculated utilities
    """
    if n_processes is None:
        n_processes = min(mp.cpu_count(), 8)  # Limit to 8 processes to avoid overhead
    
    # Prepare data arrays
    income = df['average_income_norm'].to_numpy(dtype=np.float64)
    prox_cbd = df['prox_cbd_norm'].to_numpy(dtype=np.float64)
    flood_risk = df['flood_risk_norm'].to_numpy(dtype=np.float64)
    sqfeet = df['N_MeanSqfeet'].to_numpy(dtype=np.float64)
    age = df['N_MeanAge'].to_numpy(dtype=np.float64)
    stories = df['N_MeanNoOfStories'].to_numpy(dtype=np.float64)
    baths = df['N_MeanFullBathNumber'].to_numpy(dtype=np.float64)
    residuals = df['residuals'].to_numpy(dtype=np.float64)
    
    # Split data into chunks
    chunk_size = len(df) // n_processes
    chunks = []
    
    for i in range(n_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < n_processes - 1 else len(df)
        
        chunk_data = (
            income[start_idx:end_idx],
            prox_cbd[start_idx:end_idx],
            flood_risk[start_idx:end_idx],
            sqfeet[start_idx:end_idx],
            age[start_idx:end_idx],
            stories[start_idx:end_idx],
            baths[start_idx:end_idx],
            residuals[start_idx:end_idx],
            house_choice_mode,
            simple_anova_coefficients
        )
        chunks.append(chunk_data)
    
    # Process in parallel
    with mp.Pool(processes=n_processes) as pool:
        results = pool.map(parallel_utility_calculation_chunk, chunks)
    
    # Combine results
    return np.concatenate(results)


def parallel_household_processing(
        households: List, 
        block_group_df: pd.DataFrame, 
        block_group_sample_size: int, 
        house_choice_mode: str, 
        simple_anova_coefficients: List[float], 
        budget_reduction_perc: float = 0.10, 
        n_processes: int = None
) -> List[pd.DataFrame]:
    """
    Process households for location assignment in parallel.
    
    Args:
        households: List of household agents
        block_group_df: DataFrame containing block group data
        block_group_sample_size: Number of block groups to sample
        house_choice_mode: Mode for utility calculation
        simple_anova_coefficients: Coefficients for ANOVA utility
        budget_reduction_perc: Budget reduction percentage
        n_processes: Number of processes to use (defaults to CPU count)
        
    Returns:
        List[pd.DataFrame]: List of sampled DataFrames for each household
    """
    if n_processes is None:
        n_processes = min(mp.cpu_count(), 4)  # Limit to 4 processes for household processing
    
    # Split households into chunks
    chunk_size = max(1, len(households) // n_processes)
    chunks = []
    
    for i in range(n_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < n_processes - 1 else len(households)
        
        chunk_data = (
            households[start_idx:end_idx],
            block_group_df,
            block_group_sample_size,
            house_choice_mode,
            simple_anova_coefficients,
            budget_reduction_perc
        )
        chunks.append(chunk_data)
    
    # Process in parallel
    with mp.Pool(processes=n_processes) as pool:
        results = pool.map(parallel_household_processing_chunk, chunks)
    
    # Combine results
    all_results = []
    for result in results:
        all_results.extend(result)
    
    return all_results


def parallel_market_matching(utilities_df: pd.DataFrame, n_processes: int = None) -> Dict[str, str]:
    """
    Perform market matching in parallel.
    
    Args:
        utilities_df: DataFrame containing household utilities
        n_processes: Number of processes to use (defaults to CPU count)
        
    Returns:
        Dict[str, str]: Dictionary mapping household names to assigned GEOIDs
    """
    if n_processes is None:
        n_processes = min(mp.cpu_count(), 4)  # Limit to 4 processes for market matching
    
    # Convert to numpy arrays
    geoids = utilities_df['GEOID'].to_numpy()
    households = utilities_df['household'].to_numpy()
    utilities = utilities_df['utility'].to_numpy()
    
    # Get unique households
    unique_households = np.unique(households)
    
    # Split households into chunks
    chunk_size = max(1, len(unique_households) // n_processes)
    chunks = []
    used_geoids = set()
    
    for i in range(n_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < n_processes - 1 else len(unique_households)
        
        chunk_households = unique_households[start_idx:end_idx]
        
        # Get data for this chunk
        chunk_mask = np.isin(households, chunk_households)
        chunk_geoids = geoids[chunk_mask]
        chunk_utilities = utilities[chunk_mask]
        chunk_household_names = households[chunk_mask]
        
        chunk_data = (chunk_geoids, chunk_utilities, chunk_household_names, used_geoids)
        chunks.append(chunk_data)
    
    # Process in parallel
    with mp.Pool(processes=n_processes) as pool:
        results = pool.map(parallel_market_matching_chunk, chunks)
    
    # Combine results
    all_assignments = {}
    for result in results:
        all_assignments.update(result)
    
    return all_assignments


def get_optimal_process_count(task_type: str = 'general') -> int:
    """
    Get optimal number of processes based on task type and system resources.
    
    Args:
        task_type: Type of task ('utility', 'household', 'market', 'general')
        
    Returns:
        int: Optimal number of processes
    """
    cpu_count = mp.cpu_count()
    
    if task_type == 'utility':
        # Utility calculations are CPU-intensive, use more processes
        return min(cpu_count, 8)
    elif task_type == 'household':
        # Household processing involves I/O and moderate computation
        return min(cpu_count, 4)
    elif task_type == 'market':
        # Market matching is memory-intensive, use fewer processes
        return min(cpu_count, 4)
    else:
        # General purpose
        return min(cpu_count, 6) 