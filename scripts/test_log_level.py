#!/usr/bin/env python3
"""
Test script to demonstrate log level functionality in the Model class.

This script shows how different log levels affect the output verbosity.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chance_c import Model, SimulationConfig


def test_log_level(level, name="test"):
    """Test a specific log level."""
    print(f"\n{'='*60}")
    print(f"Testing log level: {level}")
    print(f"{'='*60}")
    
    # Create a minimal configuration for testing
    config = SimulationConfig(
        simulation_name=f"log_test_{name}",
        start_year=2018,
        n_years=1,  # Short simulation for testing
        agent_housing_aggregation=100,  # Larger aggregation for faster test
        pop_growth_perc=0.01,
        perc_move=0.05,
        log_level=level
    )
    
    # Create and run model
    model = Model(config=config, log_level=level)
    print(f"Model config log_level: {model.config.log_level}")
    
    # Run a short simulation to see logging output
    try:
        model.run_simulation()
        print(f"Simulation completed with log level: {level}")
    except Exception as e:
        print(f"Simulation failed: {e}")
    
    return model


def main():
    """Test different log levels."""
    print("Log Level Functionality Test")
    print("="*60)
    print("This script demonstrates how different log levels affect output verbosity.\n")
    
    # Test different log levels
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    
    for level in log_levels:
        try:
            test_log_level(level, f"level_{level.lower()}")
        except Exception as e:
            print(f"Error testing log level {level}: {e}")
    
    print(f"\n{'='*60}")
    print("Log Level Test Summary:")
    print("- DEBUG: Most verbose, shows all messages")
    print("- INFO: Standard level, shows important information")
    print("- WARNING: Shows only warnings and errors")
    print("- ERROR: Shows only errors")
    print("="*60)


if __name__ == "__main__":
    main() 