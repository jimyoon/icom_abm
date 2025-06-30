import random
import logging
import pandas as pd
import numpy as np
import polars as pl
from pynsim import Engine
from chance_c.utils.numba_utils import filter_and_sample, calculate_utilities_vectorized, calculate_utilities_with_flood_vectorized, calculate_cobb_douglas_utilities
from chance_c.utils.polars_utils import fast_filter_and_sample_polars, fast_concat_dataframes, convert_polars_to_pandas
from chance_c.utils.multiprocessing_utils import parallel_household_processing, get_optimal_process_count


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
        use_multiprocessing (bool, optional): Whether to use multiprocessing for parallel processing.
            Defaults to True.
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
        budget_reduction_perc: float = 0.10,
        use_multiprocessing: bool = True,
        **kwargs
    ) -> None:
        """Initialize the ExistingAgentLocation engine.
        
        Args:
            target: The simulation network target.
            block_group_sample_size: Number of block groups to sample for each agent.
            house_choice_mode: Method for calculating housing utility.
            simple_anova_coefficients: Coefficients for ANOVA-based utility.
            budget_reduction_perc: Budget reduction percentage.
            use_multiprocessing: Whether to use multiprocessing for parallel processing.
            **kwargs: Additional keyword arguments.
        """
        super(ExistingAgentLocation, self).__init__(target, **kwargs)
        self.block_group_sample_size = block_group_sample_size
        self.house_choice_mode = house_choice_mode
        if simple_anova_coefficients is not None:
            self.simple_anova_coefficients = np.array(simple_anova_coefficients, dtype=np.float64)
        else:
            self.simple_anova_coefficients = np.array([], dtype=np.float64)
        self.budget_reduction_perc = budget_reduction_perc
        self.use_multiprocessing = use_multiprocessing

    def run(self) -> None:
        """Run the ExistingAgentLocation engine.
        
        Processes all relocating household agents waiting in the location queue.
        For each agent, samples from available homes and calculates utility
        scores based on the specified house choice mode. Uses multiprocessing
        for parallel processing when enabled.
        """
        logging.info("Running the existing agent location engine, year " + str(self.target.current_timestep.year))

        if not hasattr(self.target, 'relocating_households') or not self.target.relocating_households:
            logging.info("No relocating households to process")
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
        max_budget = max([hh.house_budget for hh in self.target.relocating_households.values()])
        block_group_all = block_group_all.filter(pl.col("new_price") <= max_budget)
        
        # Convert back to pandas for compatibility
        block_group_df = block_group_all.to_pandas()
        
        # Get list of households to process
        households = list(self.target.relocating_households.values())
        
        if self.use_multiprocessing and len(households) > 10:
            # Use multiprocessing for large numbers of households
            logging.info(f"Using multiprocessing for {len(households)} relocating households")
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
            logging.info(f"Using sequential processing for {len(households)} relocating households")
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
                    residuals = block_group_sample['residuals'].to_numpy(dtype=np.float64)
                    coefficients = np.array(self.simple_anova_coefficients, dtype=np.float64)
                    utilities = calculate_utilities_vectorized(sqfeet, age, stories, baths, residuals, coefficients)
                    block_group_sample['utility'] = utilities
                    
                else:
                    # Default to simple ANOVA
                    sqfeet = block_group_sample['N_MeanSqfeet'].to_numpy(dtype=np.float64)
                    age = block_group_sample['N_MeanAge'].to_numpy(dtype=np.float64)
                    stories = block_group_sample['N_MeanNoOfStories'].to_numpy(dtype=np.float64)
                    baths = block_group_sample['N_MeanFullBathNumber'].to_numpy(dtype=np.float64)
                    residuals = block_group_sample['residuals'].to_numpy(dtype=np.float64)
                    coefficients = np.array(self.simple_anova_coefficients, dtype=np.float64)
                    utilities = calculate_utilities_vectorized(sqfeet, age, stories, baths, residuals, coefficients)
                    block_group_sample['utility'] = utilities
                
                all_samples.append(block_group_sample)

        # Efficient single concatenation
        if not all_samples:
            self.target.hh_utilities_df = pd.DataFrame(columns=['GEOID', 'household', 'utility'])
            return
        
        block_group_sample = pd.concat(all_samples, ignore_index=True)
        self.target.hh_utilities_df = block_group_sample[['GEOID', 'household', 'utility']]
