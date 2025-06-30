#!/usr/bin/env python3
"""
Test script to demonstrate the logging functionality in the Model class.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chance_c.model import Model
import logging


def test_logging_levels():
    """Test different logging levels with the Model class."""
    
    print("Testing Model logging functionality...")
    print("=" * 50)
    
    # Test 1: Default INFO level
    print("\n1. Testing with default INFO level:")
    model1 = Model(
        simulation_name="test_info",
        n_years=1,
        log_level=logging.INFO
    )
    model1.logger.info("This is an INFO message")
    model1.logger.debug("This DEBUG message should not appear")
    
    # Test 2: DEBUG level
    print("\n2. Testing with DEBUG level:")
    model2 = Model(
        simulation_name="test_debug",
        n_years=1,
        log_level=logging.DEBUG
    )
    model2.logger.info("This is an INFO message")
    model2.logger.debug("This DEBUG message should appear")
    
    # Test 3: String log level
    print("\n3. Testing with string log level 'WARNING':")
    model3 = Model(
        simulation_name="test_warning",
        n_years=1,
        log_level="WARNING"
    )
    model3.logger.info("This INFO message should not appear")
    model3.logger.warning("This WARNING message should appear")
    
    # Test 4: Changing log level after creation
    print("\n4. Testing log level change after creation:")
    model4 = Model(
        simulation_name="test_change",
        n_years=1,
        log_level=logging.ERROR
    )
    model4.logger.info("This INFO message should not appear")
    model4.set_log_level("DEBUG")
    model4.logger.debug("This DEBUG message should appear after level change")
    
    # Test 5: Error handling for invalid log level
    print("\n5. Testing error handling for invalid log level:")
    try:
        model5 = Model(
            simulation_name="test_invalid",
            n_years=1,
            log_level="INVALID_LEVEL"
        )
    except ValueError as e:
        print(f"✅ Correctly caught invalid log level: {e}")
    
    print("\n" + "=" * 50)
    print("✅ All logging tests completed!")


def test_config_logging():
    """Test logging with configuration file."""
    
    print("\nTesting logging with configuration...")
    print("=" * 50)
    
    # Create a config with custom log level
    from chance_c.data_loader import SimulationConfig
    
    config = SimulationConfig(
        simulation_name="test_config_logging",
        n_years=1,
        log_level="DEBUG"
    )
    
    model = Model(config=config)
    model.logger.debug("This DEBUG message should appear from config")
    model.logger.info("This INFO message should also appear")
    
    print("✅ Config logging test completed!")


if __name__ == "__main__":
    test_logging_levels()
    test_config_logging() 