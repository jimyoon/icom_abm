#!/usr/bin/env python3
"""
Example script demonstrating log level functionality in the Model class.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chance_c import Model, SimulationConfig


def main():
    """Demonstrate log level functionality."""
    print("Log Level Functionality Examples")
    print("=" * 50)
    
    # Example 1: Default INFO level
    print("Example 1: Default INFO level")
    model1 = Model(
        simulation_name="example_info",
        start_year=2018,
        n_years=1
    )
    print(f"Model config log_level: {model1.config.log_level}")
    
    # Example 2: DEBUG level
    print("\nExample 2: DEBUG level")
    model2 = Model(
        simulation_name="example_debug",
        start_year=2018,
        n_years=1,
        log_level='DEBUG'
    )
    print(f"Model config log_level: {model2.config.log_level}")
    
    # Example 3: WARNING level
    print("\nExample 3: WARNING level")
    model3 = Model(
        simulation_name="example_warning",
        start_year=2018,
        n_years=1,
        log_level='WARNING'
    )
    print(f"Model config log_level: {model3.config.log_level}")
    
    # Example 4: Using config object
    print("\nExample 4: Using config object")
    config = SimulationConfig(
        simulation_name="example_config",
        start_year=2018,
        n_years=1,
        log_level='ERROR'
    )
    model4 = Model(config=config)
    print(f"Model config log_level: {model4.config.log_level}")
    
    # Example 5: Override config
    print("\nExample 5: Override config log level")
    model5 = Model(config=config, log_level='DEBUG')
    print(f"Original config log_level: {config.log_level}")
    print(f"Model config log_level: {model5.config.log_level}")
    
    print("\n" + "=" * 50)
    print("Log level functionality implemented successfully!")
    print("\nAvailable log levels:")
    print("- DEBUG: Most verbose output")
    print("- INFO: Standard information (default)")
    print("- WARNING: Only warnings and errors")
    print("- ERROR: Only error messages")
    print("- CRITICAL: Only critical errors")


if __name__ == "__main__":
    main() 