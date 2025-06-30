import random
import logging
import numpy as np
import polars as pl

from pynsim import Engine
import pandas as pd
from typing import List, Dict, Any, Optional

from ..model_classes.urban_agents import HouseholdAgent
from chance_c.utils.numba_utils import calculate_utilities_vectorized, calculate_cobb_douglas_utilities, filter_and_sample
from chance_c.utils.polars_utils import fast_filter_and_sample_polars, fast_concat_dataframes, convert_polars_to_pandas
from chance_c.utils.multiprocessing_utils import parallel_household_processing, get_optimal_process_count


class NewAgentLocation(Engine):
    """Calculate new household agent's utility for available homes.
    
    A pynsim engine that calculates utility scores for new household agents
    considering a sample of available homes. The engine processes unlocated
    agents in the queue, samples from available homes, and calculates utility
    functions for each home based on the specified choice mode.
    
    Args:
        target: The simulation network containing housing data and agents.
        block_group_sample_size: Number of block groups to sample for each agent.
            Defaults to 10.
        house_choice_mode: Method for calculating housing utility. Options:
            'simple_anova_utility', 'cobb_douglas_utility', 'simple_flood_utility',
            'simple_avoidance_utility', 'budget_reduction'. Defaults to
            'simple_anova_utility'.
        simple_anova_coefficients: Coefficients for ANOVA-based utility
            calculation. Defaults to empty list.
        budget_reduction_perc: Percentage reduction in budget for flood-prone
            areas when using budget_reduction mode. Defaults to 0.10.
        no_households_per_agent: Number of households per agent.
        household_size: Average household size.
        **kwargs: Additional keyword arguments passed to parent class.
    
    Attributes:
        block_group_sample_size: Number of block groups to sample per agent.
        house_choice_mode: Selected utility calculation method.
        simple_anova_coefficients: Coefficients for ANOVA utility calculation.
        budget_reduction_perc: Budget reduction percentage for flood areas.
        no_households_per_agent: Number of households per agent.
        household_size: Average household size.
    """
    
    def __init__(
        self, 
        target, 
        block_group_sample_size: int = 10, 
        house_choice_mode: str = 'simple_anova_utility', 
        simple_anova_coefficients: list = None, 
        budget_reduction_perc: float = 0.10,
        no_households_per_agent: int = 10,
        household_size: float = 2.7,
        use_multiprocessing: bool = True,
        **kwargs
    ) -> None:
        """Initialize the NewAgentLocation engine.
        
        Args:
            target: The simulation network containing housing data and agents.
            block_group_sample_size: Number of block groups to sample for each agent.
            house_choice_mode: Method for calculating housing utility.
            simple_anova_coefficients: Coefficients for ANOVA-based utility calculation.
            budget_reduction_perc: Percentage reduction in budget for flood-prone areas.
            no_households_per_agent: Number of households per agent.
            household_size: Average household size.
            use_multiprocessing: Whether to use multiprocessing for parallel processing.
            **kwargs: Additional keyword arguments passed to parent class.
        """
        super(NewAgentLocation, self).__init__(target, **kwargs)
        self.block_group_sample_size = block_group_sample_size
        self.house_choice_mode = house_choice_mode
        self.simple_anova_coefficients = simple_anova_coefficients or []
        self.budget_reduction_perc = budget_reduction_perc
        self.no_households_per_agent = no_households_per_agent
        self.household_size = household_size
        self.use_multiprocessing = use_multiprocessing

    def run(self) -> None:
        """Run the NewAgentLocation engine.
        
        Processes all new household agents waiting in the location queue.
        For each agent, samples from available homes and calculates utility
        scores based on the specified house choice mode. Uses multiprocessing
        for parallel processing when enabled.
        """
        logging.info("Running the new agent location engine, year " + str(self.target.current_timestep.year))

        if not hasattr(self.target, 'unassigned_households') or not self.target.unassigned_households:
            logging.info("No unassigned households to process")
            self.target.hh_utilities_df = pd.DataFrame(columns=['GEOID', 'household', 'utility'])
            return

        # Convert to Polars for faster operations
        # Only drop the geometry column before conversion
        df = self.target.housing_block_group_df
        drop_cols = [col for col in df.columns if str(df[col].dtype) == 'geometry']
        if 'geometry' in df.columns:
            drop_cols.append('geometry')
        block_group_all = pl.from_pandas(df.drop(columns=drop_cols))
        
        # Pre-filter by budget to reduce computation
        max_budget = max([hh.house_budget for hh in self.target.unassigned_households.values()])
        block_group_all = block_group_all.filter(pl.col("new_price") <= max_budget)
        
        # Convert back to pandas for compatibility
        block_group_df = block_group_all.to_pandas()
        
        # Get list of households to process
        households = list(self.target.unassigned_households.values())
        
        if self.use_multiprocessing and len(households) > 10:
            # Use multiprocessing for large numbers of households
            logging.info(f"Using multiprocessing for {len(households)} households")
            n_processes = get_optimal_process_count('household')
            
            all_samples = parallel_household_processing(
                households=households,
                block_group_df=block_group_df,
                block_group_sample_size=self.block_group_sample_size,
                house_choice_mode=self.house_choice_mode,
                simple_anova_coefficients=self.simple_anova_coefficients,
                budget_reduction_perc=self.budget_reduction_perc,
                n_processes=n_processes
            )
        else:
            # Use sequential processing for small numbers of households
            logging.info(f"Using sequential processing for {len(households)} households")
            all_samples = []
            
            for household in households:
                # Filter by budget
                budget_filter = block_group_df['new_price'] <= household.house_budget
                block_group_budget = block_group_df[budget_filter].copy()
                
                if len(block_group_budget) == 0:
                    logging.info(household.name + ' cannot afford any available homes!')
                    household.location = 'outmigrated'
                    continue
                
                # Sample block groups
                n_sample = min(self.block_group_sample_size, len(block_group_budget))
                prices = block_group_budget['new_price'].to_numpy(dtype=np.float64)
                weights = block_group_budget['available_units'].to_numpy(dtype=np.float64)
                indices = filter_and_sample(prices, weights, np.inf, n_sample)
                
                if len(indices) == 0:
                    logging.info(household.name + ' cannot afford any available homes!')
                    household.location = 'outmigrated'
                    continue
                
                block_group_sample = block_group_budget.iloc[indices].copy()
                block_group_sample['household'] = household.name
                block_group_sample['a'] = 0.4
                block_group_sample['b'] = 0.4
                block_group_sample['c'] = 0.2
                
                # Calculate utilities
                if self.house_choice_mode == 'cobb_douglas_utility':
                    income = block_group_sample['average_income_norm'].to_numpy(dtype=np.float64)
                    prox_cbd = block_group_sample['prox_cbd_norm'].to_numpy(dtype=np.float64)
                    flood_risk = block_group_sample['flood_risk_norm'].to_numpy(dtype=np.float64)
                    a = block_group_sample['a'].to_numpy(dtype=np.float64)
                    b = block_group_sample['b'].to_numpy(dtype=np.float64)
                    c = block_group_sample['c'].to_numpy(dtype=np.float64)
                    utilities = calculate_cobb_douglas_utilities(income, prox_cbd, flood_risk, a, b, c)
                    block_group_sample['utility'] = utilities
                    
                elif self.house_choice_mode == 'simple_flood_utility':
                    sqfeet = block_group_sample['N_MeanSqfeet'].to_numpy(dtype=np.float64)
                    age = block_group_sample['N_MeanAge'].to_numpy(dtype=np.float64)
                    stories = block_group_sample['N_MeanNoOfStories'].to_numpy(dtype=np.float64)
                    baths = block_group_sample['N_MeanFullBathNumber'].to_numpy(dtype=np.float64)
                    flood_risk = block_group_sample['N_perc_area_flood'].to_numpy(dtype=np.float64)
                    residuals = block_group_sample['residuals'].to_numpy(dtype=np.float64)
                    utilities = calculate_utilities_with_flood_vectorized(sqfeet, age, stories, baths, flood_risk, residuals)
                    block_group_sample['utility'] = utilities
                    
                elif self.house_choice_mode == 'simple_anova_utility':
                    sqfeet = block_group_sample['N_MeanSqfeet'].to_numpy(dtype=np.float64)
                    age = block_group_sample['N_MeanAge'].to_numpy(dtype=np.float64)
                    stories = block_group_sample['N_MeanNoOfStories'].to_numpy(dtype=np.float64)
                    baths = block_group_sample['N_MeanFullBathNumber'].to_numpy(dtype=np.float64)
                    utilities = calculate_utilities_vectorized(sqfeet, age, stories, baths, self.simple_anova_coefficients)
                    block_group_sample['utility'] = utilities
                    
                else:
                    # Default to simple ANOVA
                    sqfeet = block_group_sample['N_MeanSqfeet'].to_numpy(dtype=np.float64)
                    age = block_group_sample['N_MeanAge'].to_numpy(dtype=np.float64)
                    stories = block_group_sample['N_MeanNoOfStories'].to_numpy(dtype=np.float64)
                    baths = block_group_sample['N_MeanFullBathNumber'].to_numpy(dtype=np.float64)
                    utilities = calculate_utilities_vectorized(sqfeet, age, stories, baths, self.simple_anova_coefficients)
                    block_group_sample['utility'] = utilities
                
                all_samples.append(block_group_sample)

        # Efficient single concatenation
        if not all_samples:
            self.target.hh_utilities_df = pd.DataFrame(columns=['GEOID', 'household', 'utility'])
            return
        
        block_group_sample = pd.concat(all_samples, ignore_index=True)
        self.target.hh_utilities_df = block_group_sample[['GEOID', 'household', 'utility']]

    def run_old_version(self):
        """ Run the NewAgentLocation Engine. The target of this engine are all new household agents waiting in the location queue.
        This version of the engine is a simple proof-of-concept version to illustrate pynsim functionality.
        """
        # identify block groups in which new residents/development is allowed
        block_group_dev_allowed = []
        for block_group in self.target.nodes:
            if block_group.zoning == 'allowed':
                block_group_dev_allowed.append(block_group)

        # assign new population to block groups (currently assumes agents move to a random block group)
        new_population = self.target.total_population * self.pop_growth
        no_of_new_agents = (new_population + self.no_hhs_per_agent // 2) // self.no_hhs_per_agent  # division with rounding to nearest integer
        count = 1
        for a in range(int(no_of_new_agents)):
            block_group = random.choice(block_group_dev_allowed)
            name = 'hh_agent_' + str(self.timestep.year) + '_' + str(count)
            self.target.add_component(HouseholdAgent(name=name, location=block_group.name, no_households_per_agent=self.no_households_per_agent,
                                               household_size=self.household_size, year_of_residence=self.timestep.year))  # add household agent to pynsim network
            block_group.household_agents[self.target.components[-1].name] = self.target.components[-1]  # add pynsim household agent to associated block group node
            self.target.get_institution('all_household_agents').add_component(self.target.components[-1])  # add pynsim household agent to all household agents institution
            count += 1

        # make agent relocation decisions (currently assumes that 10% of randomly selected agents move to a random block group)
        no_agents_moving = int(len(self.target.get_institution('all_household_agents').components) * .10)
        agents_moving = random.sample(self.target.get_institution('all_household_agents').components, no_agents_moving)
        for agent in agents_moving:
            block_group_old_location = self.target.get_node(agent.location)
            del block_group_old_location.household_agents[agent.name]  # remove agent from old location
            block_group_old_location.occupied_units -= 1  # adjust occupied units
            block_group_old_location.available_units += 1  # adjust available units
            block_group_new_location = random.choice(block_group_dev_allowed)
            agent.location = block_group_new_location.name  # assign agent to new location
            block_group_new_location.household_agents[agent.name] = agent  # add agent to new location
            block_group_new_location.occupied_units += 1  # adjust occupied units
            block_group_new_location.available_units -= 1  # adjust available units

