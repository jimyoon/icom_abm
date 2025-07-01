#!/usr/bin/env python3
"""
Test script to demonstrate random seed functionality in the Model class.

This script shows how setting a random seed ensures reproducible results
across multiple simulation runs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chance_c import Model, SimulationConfig
import pandas as pd


def run_test_simulation(seed=None, name="test"):
    """Run a test simulation with optional random seed."""
    print(f"\n{'='*50}")
    print(f"Running simulation: {name}")
    if seed is not None:
        print(f"Random seed: {seed}")
    else:
        print("No random seed set")
    print(f"{'='*50}")
    
    # Create a minimal configuration for testing
    config = SimulationConfig(
        simulation_name=f"test_{name}",
        start_year=2018,
        n_years=1,  # Short simulation for testing
        agent_housing_aggregation=100,  # Larger aggregation for faster test
        pop_growth_perc=0.01,
        perc_move=0.05,
        random_seed=seed
    )
    
    # Create and run model
    model = Model(config=config, random_seed=seed)
    model.run_simulation()
    
    # Get some results to compare
    final_population = model.get_history('total_population')[-1]
    print(f"Final total population: {final_population}")
    
    return final_population


def main():
    """Main test function."""
    print("Testing Random Seed Functionality")
    print("="*50)
    
    # Test 1: No seed (random behavior)
    result1 = run_test_simulation(seed=None, name="no_seed_1")
    result2 = run_test_simulation(seed=None, name="no_seed_2")
    
    print(f"\nResults without seed:")
    print(f"Run 1: {result1}")
    print(f"Run 2: {result2}")
    print(f"Same result: {result1 == result2}")
    
    # Test 2: With fixed seed (reproducible behavior)
    result3 = run_test_simulation(seed=42, name="with_seed_1")
    result4 = run_test_simulation(seed=42, name="with_seed_2")
    
    print(f"\nResults with seed=42:")
    print(f"Run 1: {result3}")
    print(f"Run 2: {result4}")
    print(f"Same result: {result3 == result4}")
    
    # Test 3: Different seeds (different results)
    result5 = run_test_simulation(seed=123, name="different_seed")
    
    print(f"\nResults with different seeds:")
    print(f"Seed 42: {result3}")
    print(f"Seed 123: {result5}")
    print(f"Same result: {result3 == result5}")
    
    print(f"\n{'='*50}")
    print("Test Summary:")
    print("- Without seed: Results vary between runs")
    print("- With same seed: Results are reproducible")
    print("- With different seeds: Results differ")
    print("="*50)


if __name__ == "__main__":
    main() 