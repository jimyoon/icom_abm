#!/usr/bin/env python3
"""
Example script demonstrating random seed functionality in the Model class.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chance_c import Model, SimulationConfig


def main():
    """Demonstrate random seed functionality."""
    print("Random Seed Functionality Examples")
    print("=" * 50)
    
    # Example 1: Direct parameter
    print("Example 1: Setting random seed directly")
    model1 = Model(
        simulation_name="example_1",
        start_year=2018,
        n_years=1,
        random_seed=42
    )
    print(f"Model config random_seed: {model1.config.random_seed}")
    
    # Example 2: Config object
    print("\nExample 2: Setting random seed in config")
    config = SimulationConfig(
        simulation_name="example_2",
        start_year=2018,
        n_years=1,
        random_seed=123
    )
    model2 = Model(config=config)
    print(f"Model config random_seed: {model2.config.random_seed}")
    
    # Example 3: Override config
    print("\nExample 3: Override config seed")
    model3 = Model(config=config, random_seed=999)
    print(f"Original config seed: {config.random_seed}")
    print(f"Model config seed: {model3.config.random_seed}")
    
    print("\n" + "=" * 50)
    print("Random seed functionality implemented successfully!")


if __name__ == "__main__":
    main() 