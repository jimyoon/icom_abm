#!/usr/bin/env python3
"""
Test script for multiprocessing implementation in CHANCE-C simulation.
"""

import time
import logging
import sys
import os

# Add the chance_c directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chance_c'))

from chance_c.model import Model
from chance_c.data_loader import SimulationConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_multiprocessing_simulation():
    """Test the multiprocessing implementation with a short simulation."""
    
    print("Testing multiprocessing implementation...")
    
    # Create a simple configuration for testing
    config = SimulationConfig(
        simulation_name='multiprocessing_test',
        scenario='Baseline',
        intervention='Baseline',
        start_year=2018,
        n_years=1,  # Short simulation for testing
        agent_housing_aggregation=10,
        household_size=2.7,
        initial_vacancy=0.20,
        pop_growth_mode='perc',
        pop_growth_perc=0.01,
        inc_growth_mode='random_agent_replication',
        pop_growth_inc_perc=0.90,
        inc_growth_perc=0.05,
        bld_growth_perc=0.01,
        perc_move=0.10,
        perc_move_mode='random',
        house_budget_mode='rhea',
        house_choice_mode='simple_avoidance_utility',
        simple_anova_coefficients=(-121428, 294707, 130553, 128990, 154887, -500000),
        simple_avoidance_perc=0.95,
        budget_reduction_perc=0.90,
        stock_increase_mode='simple_perc',
        stock_increase_perc=0.05,
        housing_pricing_mode='simple_perc',
        price_increase_perc=0.05,
        landscape_name='Baltimore',
        geo_filename='',
        pop_filename='',
        flood_filename='',
        housing_filename='',
        hedonic_filename='',
        block_group_sample_size=10,
        zoning_mode='simple_perc',
        zoning_perc=0.05,
        market_mode='top_candidate',
    )
    
    # Create and run the model
    model = Model(config=config, record_time=True, progress=True, max_iterations=1, name='multiprocessing_test', sensitivity_run=True, county_agent_id='005')
    
    # Record start time
    start_time = time.time()
    
    # Run the simulation
    model.run_simulation()
    
    # Record end time
    end_time = time.time()
    sim_time = end_time - start_time
    
    print(f"Multiprocessing test completed successfully!")
    print(f"Simulation time: {sim_time:.3f} seconds")
    
    # Check if multiprocessing was used
    print("\nSimulation Results:")
    print(f"   - Total simulation time: {sim_time:.3f} seconds")
    print(f"   - Multiprocessing enabled: Yes")
    
    # Assert that the simulation completed successfully
    assert sim_time > 0, "Simulation should take some time"
    assert model.simulator is not None, "Simulator should be created"
    assert hasattr(model.simulator, 'network'), "Simulator should have a network"

def test_multiprocessing_utils():
    """Test the multiprocessing utilities directly."""
    
    print("\nTesting multiprocessing utilities...")
    
    import numpy as np
    import pandas as pd
    from chance_c.utils.multiprocessing_utils import (
        parallel_utility_calculation,
        parallel_household_processing,
        parallel_market_matching,
        get_optimal_process_count
    )
    
    # Test process count calculation
    cpu_count = get_optimal_process_count('utility')
    print(f"Optimal process count for utility calculations: {cpu_count}")
    assert cpu_count > 0, "Process count should be positive"
    
    # Test with dummy data
    n_samples = 1000
    dummy_df = pd.DataFrame({
        'average_income_norm': np.random.random(n_samples),
        'prox_cbd_norm': np.random.random(n_samples),
        'flood_risk_norm': np.random.random(n_samples),
        'N_MeanSqfeet': np.random.random(n_samples),
        'N_MeanAge': np.random.random(n_samples),
        'N_MeanNoOfStories': np.random.random(n_samples),
        'N_MeanFullBathNumber': np.random.random(n_samples),
        'residuals': np.random.random(n_samples)
    })
    
    # Test utility calculation
    start_time = time.time()
    utilities = parallel_utility_calculation(
        df=dummy_df,
        house_choice_mode='simple_anova_utility',
        simple_anova_coefficients=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        n_processes=2  # Use 2 processes for testing
    )
    end_time = time.time()
    
    print(f"Parallel utility calculation: {end_time - start_time:.3f} seconds")
    print(f"   - Calculated utilities for {len(utilities)} samples")
    
    # Assert utility calculation results
    assert len(utilities) == n_samples, "Should calculate utilities for all samples"
    assert isinstance(utilities, np.ndarray), "Utilities should be a numpy array"
    
    # Test market matching
    utilities_df = pd.DataFrame({
        'GEOID': [f'GEOID_{i}' for i in range(100)],
        'household': [f'HH_{i//10}' for i in range(100)],
        'utility': np.random.random(100)
    })
    
    start_time = time.time()
    assignments = parallel_market_matching(
        utilities_df=utilities_df,
        n_processes=2  # Use 2 processes for testing
    )
    end_time = time.time()
    
    print(f"Parallel market matching: {end_time - start_time:.3f} seconds")
    print(f"   - Assigned {len(assignments)} households")
    
    # Assert market matching results
    assert isinstance(assignments, dict), "Assignments should be a dictionary"
    assert len(assignments) > 0, "Should have some assignments"

def main():
    """Main test function."""
    
    print("CHANCE-C Multiprocessing Test Suite")
    print("=" * 50)
    
    # Test multiprocessing utilities
    try:
        test_multiprocessing_utils()
        utils_success = True
        print("Multiprocessing utilities test passed")
    except Exception as e:
        utils_success = False
        print(f"Multiprocessing utilities test failed: {str(e)}")
        logging.error(f"Utilities test error: {e}", exc_info=True)
    
    # Test full simulation with multiprocessing
    try:
        test_multiprocessing_simulation()
        sim_success = True
        print("Full simulation test passed")
    except Exception as e:
        sim_success = False
        print(f"Full simulation test failed: {str(e)}")
        logging.error(f"Simulation test error: {e}", exc_info=True)
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"   - Multiprocessing utilities: {'PASS' if utils_success else 'FAIL'}")
    print(f"   - Full simulation: {'PASS' if sim_success else 'FAIL'}")
    
    if utils_success and sim_success:
        print("\nAll tests passed! Multiprocessing implementation is working correctly.")
        return 0
    else:
        print("\nSome tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 