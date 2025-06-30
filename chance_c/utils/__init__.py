"""
Utility modules for chance-c performance optimizations.
"""

# Import from numba_utils
from .numba_utils import (
    calculate_distances_2d,
    build_spatial_grid,
    find_nearest_neighbor_spatial,
    find_nearest_neighbor,
    calculate_utilities_vectorized,
    calculate_utilities_with_flood_vectorized,
    calculate_cobb_douglas_utilities,
    filter_and_sample,
    find_top_candidates,
    fast_market_matching_numba,
    fast_market_matching_batch_numba,
    fast_sort_utilities_numba
)

# Import from polars_utils
from .polars_utils import (
    fast_concat_dataframes,
    fast_filter_and_sample_polars,
    fast_boolean_indexing_polars,
    convert_pandas_to_polars,
    convert_polars_to_pandas,
    fast_groupby_agg_polars,
    fast_join_polars,
    fast_sort_polars,
    fast_merge_polars,
    fast_statistics_polars,
    fast_normalize_polars,
    fast_conditional_update_polars,
    fast_batch_operations_polars,
    optimize_polars_memory,
    fast_utility_calculation_polars,
    fast_market_matching_polars,
    fast_market_matching_parallel_polars,
    fast_market_matching_numba_optimized,
    fast_market_matching_hybrid
)

# Import from multiprocessing_utils
from .multiprocessing_utils import (
    parallel_utility_calculation_chunk,
    parallel_household_processing_chunk,
    parallel_market_matching_chunk,
    parallel_utility_calculation,
    parallel_household_processing,
    parallel_market_matching,
    get_optimal_process_count
)

__all__ = [
    # numba_utils
    'calculate_distances_2d',
    'build_spatial_grid',
    'find_nearest_neighbor_spatial',
    'find_nearest_neighbor',
    'calculate_utilities_vectorized',
    'calculate_utilities_with_flood_vectorized',
    'calculate_cobb_douglas_utilities',
    'filter_and_sample',
    'find_top_candidates',
    'fast_market_matching_numba',
    'fast_market_matching_batch_numba',
    'fast_sort_utilities_numba',
    
    # polars_utils
    'fast_concat_dataframes',
    'fast_filter_and_sample_polars',
    'fast_boolean_indexing_polars',
    'convert_pandas_to_polars',
    'convert_polars_to_pandas',
    'fast_groupby_agg_polars',
    'fast_join_polars',
    'fast_sort_polars',
    'fast_merge_polars',
    'fast_statistics_polars',
    'fast_normalize_polars',
    'fast_conditional_update_polars',
    'fast_batch_operations_polars',
    'optimize_polars_memory',
    'fast_utility_calculation_polars',
    'fast_market_matching_polars',
    'fast_market_matching_parallel_polars',
    'fast_market_matching_numba_optimized',
    'fast_market_matching_hybrid',
    
    # multiprocessing_utils
    'parallel_utility_calculation_chunk',
    'parallel_household_processing_chunk',
    'parallel_market_matching_chunk',
    'parallel_utility_calculation',
    'parallel_household_processing',
    'parallel_market_matching',
    'get_optimal_process_count'
]
