import random
import logging
import pandas as pd
import numpy as np
import polars as pl
from chance_c.numba_utils import filter_and_sample, calculate_utilities_vectorized, calculate_utilities_with_flood_vectorized, calculate_cobb_douglas_utilities
from chance_c.polars_utils import fast_filter_and_sample_polars, fast_concat_dataframes, convert_polars_to_pandas

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

    def run(self) -> None:
        """Run the ExistingAgentLocation engine.
        
        Processes all relocating household agents waiting in the location queue.
        For each agent, samples from available homes and calculates utility
        scores based on the specified house choice mode. Agents that cannot
        afford any homes are marked as outmigrated.
        """
        logging.info("Running the existing agent location engine, year " + str(self.target.current_timestep.year))

        # Convert block group DataFrame to Polars, excluding geometry
        block_group_all = pl.from_pandas(self.target.housing_block_group_df.drop(columns=['geometry']))
        all_samples = []
        to_delete_relocating_households = []
        for household in self.target.relocating_households.values():
            # Filtering in Polars
            filtered = block_group_all.filter(pl.col('new_price') <= household.house_budget)
            if filtered.height == 0:
                logging.info(household.name + ' cannot afford any available homes!')
                household.location = 'outmigrated'
                continue
            n_sample = 10
            # Fast sampling in Polars
            try:
                sampled = filtered.sample(n=min(n_sample, filtered.height), with_replacement=True, weights='available_units')
            except Exception:
                sampled = filtered.sample(n=min(n_sample, filtered.height), with_replacement=True)
            sampled = sampled.with_columns([
                pl.lit(household.name).alias('household'),
                pl.lit(0.4).alias('a'),
                pl.lit(0.4).alias('b'),
                pl.lit(0.2).alias('c')
            ])
            all_samples.append(sampled)

        # Efficient single concatenation
        if not all_samples:
            self.target.hh_utilities_df = convert_polars_to_pandas(pl.DataFrame([{'GEOID': '', 'household': '', 'utility': 0.0}]))
            return
        block_group_sample = fast_concat_dataframes(all_samples)

        # Utility calculation (convert to numpy for numba)
        if self.house_choice_mode == 'cobb_douglas_utility':
            income = block_group_sample['average_income_norm'].to_numpy().astype(np.float64)
            prox_cbd = block_group_sample['prox_cbd_norm'].to_numpy().astype(np.float64)
            flood_risk = block_group_sample['flood_risk_norm'].to_numpy().astype(np.float64)
            a = block_group_sample['a'].to_numpy().astype(np.float64)
            b = block_group_sample['b'].to_numpy().astype(np.float64)
            c = block_group_sample['c'].to_numpy().astype(np.float64)
            utilities = calculate_cobb_douglas_utilities(income, prox_cbd, flood_risk, a, b, c)
            block_group_sample = block_group_sample.with_columns(pl.Series('utility', utilities))
        elif self.house_choice_mode == 'simple_flood_utility':
            sqfeet = block_group_sample['N_MeanSqfeet'].to_numpy().astype(np.float64)
            age = block_group_sample['N_MeanAge'].to_numpy().astype(np.float64)
            stories = block_group_sample['N_MeanNoOfStories'].to_numpy().astype(np.float64)
            baths = block_group_sample['N_MeanFullBathNumber'].to_numpy().astype(np.float64)
            flood = block_group_sample['N_perc_area_flood'].to_numpy().astype(np.float64)
            residuals = block_group_sample['residuals'].to_numpy().astype(np.float64)
            coefficients = np.array(self.simple_anova_coefficients, dtype=np.float64)
            utilities = calculate_utilities_with_flood_vectorized(sqfeet, age, stories, baths, flood, residuals, coefficients)
            block_group_sample = block_group_sample.with_columns(pl.Series('utility', utilities))
        elif self.house_choice_mode == 'simple_avoidance_utility' or self.house_choice_mode == 'budget_reduction':
            sqfeet = block_group_sample['N_MeanSqfeet'].to_numpy().astype(np.float64)
            age = block_group_sample['N_MeanAge'].to_numpy().astype(np.float64)
            stories = block_group_sample['N_MeanNoOfStories'].to_numpy().astype(np.float64)
            baths = block_group_sample['N_MeanFullBathNumber'].to_numpy().astype(np.float64)
            residuals = block_group_sample['residuals'].to_numpy().astype(np.float64)
            coefficients = np.array(self.simple_anova_coefficients, dtype=np.float64)
            utilities = calculate_utilities_vectorized(sqfeet, age, stories, baths, residuals, coefficients)
            block_group_sample = block_group_sample.with_columns(pl.Series('utility', utilities))

        # Convert back to pandas for compatibility
        self.target.hh_utilities_df = convert_polars_to_pandas(block_group_sample.select(['GEOID', 'household', 'utility']))
