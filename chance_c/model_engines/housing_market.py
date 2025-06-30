import logging
import pandas as pd
import numpy as np
import polars as pl
from pynsim import Engine

from chance_c.utils.numba_utils import find_top_candidates
from chance_c.utils.polars_utils import (
    fast_market_matching_polars, 
    fast_market_matching_parallel_polars,
    fast_market_matching_numba_optimized,
    fast_market_matching_hybrid
)


class HousingMarket(Engine):
    """An engine class that matches households to housing based on utility scores.
    
    The HousingMarket class is a pynsim engine that matches households to housing
    based on utility scores and availability. It uses a greedy matching algorithm
    where households with higher utilities get priority for their preferred locations.
    
    Args:
        target: The simulation network target containing block group nodes and household data.
        market_mode (str, optional): Mode for market matching algorithm. Defaults to 'hybrid'.
        block_group_sample_size (int, optional): Number of market iterations to perform.
            Defaults to 10.
        use_multiprocessing (bool, optional): Whether to use multiprocessing for parallel processing.
            Defaults to True.
        **kwargs: Additional keyword arguments passed to the parent class.
    
    Inter-module Outputs/Modifications:
        target.household_assignments (dict): Dictionary mapping household names to assigned GEOIDs.
    """

    def __init__(self, target, market_mode: str = 'hybrid', 
                 block_group_sample_size: int = 10, use_multiprocessing: bool = True, **kwargs) -> None:
        """Initialize the HousingMarket engine.
        
        Args:
            target: The simulation network target containing block group nodes and household data.
            market_mode: Mode for market matching algorithm ('polars', 'parallel', 'hybrid').
            block_group_sample_size: Number of market iterations to perform.
            use_multiprocessing: Whether to use multiprocessing for parallel processing.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(HousingMarket, self).__init__(target, **kwargs)
        self.market_mode = market_mode
        self.block_group_sample_size = block_group_sample_size
        self.use_multiprocessing = use_multiprocessing

    def run(self) -> None:
        """Run the HousingMarket engine.
        
        Matches households to housing based on utility scores and availability.
        Uses a greedy matching algorithm where households with higher utilities
        get priority for their preferred locations. Uses optimized algorithms
        for better performance.
        """
        logging.debug("Running the housing market engine, year " + str(self.target.current_timestep.year))

        if self.target.hh_utilities_df.empty:
            logging.info("No household utilities to process")
            return

        # Convert to Polars for faster processing
        utilities_df = pl.from_pandas(self.target.hh_utilities_df)
        
        if len(utilities_df) == 0:
            logging.info("No household utilities to process")
            return

        # Choose market matching algorithm based on mode
        if self.market_mode == 'polars':
            household_assignments = fast_market_matching_polars(
                utilities_df=utilities_df,
                geoid_col='GEOID',
                household_col='household',
                utility_col='utility'
            )
        elif self.market_mode == 'parallel':
            household_assignments = fast_market_matching_parallel_polars(
                utilities_df=utilities_df,
                geoid_col='GEOID',
                household_col='household',
                utility_col='utility'
            )
        else:  # hybrid (default)
            household_assignments = fast_market_matching_hybrid(
                utilities_df=utilities_df,
                geoid_col='GEOID',
                household_col='household',
                utility_col='utility'
            )

        # Store assignments
        self.target.household_assignments = household_assignments
        
        # Process assignments to update block groups
        for household_name, geoid in household_assignments.items():
            if geoid == 'outmigrated':
                logging.debug(f"Household {household_name} outmigrated - no suitable location found")
                continue
            
            # Find the household agent
            household_agent = None
            if hasattr(self.target, 'unassigned_households'):
                for hh in self.target.unassigned_households.values():
                    if hh.name == household_name:
                        household_agent = hh
                        break
            
            if hasattr(self.target, 'relocating_households') and household_agent is None:
                for hh in self.target.relocating_households.values():
                    if hh.name == household_name:
                        household_agent = hh
                        break
            
            if household_agent is None:
                logging.debug(f"Could not find household agent for {household_name}")
                continue
            
            # Assign household to block group
            target_block_group = self.target.get_node(geoid)
            if target_block_group is None:
                logging.warning(f"Could not find block group {geoid}")
                continue
            
            # Update household location
            household_agent.location = geoid
            target_block_group.household_agents[household_name] = household_agent
            
            # Update block group occupancy
            target_block_group.occupied_units += 1
            target_block_group.available_units -= 1
            
            # Remove from unassigned/relocating lists
            if hasattr(self.target, 'unassigned_households') and household_name in self.target.unassigned_households:
                del self.target.unassigned_households[household_name]
            
            if hasattr(self.target, 'relocating_households') and household_name in self.target.relocating_households:
                del self.target.relocating_households[household_name]
            
            logging.debug(f"Assigned household {household_name} to block group {geoid}")
