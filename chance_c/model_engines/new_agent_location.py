import random
import logging
import numpy as np
import polars as pl

from pynsim import Engine
import pandas as pd

from ..model_classes.urban_agents import HouseholdAgent
from chance_c.numba_utils import calculate_utilities_vectorized, calculate_cobb_douglas_utilities, filter_and_sample
from chance_c.polars_utils import fast_filter_and_sample_polars, fast_concat_dataframes, convert_polars_to_pandas


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
        **kwargs
    ) -> None:
        """Initialize the NewAgentLocation engine.
        
        Args:
            target: The simulation network target.
            block_group_sample_size: Number of block groups to sample for each agent.
            house_choice_mode: Method for calculating housing utility.
            simple_anova_coefficients: Coefficients for ANOVA-based utility.
            budget_reduction_perc: Budget reduction percentage for flood areas.
            no_households_per_agent: Number of households per agent.
            household_size: Average household size.
            **kwargs: Additional keyword arguments.
        """
        super(NewAgentLocation, self).__init__(target, **kwargs)
        self.block_group_sample_size = block_group_sample_size
        self.house_choice_mode = house_choice_mode
        self.simple_anova_coefficients = simple_anova_coefficients or []
        self.budget_reduction_perc = budget_reduction_perc
        self.no_households_per_agent = no_households_per_agent
        self.household_size = household_size

    def run(self) -> None:
        """Run the NewAgentLocation engine.
        
        Processes all new household agents waiting in the location queue.
        For each agent, samples from available homes and calculates utility
        scores based on the specified house choice mode. Agents that cannot
        afford any homes are marked as outmigrated.
        """
        logging.info("Running the new agent location engine, year " + str(self.target.current_timestep.year))

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
        
        # Collect all DataFrames for efficient concatenation
        all_samples = []
        to_delete_new_households = []
        
        # Batch process households for better performance
        household_batch = list(self.target.unassigned_households.values())
        
        for household in household_batch:
            # Use pre-filtered data and apply household-specific budget filter
            mask = (block_group_all["new_price"] <= household.house_budget)
            block_group_budget = block_group_all.filter(mask)
            
            # Convert back to pandas for compatibility with existing code
            block_group_budget_pd = block_group_budget.to_pandas()
            
            # --- NUMBA-OPTIMIZED SAMPLING ---
            if len(block_group_budget_pd) == 0:
                logging.info(household.name + ' cannot afford any available homes!')
                household.location = 'outmigrated'
                continue
            n_sample = 10
            prices = block_group_budget_pd['new_price'].to_numpy(dtype=np.float64)
            weights = block_group_budget_pd['available_units'].to_numpy(dtype=np.float64)
            indices = filter_and_sample(prices, weights, np.inf, n_sample)  # no price filter here, already filtered
            if len(indices) == 0:
                logging.info(household.name + ' cannot afford any available homes!')
                household.location = 'outmigrated'
                continue
            # Always include GEOID in the sample
            sample_cols = list(block_group_budget_pd.columns)
            if 'GEOID' not in sample_cols:
                sample_cols.append('GEOID')
            block_group_sample = block_group_budget_pd.iloc[indices][sample_cols].copy()
            block_group_sample['household'] = household.name
            block_group_sample['a'] = 0.4  # JY revise - only need this for Cobb-Douglas
            block_group_sample['b'] = 0.4
            block_group_sample['c'] = 0.2
            all_samples.append(block_group_sample)

        # Efficient single concatenation
        if not all_samples:
            self.target.hh_utilities_df = pd.DataFrame(columns=['GEOID', 'household', 'utility'])
            return
        block_group_sample = pd.concat(all_samples, ignore_index=True)

        if self.house_choice_mode == 'cobb_douglas_utility':  # consider moving to method on household agents
            # Use numba-optimized vectorized Cobb-Douglas utility calculation
            income = block_group_sample['average_income_norm'].to_numpy(dtype=np.float64)
            prox_cbd = block_group_sample['prox_cbd_norm'].to_numpy(dtype=np.float64)
            flood_risk = block_group_sample['flood_risk_norm'].to_numpy(dtype=np.float64)
            a = block_group_sample['a'].to_numpy(dtype=np.float64)
            b = block_group_sample['b'].to_numpy(dtype=np.float64)
            c = block_group_sample['c'].to_numpy(dtype=np.float64)
            # Ensure a, b, c are arrays (not scalars)
            if a.shape == ():
                a = np.full_like(income, a)
            if b.shape == ():
                b = np.full_like(income, b)
            if c.shape == ():
                c = np.full_like(income, c)
            utilities = calculate_cobb_douglas_utilities(income, prox_cbd, flood_risk, a, b, c)
            block_group_sample['utility'] = utilities

        elif self.house_choice_mode == 'simple_flood_utility':  # JY consider moving to method on household agents
            # Use numba-optimized vectorized utility calculation
            sqfeet = block_group_sample['N_MeanSqfeet'].to_numpy(dtype=np.float64)
            age = block_group_sample['N_MeanAge'].to_numpy(dtype=np.float64)
            stories = block_group_sample['N_MeanNoOfStories'].to_numpy(dtype=np.float64)
            baths = block_group_sample['N_MeanFullBathNumber'].to_numpy(dtype=np.float64)
            flood = block_group_sample['N_perc_area_flood'].to_numpy(dtype=np.float64)
            residuals = block_group_sample['residuals'].to_numpy(dtype=np.float64)
            coefficients = np.array(self.simple_anova_coefficients, dtype=np.float64)
            from chance_c.numba_utils import calculate_utilities_with_flood_vectorized
            utilities = calculate_utilities_with_flood_vectorized(sqfeet, age, stories, baths, flood, residuals, coefficients)
            block_group_sample['utility'] = utilities

        elif self.house_choice_mode == 'simple_avoidance_utility' or self.house_choice_mode == 'budget_reduction':  # JY consider moving to method on household agents
            # Use numba-optimized vectorized utility calculation (without flood term)
            sqfeet = block_group_sample['N_MeanSqfeet'].to_numpy(dtype=np.float64)
            age = block_group_sample['N_MeanAge'].to_numpy(dtype=np.float64)
            stories = block_group_sample['N_MeanNoOfStories'].to_numpy(dtype=np.float64)
            baths = block_group_sample['N_MeanFullBathNumber'].to_numpy(dtype=np.float64)
            residuals = block_group_sample['residuals'].to_numpy(dtype=np.float64)
            coefficients = np.array(self.simple_anova_coefficients, dtype=np.float64)
            utilities = calculate_utilities_vectorized(sqfeet, age, stories, baths, residuals, coefficients)
            block_group_sample['utility'] = utilities

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
        agent_move_list = random.sample(self.target.get_institution('all_household_agents').components, no_agents_moving)
        for a in agent_move_list:
            block_group_old_location = self.target.get_node(a.location)
            block_group_new_location = random.choice(block_group_dev_allowed)
            del block_group_old_location.household_agents[a.name]
            block_group_new_location.household_agents[a.name] = a
            a.location = block_group_new_location.name

