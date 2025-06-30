"""
Polars-optimized utility functions for chance-c performance improvements.
"""

import polars as pl
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging


def fast_concat_dataframes(dfs: List[pl.DataFrame]) -> pl.DataFrame:
    """
    Fast concatenation of Polars DataFrames.
    
    Args:
        dfs: List of DataFrames to concatenate
        
    Returns:
        Concatenated DataFrame
    """
    if not dfs:
        return pl.DataFrame()
    if len(dfs) == 1:
        return dfs[0]
    
    # Use Polars' fast concat
    return pl.concat(dfs, how="vertical")


def fast_filter_and_sample_polars(
    df: pl.DataFrame,
    filter_condition: pl.Expr,
    sample_size: int,
    weights_col: Optional[str] = None
) -> pl.DataFrame:
    """
    Fast filtering and sampling using Polars.
    
    Args:
        df: Polars DataFrame to filter and sample
        filter_condition: Polars expression for filtering
        sample_size: Number of rows to sample
        weights_col: Optional column name for weighted sampling
        
    Returns:
        Polars DataFrame with sampled rows
    """
    # Apply filter
    filtered_df = df.filter(filter_condition)
    
    if len(filtered_df) == 0:
        return pl.DataFrame()
    
    # Sample rows
    if weights_col and weights_col in filtered_df.columns:
        # Weighted sampling
        return filtered_df.sample(n=min(sample_size, len(filtered_df)), with_replacement=False, weights=weights_col)
    else:
        # Uniform sampling
        return filtered_df.sample(n=min(sample_size, len(filtered_df)), with_replacement=False)


def fast_boolean_indexing_polars(
    df: pl.DataFrame,
    condition: pl.Expr
) -> pl.DataFrame:
    """
    Fast boolean indexing using Polars expressions.
    
    Args:
        df: Input DataFrame
        condition: Polars expression for filtering
        
    Returns:
        Filtered DataFrame
    """
    return df.filter(condition)


def convert_pandas_to_polars(pdf: 'pandas.DataFrame') -> pl.DataFrame:
    """
    Convert pandas DataFrame to Polars DataFrame efficiently.
    
    Args:
        pdf: Pandas DataFrame
        
    Returns:
        Polars DataFrame
    """
    return pl.from_pandas(pdf)


def convert_polars_to_pandas(df: pl.DataFrame) -> pd.DataFrame:
    """
    Convert Polars DataFrame to pandas DataFrame efficiently.
    
    Args:
        df: Polars DataFrame
        
    Returns:
        pandas DataFrame
    """
    return df.to_pandas()


def fast_groupby_agg_polars(
    df: pl.DataFrame,
    group_cols: List[str],
    agg_exprs: List[pl.Expr]
) -> pl.DataFrame:
    """
    Fast groupby aggregation using Polars.
    
    Args:
        df: Input DataFrame
        group_cols: Columns to group by
        agg_exprs: Aggregation expressions
        
    Returns:
        Aggregated DataFrame
    """
    return df.group_by(group_cols).agg(agg_exprs)


def fast_join_polars(
    left: pl.DataFrame,
    right: pl.DataFrame,
    on: str,
    how: str = "inner"
) -> pl.DataFrame:
    """
    Fast join using Polars.
    
    Args:
        left: Left DataFrame
        right: Right DataFrame
        on: Join column
        how: Join type ("inner", "left", "right", "outer")
        
    Returns:
        Joined DataFrame
    """
    return left.join(right, on=on, how=how)


def fast_sort_polars(
    df: pl.DataFrame,
    by: List[str],
    descending: bool = False
) -> pl.DataFrame:
    """
    Fast sorting using Polars.
    
    Args:
        df: Input DataFrame
        by: Columns to sort by
        descending: Sort in descending order
        
    Returns:
        Sorted DataFrame
    """
    return df.sort(by, descending=descending)


def fast_merge_polars(
    left_df: pl.DataFrame,
    right_df: pl.DataFrame,
    left_on: str,
    right_on: str,
    how: str = 'left'
) -> pl.DataFrame:
    """
    Fast merge (join) for Polars DataFrames, dropping duplicate columns after join.
    
    Args:
        left_df: Left Polars DataFrame
        right_df: Right Polars DataFrame
        left_on: Column name in left DataFrame for joining
        right_on: Column name in right DataFrame for joining
        how: Join type ('left', 'right', 'inner', 'outer')
        
    Returns:
        Merged Polars DataFrame
    """
    merged = left_df.join(right_df, left_on=left_on, right_on=right_on, how=how, suffix="_right")
    # Drop duplicate columns (those ending with '_right' if the base column exists)
    base_cols = set(left_df.columns)
    drop_cols = [col for col in merged.columns if col.endswith('_right') and col[:-6] in base_cols]
    return merged.drop(drop_cols)


def fast_statistics_polars(
    df: pl.DataFrame,
    stat_cols: List[str],
    group_col: Optional[str] = None
) -> pl.DataFrame:
    """
    Fast statistical calculations using Polars.
    
    Args:
        df: Polars DataFrame
        stat_cols: List of column names for statistics
        group_col: Optional column name for grouping
        
    Returns:
        Polars DataFrame with statistics
    """
    if group_col:
        # Grouped statistics
        agg_exprs = []
        for col in stat_cols:
            agg_exprs.extend([
                pl.col(col).mean().alias(f"{col}_mean"),
                pl.col(col).std().alias(f"{col}_std"),
                pl.col(col).min().alias(f"{col}_min"),
                pl.col(col).max().alias(f"{col}_max"),
                pl.col(col).count().alias(f"{col}_count")
            ])
        return df.group_by(group_col).agg(agg_exprs)
    else:
        # Overall statistics
        agg_exprs = []
        for col in stat_cols:
            agg_exprs.extend([
                pl.col(col).mean().alias(f"{col}_mean"),
                pl.col(col).std().alias(f"{col}_std"),
                pl.col(col).min().alias(f"{col}_min"),
                pl.col(col).max().alias(f"{col}_max"),
                pl.col(col).count().alias(f"{col}_count")
            ])
        return df.select(agg_exprs)


def fast_normalize_polars(
    df: pl.DataFrame,
    cols_to_normalize: List[str],
    method: str = 'max'
) -> pl.DataFrame:
    """
    Fast normalization using Polars.
    
    Args:
        df: Polars DataFrame
        cols_to_normalize: List of column names to normalize
        method: Normalization method ('max', 'minmax', 'zscore')
        
    Returns:
        Polars DataFrame with normalized columns
    """
    result_df = df.clone()
    
    for col in cols_to_normalize:
        if method == 'max':
            max_val = df.select(pl.col(col).max()).item()
            if max_val != 0:
                result_df = result_df.with_columns(pl.col(col) / max_val)
        elif method == 'minmax':
            min_val = df.select(pl.col(col).min()).item()
            max_val = df.select(pl.col(col).max()).item()
            range_val = max_val - min_val
            if range_val != 0:
                result_df = result_df.with_columns((pl.col(col) - min_val) / range_val)
        elif method == 'zscore':
            mean_val = df.select(pl.col(col).mean()).item()
            std_val = df.select(pl.col(col).std()).item()
            if std_val != 0:
                result_df = result_df.with_columns((pl.col(col) - mean_val) / std_val)
    
    return result_df


def fast_conditional_update_polars(
    df: pl.DataFrame,
    condition: pl.Expr,
    update_expr: pl.Expr
) -> pl.DataFrame:
    """
    Fast conditional updates using Polars.
    
    Args:
        df: Polars DataFrame
        condition: Polars expression for condition
        update_expr: Polars expression for update
        
    Returns:
        Updated Polars DataFrame
    """
    return df.with_columns(pl.when(condition).then(update_expr).otherwise(pl.col("*")))


def fast_batch_operations_polars(
    df: pl.DataFrame,
    operations: List[Dict[str, Any]]
) -> pl.DataFrame:
    """
    Fast batch operations using Polars.
    
    Args:
        df: Polars DataFrame
        operations: List of operation dictionaries with keys:
                   - 'type': 'filter', 'select', 'with_columns', 'group_by'
                   - 'expr': Polars expression
                   - 'args': Additional arguments
                   
    Returns:
        Polars DataFrame after applying all operations
    """
    result_df = df
    
    for op in operations:
        op_type = op['type']
        expr = op['expr']
        
        if op_type == 'filter':
            result_df = result_df.filter(expr)
        elif op_type == 'select':
            result_df = result_df.select(expr)
        elif op_type == 'with_columns':
            result_df = result_df.with_columns(expr)
        elif op_type == 'group_by':
            agg_exprs = op.get('agg_exprs', [])
            result_df = result_df.group_by(expr).agg(agg_exprs)
    
    return result_df


def optimize_polars_memory(df: pl.DataFrame) -> pl.DataFrame:
    """
    Optimize memory usage of Polars DataFrame.
    
    Args:
        df: Polars DataFrame
        
    Returns:
        Memory-optimized Polars DataFrame
    """
    # Polars automatically optimizes memory usage, but we can force some optimizations
    return df.cast(pl.all().cast(pl.Float32, strict=False))


def fast_utility_calculation_polars(
    df: pl.DataFrame,
    sqfeet_col: str,
    age_col: str,
    stories_col: str,
    baths_col: str,
    coefficients: List[float]
) -> pl.DataFrame:
    """
    Fast utility calculation using Polars expressions.
    
    Args:
        df: Polars DataFrame with housing data
        sqfeet_col: Column name for square footage
        age_col: Column name for age
        stories_col: Column name for stories
        baths_col: Column name for bathrooms
        coefficients: List of coefficients for utility calculation
        
    Returns:
        Polars DataFrame with utility column added
    """
    if len(coefficients) >= 4:
        utility_expr = (
            coefficients[0] * pl.col(sqfeet_col) +
            coefficients[1] * pl.col(age_col) +
            coefficients[2] * pl.col(stories_col) +
            coefficients[3] * pl.col(baths_col)
        )
        
        if len(coefficients) >= 5:
            utility_expr = utility_expr + coefficients[4]
        
        return df.with_columns(utility_expr.alias('utility'))
    else:
        logging.warning("Insufficient coefficients for utility calculation")
        return df.with_columns(pl.lit(0.0).alias('utility'))


def fast_market_matching_polars(
    utilities_df: pl.DataFrame,
    geoid_col: str = 'GEOID',
    household_col: str = 'household',
    utility_col: str = 'utility'
) -> Dict[str, str]:
    """
    Fast market matching using Polars.
    
    Args:
        utilities_df: Polars DataFrame with utilities
        geoid_col: Column name for GEOID
        household_col: Column name for household
        utility_col: Column name for utility
        
    Returns:
        Dictionary mapping household names to assigned GEOIDs
    """
    # Sort by utility (descending) and get unique households
    sorted_df = utilities_df.sort(utility_col, descending=True)
    
    # Get unique households
    unique_households = sorted_df.select(pl.col(household_col)).unique().to_series().to_list()
    
    assignments = {}
    used_geoids = set()
    
    for household in unique_households:
        # Get options for this household
        household_options = sorted_df.filter(pl.col(household_col) == household)
        
        if len(household_options) == 0:
            assignments[household] = 'outmigrated'
            continue
        
        # Try to assign the best available location
        assigned = False
        for row in household_options.iter_rows(named=True):
            geoid = row[geoid_col]
            if geoid not in used_geoids:
                assignments[household] = geoid
                used_geoids.add(geoid)
                assigned = True
                break
        
        if not assigned:
            assignments[household] = 'outmigrated'
    
    return assignments


def fast_market_matching_parallel_polars(
    utilities_df: pl.DataFrame,
    geoid_col: str = 'GEOID',
    household_col: str = 'household',
    utility_col: str = 'utility',
    batch_size: int = 1000
) -> Dict[str, str]:
    """
    Fast market matching using Polars with parallel processing and optimized sorting.
    
    Args:
        utilities_df: Polars DataFrame with utilities
        geoid_col: Column name for GEOID
        household_col: Column name for household
        utility_col: Column name for utility
        batch_size: Size of batches for parallel processing
        
    Returns:
        Dictionary mapping household names to assigned GEOIDs
    """
    # Pre-sort by utility (descending) for better performance
    sorted_df = utilities_df.sort(utility_col, descending=True)
    
    # Get unique households and their best options
    household_best_options = (
        sorted_df
        .group_by(household_col)
        .agg([
            pl.col(geoid_col).first().alias('best_geoid'),
            pl.col(utility_col).first().alias('best_utility')
        ])
        .sort('best_utility', descending=True)
    )
    
    # Convert to numpy arrays for faster processing
    households = household_best_options.select(pl.col(household_col)).to_series().to_numpy()
    geoids = household_best_options.select(pl.col('best_geoid')).to_series().to_numpy()
    
    # Use numpy-based assignment for better performance
    assignments = {}
    used_geoids = set()
    
    # Process in batches for better memory management
    for i in range(0, len(households), batch_size):
        batch_end = min(i + batch_size, len(households))
        batch_households = households[i:batch_end]
        batch_geoids = geoids[i:batch_end]
        
        for household, geoid in zip(batch_households, batch_geoids):
            if geoid not in used_geoids:
                assignments[household] = geoid
                used_geoids.add(geoid)
            else:
                # Find next best option for this household
                household_options = sorted_df.filter(pl.col(household_col) == household)
                assigned = False
                
                for row in household_options.iter_rows(named=True):
                    option_geoid = row[geoid_col]
                    if option_geoid not in used_geoids:
                        assignments[household] = option_geoid
                        used_geoids.add(option_geoid)
                        assigned = True
                        break
                
                if not assigned:
                    assignments[household] = 'outmigrated'
    
    return assignments


def fast_market_matching_numba_optimized(
    utilities_df: pl.DataFrame,
    geoid_col: str = 'GEOID',
    household_col: str = 'household',
    utility_col: str = 'utility'
) -> Dict[str, str]:
    """
    Fast market matching using Numba-optimized algorithms.
    
    Args:
        utilities_df: Polars DataFrame with utilities
        geoid_col: Column name for GEOID
        household_col: Column name for household
        utility_col: Column name for utility
        
    Returns:
        Dictionary mapping household names to assigned GEOIDs
    """
    from chance_c.utils.numba_utils import fast_market_matching_numba
    
    # Convert to numpy arrays for numba processing
    households = utilities_df.select(pl.col(household_col)).to_series().to_numpy()
    geoids = utilities_df.select(pl.col(geoid_col)).to_series().to_numpy()
    utilities = utilities_df.select(pl.col(utility_col)).to_series().to_numpy()
    
    # Use numba-optimized market matching
    assigned_households, assigned_geoids = fast_market_matching_numba(households, geoids, utilities)
    
    # Convert back to dictionary
    assignments = {}
    for household, geoid in zip(assigned_households, assigned_geoids):
        assignments[household] = geoid
    
    return assignments


def fast_market_matching_hybrid(
    utilities_df: pl.DataFrame,
    geoid_col: str = 'GEOID',
    household_col: str = 'household',
    utility_col: str = 'utility',
    threshold: int = 1000
) -> Dict[str, str]:
    """
    Hybrid market matching that chooses the best algorithm based on data size.
    
    Args:
        utilities_df: Polars DataFrame with utilities
        geoid_col: Column name for GEOID
        household_col: Column name for household
        utility_col: Column name for utility
        threshold: Threshold for choosing algorithm
        
    Returns:
        Dictionary mapping household names to assigned GEOIDs
    """
    # Choose algorithm based on data size
    if len(utilities_df) < threshold:
        # For small datasets, use simple Polars approach
        return fast_market_matching_polars(utilities_df, geoid_col, household_col, utility_col)
    else:
        # For large datasets, use parallel approach
        return fast_market_matching_parallel_polars(utilities_df, geoid_col, household_col, utility_col) 