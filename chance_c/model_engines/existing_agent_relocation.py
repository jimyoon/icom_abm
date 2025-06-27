import random
import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any

from pynsim import Engine


class ExistingAgentReloSampler(Engine):
    """An engine class that identifies existing agents to relocate and determines utility for homes.

    The ExistingAgentReloSampler class is a pynsim engine that determines which agents wish to relocate.
    The target of the engine is the simulation network. For each block group, it randomly samples a
    percentage of the existing household population to relocate, vacates their existing properties,
    and adds them to the relocation queue.

    Args:
        target: The simulation network target.
        perc_move (float, optional): The percentage of agents that desire to move in any given 
            time period. Defaults to 0.10.
        **kwargs: Additional keyword arguments passed to the parent class.

    Inter-module Outputs/Modifications:
        target.relocating_households (dict): Dictionary of HHAgent objects in the relocation queue.
        bg.household_agents (dict): Updated household agents dictionary for each block group.
        bg.occupied_units (int): Updated occupied units count for each block group.
        bg.available_units (int): Updated available units count for each block group.
    """

    def __init__(self, target, perc_move: float = 0.10, **kwargs) -> None:
        """Initialize the ExistingAgentReloSampler engine.

        Args:
            target: The simulation network target.
            perc_move: The percentage of agents that desire to move in any given time period.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(ExistingAgentReloSampler, self).__init__(target, **kwargs)
        self.perc_move = perc_move

    def run(self) -> None:
        """Execute the existing agent relocation sampling process.

        For each block group, randomly samples a percentage of the existing household
        population to relocate. The engine vacates the agent's existing property
        (adding the property to the block group's available units) and adds the
        agent to the relocation queue.
        """
        logging.info("Running the existing agent sampler engine, year " + str(self.target.current_timestep.year))

        for block_group in self.target.nodes:
            no_of_agents = len(block_group.household_agents)  # number of representative household agents
            no_of_agents_moving = round(no_of_agents * self.perc_move)
            agents_moving = random.sample(list(block_group.household_agents), no_of_agents_moving)  # randomly sample agents that will move
            for household in agents_moving:
                self.target.relocating_households[household] = self.target.get_institution('all_household_agents')._component_map[household]  # add agent to unassigned household list (is there a better way in pynsim rather than accessing _components_map)
                block_group_old_location = self.target.get_node(self.target.get_institution('all_household_agents')._component_map[household].location)
                del block_group_old_location.household_agents[household]  # remove agent from old location
                block_group_old_location.occupied_units -= 1  # adjust occupied units
                block_group_old_location.available_units += 1  # adjust available units
                # need to adjust available units in block group that agent is moving from
        pass  # to accommodate debugger


class ExistingAgentLocation(Engine):
    """An engine class to calculate existing (relocating) household agent's utility for homes.

    The ExistingAgentLocation class is a pynsim engine that calculates an existing/relocating 
    household agent's utility for a sample of available homes. The target of the engine is 
    a list of relocating existing agents in the queue. For each relocating agent, the engine 
    samples from available homes and calculates a utility function for each of those homes.

    Args:
        target: The simulation network target.
        block_group_sample_size (int, optional): Sample size for new agent's housing search. 
            Defaults to 10.
        house_choice_mode (str, optional): Mode for house choice utility calculation. 
            Defaults to 'simple_anova_utility'.
        simple_anova_coefficients (list, optional): Coefficients for simple ANOVA utility 
            calculation. Defaults to [].
        budget_reduction_perc (float, optional): Budget reduction percentage. 
            Defaults to 0.10.
        **kwargs: Additional keyword arguments passed to the parent class.

    Inter-module Outputs/Modifications:
        target.hh_utilities_df (pandas.DataFrame): DataFrame containing household utilities.
    """

    def __init__(
        self, 
        target, 
        block_group_sample_size: int = 10, 
        house_choice_mode: str = 'simple_anova_utility', 
        simple_anova_coefficients: list = None, 
        **kwargs
    ) -> None:
        """Initialize the ExistingAgentLocation engine.
        
        Args:
            target: The simulation network target.
            block_group_sample_size: Number of block groups to sample for each agent.
            house_choice_mode: Method for calculating housing utility.
            simple_anova_coefficients: Coefficients for ANOVA-based utility.
            **kwargs: Additional keyword arguments.
        """
        super(ExistingAgentLocation, self).__init__(target, **kwargs)
        self.block_group_sample_size = block_group_sample_size
        self.house_choice_mode = house_choice_mode
        self.simple_anova_coefficients = simple_anova_coefficients or []
        
        # Cache for performance optimization
        self._cached_block_group_data = None
        self._cached_utility_functions = {}

    def _get_affordable_block_groups(self, household_budget: float) -> pd.DataFrame:
        """Get block groups that are affordable for a given household budget.
        
        Args:
            household_budget: The household's budget.
            
        Returns:
            DataFrame of affordable block groups.
        """
        if self._cached_block_group_data is None:
            self._cached_block_group_data = self.target.housing_block_group_df.copy()
        
        return self._cached_block_group_data[
            self._cached_block_group_data['new_price'] <= household_budget
        ]

    def _sample_block_groups(self, block_group_budget: pd.DataFrame, household_name: str) -> pd.DataFrame:
        """Sample block groups for a household with optimized sampling.
        
        Args:
            block_group_budget: DataFrame of affordable block groups.
            household_name: Name of the household.
            
        Returns:
            DataFrame of sampled block groups with household info.
        """
        if len(block_group_budget) == 0:
            return pd.DataFrame()
        
        # Use weights if available_units column exists, otherwise uniform sampling
        if 'available_units' in block_group_budget.columns:
            weights = block_group_budget['available_units'].values
            # Handle zero weights
            if weights.sum() == 0:
                weights = None
        else:
            weights = None
        
        try:
            if weights is not None:
                sampled_indices = np.random.choice(
                    len(block_group_budget), 
                    size=min(self.block_group_sample_size, len(block_group_budget)), 
                    replace=True, 
                    p=weights/weights.sum()
                )
            else:
                sampled_indices = np.random.choice(
                    len(block_group_budget), 
                    size=min(self.block_group_sample_size, len(block_group_budget)), 
                    replace=True
                )
            
            sampled_data = block_group_budget.iloc[sampled_indices].copy()
            sampled_data['household'] = household_name
            sampled_data['a'] = 0.4
            sampled_data['b'] = 0.4
            sampled_data['c'] = 0.2
            
            return sampled_data
            
        except ValueError:
            logging.info(f'{household_name} cannot afford any available homes!')
            return pd.DataFrame()

    def _calculate_utility_vectorized(self, block_group_sample: pd.DataFrame) -> pd.Series:
        """Calculate utility scores using vectorized operations.
        
        Args:
            block_group_sample: DataFrame with block group data.
            
        Returns:
            Series of utility scores.
        """
        if self.house_choice_mode == 'cobb_douglas_utility':
            return (
                block_group_sample['average_income_norm'] ** block_group_sample['a']
            ) * (
                block_group_sample['prox_cbd_norm'] ** block_group_sample['b']
            ) * (
                block_group_sample['flood_risk_norm'] ** block_group_sample['c']
            )
        
        elif self.house_choice_mode in ['simple_flood_utility', 'simple_avoidance_utility', 'budget_reduction']:
            # Pre-calculate coefficients for vectorized operations
            coef = self.simple_anova_coefficients
            
            # Get the housing data for the sampled block groups
            housing_data = self.target.housing_block_group_df.loc[block_group_sample.index]
            
            utility = (
                coef[0] +
                coef[1] * housing_data['N_MeanSqfeet'] +
                coef[2] * housing_data['N_MeanAge'] +
                coef[3] * housing_data['N_MeanNoOfStories'] +
                coef[4] * housing_data['N_MeanFullBathNumber'] +
                housing_data['residuals']
            )
            
            # Add flood risk component for simple_flood_utility
            if self.house_choice_mode == 'simple_flood_utility':
                utility += housing_data['N_perc_area_flood']
            
            return utility
        
        else:
            # Default to zero utility for unknown modes
            return pd.Series(0, index=block_group_sample.index)

    def run(self) -> None:
        """Run the optimized ExistingAgentLocation engine.
        
        Processes all relocating household agents waiting in the location queue.
        For each agent, samples from available homes and calculates utility
        scores based on the specified house choice mode. Agents that cannot
        afford any homes are marked as outmigrated.
        """
        logging.info("Running the existing agent location engine, year " + str(self.target.current_timestep.year))

        # Pre-allocate list for results to avoid DataFrame concatenation
        all_results = []
        outmigrated_households = []

        # Process each relocating household
        for household in self.target.relocating_households.values():
            # Get affordable block groups
            block_group_budget = self._get_affordable_block_groups(household.house_budget)
            
            if len(block_group_budget) == 0:
                logging.info(f'{household.name} cannot afford any available homes!')
                household.location = 'outmigrated'
                outmigrated_households.append(household)
                continue
            
            # Sample block groups
            block_group_sample = self._sample_block_groups(block_group_budget, household.name)
            
            if len(block_group_sample) == 0:
                household.location = 'outmigrated'
                outmigrated_households.append(household)
                continue
            
            # Calculate utility scores
            block_group_sample['utility'] = self._calculate_utility_vectorized(block_group_sample)
            
            # Store results
            all_results.append(block_group_sample[['GEOID', 'household', 'utility']])

        # Combine all results at once
        if all_results:
            self.target.hh_utilities_df = pd.concat(all_results, ignore_index=True)
        else:
            self.target.hh_utilities_df = pd.DataFrame(columns=['GEOID', 'household', 'utility'])
        
        # Remove outmigrated households from relocating queue
        for household in outmigrated_households:
            if household in self.target.relocating_households:
                del self.target.relocating_households[household]
