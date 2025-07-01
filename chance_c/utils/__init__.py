"""
Utility functions for the chance_c package.
"""

import random
import numpy as np
import logging
from typing import Union


def set_random_seed(seed: Union[int, None]) -> None:
    """Set random seed for reproducible simulations.
    
    This function sets the random seed for both Python's random module and
    NumPy's random number generator to ensure reproducible results across
    all randomized processes in the simulation.
    
    Args:
        seed: The random seed to use. If None, no seed is set (random behavior).
            
    Returns:
        None
        
    Example:
        >>> set_random_seed(42)
        >>> # All subsequent random operations will be reproducible
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        logging.info(f"Random seed set to {seed} for reproducible simulation")
    else:
        logging.info("No random seed set - simulation will use random behavior") 