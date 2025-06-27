#!/usr/bin/env python3
"""
CHANCE-C Line-by-Line Profiling Script

This script uses line_profiler to provide detailed line-by-line performance analysis
of CHANCE-C simulations. It's particularly useful for identifying bottlenecks within
specific functions.

Usage:
    python scripts/line_profile_chance_c.py [--function] [--output-file]
    
Prerequisites:
    pip install line_profiler
"""

import sys
import os
from pathlib import Path
import argparse

# Add the parent directory to the path to import chance_c
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from chance_c import Model
except ImportError as e:
    print(f"Error importing chance_c: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

try:
    from line_profiler import LineProfiler
except ImportError:
    print("line_profiler not found. Install with: pip install line_profiler")
    sys.exit(1)


def profile_simulation():
    """Profile the main simulation function."""
    print("Creating CHANCE-C model for line profiling...")
    
    # Create model with profiling-friendly settings
    model = Model(
        sensitivity_run=True,  # Faster for profiling
        n_years=2,
        record_time=False,
        progress=False
    )
    
    # Create line profiler
    profiler = LineProfiler()
    
    # Add functions to profile
    profiler.add_function(model.run_simulation)
    profiler.add_function(model.simulator.set_landscape)
    profiler.add_function(model.simulator.convert_initial_population_to_agents)
    profiler.add_function(model.simulator.initialize_available_building_units)
    
    # Add engine profiling
    for engine in model.simulator.engines:
        profiler.add_function(engine.run)
    
    # Enable profiling
    profiler.enable_by_count()
    
    # Run simulation
    print("Running simulation with line profiling...")
    model.run_simulation()
    
    # Disable profiling
    profiler.disable_by_count()
    
    return profiler


def profile_specific_function(function_name: str):
    """Profile a specific function by name."""
    print(f"Profiling function: {function_name}")
    
    # Create model
    model = Model(
        sensitivity_run=True,
        n_years=1,
        record_time=False,
        progress=False
    )
    
    # Create line profiler
    profiler = LineProfiler()
    
    # Map function names to actual functions
    function_map = {
        'run_simulation': model.run_simulation,
        'set_landscape': model.simulator.set_landscape,
        'convert_agents': model.simulator.convert_initial_population_to_agents,
        'init_housing': model.simulator.initialize_available_building_units,
    }
    
    # Add engine functions
    for engine in model.simulator.engines:
        function_map[engine.__class__.__name__] = engine.run
    
    if function_name not in function_map:
        print(f"Function '{function_name}' not found. Available functions:")
        for name in function_map.keys():
            print(f"  - {name}")
        return None
    
    # Add function to profiler
    profiler.add_function(function_map[function_name])
    profiler.enable_by_count()
    
    # Run simulation
    model.run_simulation()
    
    profiler.disable_by_count()
    return profiler


def main():
    """Main profiling function."""
    parser = argparse.ArgumentParser(description="Line-by-line profile CHANCE-C")
    parser.add_argument("--function", type=str, 
                       help="Specific function to profile (optional)")
    parser.add_argument("--output-file", type=str, default="line_profile_results.txt",
                       help="Output file for profiling results")
    
    args = parser.parse_args()
    
    # Run profiling
    if args.function:
        profiler = profile_specific_function(args.function)
        if profiler is None:
            return
    else:
        profiler = profile_simulation()
    
    # Print results
    print(f"\nLine profiling results:")
    print("=" * 50)
    profiler.print_stats()
    
    # Save results to file
    with open(args.output_file, 'w') as f:
        profiler.print_stats(stream=f)
    
    print(f"\nDetailed results saved to: {args.output_file}")
    print("\nKey optimization opportunities:")
    print("- Look for lines with high 'Hits' and 'Time' values")
    print("- Focus on functions with high cumulative time")
    print("- Consider vectorizing loops or using NumPy operations")
    print("- Check for repeated calculations that could be cached")


if __name__ == "__main__":
    main() 