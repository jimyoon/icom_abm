#!/usr/bin/env python3
"""
Profiling script for chance-c to identify slow functionality for numba optimization.
"""

import cProfile
import pstats
import io
import time
import sys
import os
from pathlib import Path

# Add the chance_c module to the path
sys.path.insert(0, str(Path(__file__).parent))

def run_basic_simulation():
    """Run a basic simulation for profiling."""
    from chance_c.model import Model
    
    # Create a minimal simulation for profiling
    model = Model(
        n_years=1,  # Short simulation for profiling
        agent_housing_aggregation=50,  # Reduce number of agents
        block_group_sample_size=5,  # Reduce sample size
        record_time=True,
        progress=False
    )
    
    print("Starting simulation for profiling...")
    model.run_simulation()
    print("Simulation completed.")

def profile_simulation():
    """Profile the simulation using cProfile."""
    print("Profiling chance-c simulation...")
    
    # Create profiler
    pr = cProfile.Profile()
    pr.enable()
    
    # Run simulation
    run_basic_simulation()
    
    # Stop profiler
    pr.disable()
    
    # Create stats
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(50)  # Top 50 functions by cumulative time
    
    # Print results
    print("\n" + "="*80)
    print("PROFILING RESULTS - Top 50 functions by cumulative time:")
    print("="*80)
    print(s.getvalue())
    
    # Save detailed stats to file
    with open('chance_c_profile_stats.txt', 'w') as f:
        ps = pstats.Stats(pr, stream=f).sort_stats('cumulative')
        ps.print_stats()
    
    print(f"\nDetailed stats saved to: chance_c_profile_stats.txt")
    
    return pr

def analyze_slow_functions(pr):
    """Analyze the profiler results to identify functions suitable for numba optimization."""
    print("\n" + "="*80)
    print("ANALYSIS OF FUNCTIONS SUITABLE FOR NUMBA OPTIMIZATION:")
    print("="*80)
    
    # Get stats
    stats = pstats.Stats(pr)
    
    # Look for functions with high call counts and/or high time per call
    potential_numba_candidates = []
    
    # Get the stats as a list of tuples
    stats_list = stats.get_stats_profile()
    
    for func_info in stats_list:
        # Extract function info - stats are in format (filename, line_number, function_name, call_count, total_time, cumulative_time, callers, callees)
        filename, line_number, func_name, call_count, total_time, cumulative_time, callers, callees = func_info
        
        # Filter for potential numba candidates
        # Look for functions with:
        # 1. High call counts (>100)
        # 2. High time per call (>0.001 seconds)
        # 3. Mathematical operations (likely to benefit from numba)
        if (call_count > 100 or total_time > 0.001) and 'chance_c' in func_name:
            time_per_call = total_time / call_count if call_count > 0 else 0
            potential_numba_candidates.append({
                'name': func_name,
                'filename': filename,
                'calls': call_count,
                'total_time': total_time,
                'time_per_call': time_per_call
            })
    
    # Sort by total time
    potential_numba_candidates.sort(key=lambda x: x['total_time'], reverse=True)
    
    print(f"Found {len(potential_numba_candidates)} potential numba optimization candidates:")
    print()
    
    for i, candidate in enumerate(potential_numba_candidates[:20]):  # Top 20
        print(f"{i+1:2d}. {candidate['name']}")
        print(f"     File: {candidate['filename']}")
        print(f"     Calls: {candidate['calls']:,}")
        print(f"     Total time: {candidate['total_time']:.4f}s")
        print(f"     Time per call: {candidate['time_per_call']:.6f}s")
        print()

def profile_specific_engines():
    """Profile specific model engines that are likely to be slow."""
    print("\n" + "="*80)
    print("PROFILING SPECIFIC MODEL ENGINES:")
    print("="*80)
    
    from chance_c.model import Model
    
    # Create model
    model = Model(
        n_years=1,
        agent_housing_aggregation=50,
        block_group_sample_size=5,
        record_time=True,
        progress=False
    )
    
    # Profile each engine separately
    engines_to_profile = [
        'NewAgentLocation',
        'HousingMarket', 
        'ExistingAgentLocation',
        'LandscapeStatistics',
        'HousingPricing'
    ]
    
    for engine_name in engines_to_profile:
        print(f"\nProfiling {engine_name}...")
        
        pr = cProfile.Profile()
        pr.enable()
        
        # Run simulation (this will include the engine)
        model.run_simulation()
        
        pr.disable()
        
        # Get stats for this engine
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Top 10 functions
        
        # Filter for engine-specific functions
        output = s.getvalue()
        engine_lines = [line for line in output.split('\n') if engine_name in line]
        
        if engine_lines:
            print(f"Top functions in {engine_name}:")
            for line in engine_lines[:5]:
                print(f"  {line}")
        else:
            print(f"No specific {engine_name} functions found in top results")

if __name__ == "__main__":
    print("Chance-C Profiling Tool")
    print("="*50)
    
    # Run main profiling
    profiler = profile_simulation()
    
    # Analyze results
    analyze_slow_functions(profiler)
    
    # Profile specific engines
    profile_specific_engines()
    
    print("\nProfiling complete!")
    print("Check chance_c_profile_stats.txt for detailed results.") 