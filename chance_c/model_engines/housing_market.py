import logging
import pandas as pd
import numpy as np
from chance_c.numba_utils import find_top_candidates

from pynsim import Engine


class HousingMarket(Engine):
    """An engine class that matches buyers with housing inventory representing the housing market.

    The HousingMarket engine matches buyers with sellers in the housing market through
    an iterative process that prioritizes households based on income and utility preferences.
    It handles both new households entering the market and existing households relocating
    within the domain.

    Args:
        target: The simulation network target containing block group nodes and household data.
        market_mode (str, optional): Mode for market matching algorithm. 
            Currently supports 'top_candidate'. Defaults to 'top_candidate'.
        block_group_sample_size (int, optional): Number of market iterations to perform. 
            Defaults to 10.
        **kwargs: Additional keyword arguments passed to the parent class.

    Inter-module Outputs/Modifications:
        target.unassigned_households (dict): Dictionary of unassigned household agents.
        target.relocating_households (dict): Dictionary of relocating household agents.
        target.get_institution('all_household_agents'): Institution containing all household agents.
        target.get_node(bg).household_agents (dict): Household agents assigned to block group nodes.
        target.get_node(bg).occupied_units (int): Updated occupied units in block group.
        target.get_node(bg).available_units (int): Updated available units in block group.
        target.get_node(bg).demand_exceeds_supply (bool): Flag indicating demand exceeds supply.
    """

    def __init__(self, target, market_mode: str = 'top_candidate', 
                 block_group_sample_size: int = 10, **kwargs) -> None:
        """Initialize the HousingMarket engine.
        
        Args:
            target: The simulation network target containing block group nodes and household data.
            market_mode: Mode for market matching algorithm.
            block_group_sample_size: Number of market iterations to perform.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(HousingMarket, self).__init__(target, **kwargs)
        self.market_mode = market_mode
        self.block_group_sample_size = block_group_sample_size

    def run(self) -> None:
        """Run the HousingMarket engine.
        
        Matches households to housing based on utility scores and availability.
        Uses a greedy matching algorithm where households with higher utilities
        get priority for their preferred locations.
        """
        logging.info("Running the housing market engine, year " + str(self.target.current_timestep.year))

        if self.target.hh_utilities_df.empty:
            logging.info("No household utilities to process")
            return

        # Convert to numpy arrays for faster processing
        utilities_df = self.target.hh_utilities_df
        geoids = utilities_df['GEOID'].to_numpy()
        households = utilities_df['household'].to_numpy()
        utilities = utilities_df['utility'].to_numpy()
        
        # Get unique households and their utilities
        unique_households = np.unique(households)
        household_assignments = {}
        used_geoids = set()
        
        # Process households in batches for better performance
        batch_size = 100
        for i in range(0, len(unique_households), batch_size):
            batch_households = unique_households[i:i+batch_size]
            
            for household in batch_households:
                # Find all options for this household
                household_mask = households == household
                household_geoids = geoids[household_mask]
                household_utilities = utilities[household_mask]
                
                if len(household_geoids) == 0:
                    continue
                
                # Find top candidates using numba-optimized function
                top_indices = find_top_candidates(household_utilities, len(household_utilities))
                
                # Try to assign the best available location
                assigned = False
                for idx in top_indices:
                    geoid = household_geoids[idx]
                    if geoid not in used_geoids:
                        household_assignments[household] = geoid
                        used_geoids.add(geoid)
                        assigned = True
                        break
                
                if not assigned:
                    # Mark as outmigrated if no location available
                    household_assignments[household] = 'outmigrated'

        # Apply assignments
        for household_name, geoid in household_assignments.items():
            if household_name in self.target.relocating_households:
                household = self.target.relocating_households[household_name]
                household.location = geoid
                del self.target.relocating_households[household_name]
            elif household_name in self.target.new_households:
                household = self.target.new_households[household_name]
                household.location = geoid
                del self.target.new_households[household_name]

        logging.info(f"Assigned {len([g for g in household_assignments.values() if g != 'outmigrated'])} households to locations")
        logging.info(f"Outmigrated {len([g for g in household_assignments.values() if g == 'outmigrated'])} households")
