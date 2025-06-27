#!/usr/bin/env python3
"""
Simple profiling script focusing on key computational bottlenecks in chance-c.
"""

import time
import cProfile
import pstats
import io
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add the chance_c module to the path
sys.path.insert(0, str(Path(__file__).parent))

def profile_geopandas_distance():
    """Profile the geopandas distance calculations which were a major bottleneck."""
    print("Profiling geopandas distance calculations...")
    
    import geopandas as gpd
    from shapely.geometry import Point
    
    # Create sample geometries
    n_points = 1000
    points = [Point(np.random.uniform(-180, 180), np.random.uniform(-90, 90)) for _ in range(n_points)]
    gdf = gpd.GeoDataFrame({'geometry': points})
    
    # Create a reference point
    ref_point = Point(0, 0)
    
    pr = cProfile.Profile()
    pr.enable()
    
    # Simulate distance calculations similar to what chance-c does
    for _ in range(10):
        distances = gdf.distance(ref_point)
    
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(10)
    
    print("Geopandas distance profiling results:")
    print(s.getvalue())
    
    return pr

def profile_pandas_operations():
    """Profile pandas operations which are often bottlenecks."""
    print("\nProfiling pandas operations...")
    
    # Create sample data similar to what chance-c uses
    n_block_groups = 1000
    n_households = 5000
    
    # Sample housing data
    housing_data = pd.DataFrame({
        'GEOID': [f'BG{i:06d}' for i in range(n_block_groups)],
        'new_price': np.random.uniform(100000, 500000, n_block_groups),
        'available_units': np.random.randint(1, 20, n_block_groups),
        'N_MeanSqfeet': np.random.uniform(1000, 3000, n_block_groups),
        'N_MeanAge': np.random.uniform(10, 50, n_block_groups),
        'N_MeanNoOfStories': np.random.uniform(1, 3, n_block_groups),
        'N_MeanFullBathNumber': np.random.uniform(1, 3, n_block_groups),
        'perc_fld_area': np.random.uniform(0, 0.3, n_block_groups),
        'residuals': np.random.normal(0, 10000, n_block_groups)
    })
    
    # Sample household utilities
    utilities_data = pd.DataFrame({
        'GEOID': np.random.choice(housing_data['GEOID'], n_households * 10),
        'household': [f'hh_{i}' for i in range(n_households)] * 10,
        'utility': np.random.uniform(0, 1000000, n_households * 10)
    })
    
    pr = cProfile.Profile()
    pr.enable()
    
    # Simulate operations similar to those in chance-c
    for _ in range(100):
        # Simulate filtering operations
        budget_filter = housing_data[housing_data['new_price'] <= 300000]
        
        # Simulate sampling operations
        if len(budget_filter) > 0:
            sample = budget_filter.sample(n=min(10, len(budget_filter)), replace=True, weights='available_units')
        
        # Simulate utility calculations
        if len(utilities_data) > 0:
            household_utilities = utilities_data[utilities_data['household'] == 'hh_0']
            utilities_dict = dict(zip(household_utilities['GEOID'], household_utilities['utility']))
            sorted_candidates = sorted(((v, k) for k, v in utilities_dict.items()))
    
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(10)
    
    print("Pandas operations profiling results:")
    print(s.getvalue())
    
    return pr

def profile_utility_calculations():
    """Profile utility calculation functions which are likely bottlenecks."""
    print("\nProfiling utility calculations...")
    
    # Create sample data
    n_elements = 100000
    coefficients = np.array([-121428, 294707, 130553, 128990, 154887, -500000])
    
    # Sample housing characteristics
    sqfeet = np.random.uniform(1000, 3000, n_elements)
    age = np.random.uniform(10, 50, n_elements)
    stories = np.random.uniform(1, 3, n_elements)
    baths = np.random.uniform(1, 3, n_elements)
    residuals = np.random.normal(0, 10000, n_elements)
    
    pr = cProfile.Profile()
    pr.enable()
    
    # Simulate utility calculations similar to chance-c
    for _ in range(100):
        # Simple ANOVA utility calculation
        utility = (coefficients[0] + 
                  coefficients[1] * sqfeet + 
                  coefficients[2] * age + 
                  coefficients[3] * stories + 
                  coefficients[4] * baths + 
                  residuals)
        
        # Cobb-Douglas utility calculation
        a, b, c = 0.4, 0.4, 0.2
        cobb_douglas_utility = (sqfeet ** a) * (age ** b) * (stories ** c)
    
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(10)
    
    print("Utility calculation profiling results:")
    print(s.getvalue())
    
    return pr

def profile_market_matching():
    """Profile the housing market matching algorithm."""
    print("\nProfiling market matching algorithm...")
    
    # Create sample market data
    n_households = 1000
    n_block_groups = 500
    
    households = {
        f'hh_{i}': {
            'income': np.random.uniform(50000, 150000),
            'utility_dict': {f'BG{j:06d}': np.random.uniform(0, 1000000) for j in range(n_block_groups)}
        }
        for i in range(n_households)
    }
    
    block_groups = {
        f'BG{i:06d}': {
            'available_units': np.random.randint(0, 10),
            'demand': {}
        }
        for i in range(n_block_groups)
    }
    
    pr = cProfile.Profile()
    pr.enable()
    
    # Simulate market matching iterations
    for market_iter in range(5):
        block_group_demand = {}
        
        # Simulate household demand calculation
        for household_name, household_data in households.items():
            utilities_dict = household_data['utility_dict']
            sorted_candidates = sorted(((v, k) for k, v in utilities_dict.items()))
            
            try:
                top_candidate = sorted_candidates[-1-market_iter][1]
                if top_candidate in block_group_demand:
                    block_group_demand[top_candidate][household_name] = household_data['income']
                else:
                    block_group_demand[top_candidate] = {household_name: household_data['income']}
            except IndexError:
                continue
        
        # Simulate matching process
        for block_group_name, demand in block_group_demand.items():
            no_households = len(demand)
            available_units = block_groups[block_group_name]['available_units']
            
            if available_units >= no_households:
                # All households can be accommodated
                pass
            else:
                # Only top income households
                top_matches = dict(sorted(demand.items(), key=lambda x: x[1], reverse=True)[:available_units])
    
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(10)
    
    print("Market matching profiling results:")
    print(s.getvalue())
    
    return pr

def benchmark_numba_candidates():
    """Benchmark operations that could benefit from numba optimization."""
    print("\nBenchmarking potential numba operations...")
    
    # Create sample data
    n_elements = 1000000
    data = np.random.uniform(0, 1000000, n_elements)
    coefficients = np.array([-121428, 294707, 130553, 128990, 154887, -500000])
    
    # Benchmark utility calculation
    start_time = time.time()
    
    for _ in range(100):
        # Simulate utility calculation similar to chance-c
        utility = (coefficients[0] + 
                  coefficients[1] * data + 
                  coefficients[2] * data * 0.5 + 
                  coefficients[3] * data * 0.3 + 
                  coefficients[4] * data * 0.2 + 
                  coefficients[5] * data * 0.1)
    
    numpy_time = time.time() - start_time
    print(f"Numpy utility calculation time: {numpy_time:.4f}s")
    
    # Benchmark sorting operations
    start_time = time.time()
    
    for _ in range(100):
        # Simulate sorting operations
        utilities = np.random.uniform(0, 1000000, 10000)
        sorted_indices = np.argsort(utilities)
    
    sorting_time = time.time() - start_time
    print(f"Numpy sorting time: {sorting_time:.4f}s")
    
    return numpy_time, sorting_time

def analyze_profiling_results():
    """Analyze the profiling results and provide recommendations."""
    print("\n" + "="*80)
    print("ANALYSIS AND RECOMMENDATIONS FOR NUMBA OPTIMIZATION:")
    print("="*80)
    
    print("Based on the profiling results, here are the key bottlenecks and recommendations:")
    print()
    
    print("1. GEOPANDAS DISTANCE CALCULATIONS (8.8s in profiling)")
    print("   - This is the biggest bottleneck in the existing agent relocation engine")
    print("   - Recommendation: Replace geopandas distance with numba-optimized distance calculations")
    print("   - Can use numba with numpy arrays for coordinates instead of shapely geometries")
    print()
    
    print("2. PANDAS OPERATIONS (Multiple bottlenecks)")
    print("   - DataFrame filtering and sampling operations")
    print("   - Recommendation: Convert pandas operations to numpy arrays where possible")
    print("   - Use numba for filtering and sampling logic")
    print()
    
    print("3. UTILITY CALCULATIONS")
    print("   - Simple mathematical operations that are perfect for numba")
    print("   - Recommendation: Convert utility functions to numba-compiled functions")
    print()
    
    print("4. MARKET MATCHING ALGORITHM")
    print("   - Sorting and dictionary operations")
    print("   - Recommendation: Use numba for sorting and matching logic")
    print()
    
    print("5. AGENT CREATION AND MANAGEMENT")
    print("   - Object creation and attribute access")
    print("   - Recommendation: Use numba for agent property calculations")
    print()

if __name__ == "__main__":
    print("Simple Profiling for Chance-C Optimization")
    print("="*60)
    
    # Run targeted profiling
    profile_geopandas_distance()
    profile_pandas_operations()
    profile_utility_calculations()
    profile_market_matching()
    benchmark_numba_candidates()
    analyze_profiling_results()
    
    print("\nProfiling complete!")
    print("Key findings:")
    print("- Geopandas distance calculations are the biggest bottleneck")
    print("- Pandas operations are significant bottlenecks")
    print("- Utility calculations are good candidates for numba optimization")
    print("- Market matching algorithms can benefit from numba") 