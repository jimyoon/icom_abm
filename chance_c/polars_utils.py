"""
Polars-optimized utility functions for chance-c performance improvements.
"""

import polars as pl
import numpy as np
from typing import List, Dict, Any, Optional, Tuple


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
    price_col: str,
    weight_col: str,
    budget: float,
    n_sample: int
) -> pl.DataFrame:
    """
    Fast filtering and sampling using Polars.
    
    Args:
        df: Input DataFrame
        price_col: Column name for prices
        weight_col: Column name for weights
        budget: Budget constraint
        n_sample: Number of samples to take
        
    Returns:
        Sampled DataFrame
    """
    # Fast filtering with Polars
    filtered = df.filter(pl.col(price_col) <= budget)
    
    if filtered.height == 0:
        return pl.DataFrame()
    
    # Fast sampling with weights
    try:
        sampled = filtered.sample(n=min(n_sample, filtered.height), with_replacement=True, weights=weight_col)
        return sampled
    except Exception:
        # Fallback to uniform sampling if weights fail
        return filtered.sample(n=min(n_sample, filtered.height), with_replacement=True)


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


def convert_polars_to_pandas(pdf: pl.DataFrame) -> 'pandas.DataFrame':
    """
    Convert Polars DataFrame to pandas DataFrame efficiently.
    
    Args:
        pdf: Polars DataFrame
        
    Returns:
        Pandas DataFrame
    """
    return pdf.to_pandas()


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