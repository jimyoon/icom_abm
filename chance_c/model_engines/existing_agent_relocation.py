import random
import logging
import pandas as pd

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
        target.relocating_hhs (dict): Dictionary of HHAgent objects in the relocation queue.
        bg.hh_agents (dict): Updated household agents dictionary for each block group.
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

        for bg in self.target.nodes:
            no_of_agents = len(bg.hh_agents)  # number of representative household agents
            no_of_agents_moving = round(self.perc_move * no_of_agents)  # number of representative household agents that are moving
            agents_moving = random.sample(list(bg.hh_agents), no_of_agents_moving)  # randomly sample agents that will move
            for hh in agents_moving:
                self.target.relocating_hhs[hh] = self.target.get_institution('all_hh_agents')._component_map[hh]  # add agent to unassigned hh list (is there a better way in pynsim rather than accessing _components_map)
                bg_old_location = self.target.get_node(self.target.get_institution('all_hh_agents')._component_map[hh].location)
                del bg_old_location.hh_agents[hh]  # remove agent from old location
                bg_old_location.occupied_units -= 1  # adjust occupied units
                bg_old_location.available_units += 1  # adjust available units
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
        bg_sample_size (int, optional): Sample size for new agent's housing search. 
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

    def __init__(self, target, bg_sample_size: int = 10, 
                 house_choice_mode: str = 'simple_anova_utility', 
                 simple_anova_coefficients: list = None, 
                 budget_reduction_perc: float = 0.10, **kwargs) -> None:
        """Initialize the ExistingAgentLocation engine.

        Args:
            target: The simulation network target.
            bg_sample_size: Sample size for new agent's housing search.
            house_choice_mode: Mode for house choice utility calculation.
            simple_anova_coefficients: Coefficients for simple ANOVA utility calculation.
            budget_reduction_perc: Budget reduction percentage.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(ExistingAgentLocation, self).__init__(target, **kwargs)
        self.bg_sample_size = bg_sample_size
        self.house_choice_mode = house_choice_mode
        self.simple_anova_coefficients = simple_anova_coefficients or []
        self.budget_reduction_perc = budget_reduction_perc

    def run(self) -> None:
        """Execute the existing agent location process.

        The target of this engine are all existing household agents waiting in the 
        re-location queue. For each agent in the re-location queue, the engine randomly 
        samples from the available homes list, calculating an agent utility for each home.
        """
        logging.info("Running the existing agent relocation engine, year " + str(self.target.current_timestep.year))

        first = True
        for hh in self.target.relocating_hhs.values():
            bg_all = self.target.housing_bg_df
            # JY restart here
            if self.house_choice_mode == 'simple_avoidance_utility':
                if hh.avoidance == True:
                    # bg_budget = bg_all[(bg_all.perc_fld_area <= bg_all.perc_fld_area.quantile(.9))]  # JY parameterize which flood quantile risk averse agents avoid
                    bg_budget = bg_all[(bg_all.perc_fld_area <= .10)]
                else:
                    bg_budget = bg_all
                bg_budget = bg_budget[(bg_budget.new_price <= hh.house_budget)]
            elif self.house_choice_mode == 'budget_reduction':
                bg_all['house_budget'] = hh.house_budget
                bg_all.loc[(bg_all.perc_fld_area >= .10), 'house_budget'] = hh.house_budget * (1.0 - self.budget_reduction_perc)
                bg_budget = bg_all[(bg_all.new_price <= bg_all.house_budget)]
            else:
                bg_budget = bg_all[(bg_all.new_price <= hh.house_budget)]  # JY revise to pin to dynamic prices
            if first:
                try:
                    bg_sample = bg_budget.sample(n=10, replace=True, weights='available_units')  # Sample from available units (JY revisit this weighting)
                except ValueError:
                    logging.info(hh.name + ' cannot afford any available homes!')  # JY: need to pull out of unassigned_hhs
                    hh.location = 'outmigrated'
                    continue
                bg_sample['hh'] = hh.name
                bg_sample['a'] = 0.4
                bg_sample['b'] = 0.4
                bg_sample['c'] = 0.2
            else:
                try:
                    bg_append = bg_budget.sample(n=10, replace=True, weights='available_units')  # Sample from available units
                except ValueError:
                    logging.info(hh.name + ' cannot afford any available homes!')  # JY: need to pull out of unassigned_hhs
                    hh.location = 'outmigrated'
                    continue
                bg_append['hh'] = hh.name
                bg_append['a'] = 0.4
                bg_append['b'] = 0.4
                bg_append['c'] = 0.2
                bg_sample = pd.concat([bg_sample, bg_append], ignore_index=True)

            first = False

        if self.house_choice_mode == 'cobb_douglas_utility':  # consider moving to method on household agents

            def cobb_douglas_utility(row):
                return (row['average_income_norm'] ** row['a']) * (row['prox_cbd_norm'] ** row['b']) * (row['flood_risk_norm'] ** row['c'])

            bg_sample['utility'] = bg_sample.apply(cobb_douglas_utility, axis=1)

        elif self.house_choice_mode == 'simple_flood_utility':  # JY consider moving to method on household agents
            bg_sample['utility'] = (self.simple_anova_coefficients[0]) + \
                (self.simple_anova_coefficients[1] * self.target.housing_bg_df['N_MeanSqfeet']) + \
                (self.simple_anova_coefficients[2] * self.target.housing_bg_df['N_MeanAge']) + \
                (self.simple_anova_coefficients[3] * self.target.housing_bg_df['N_MeanNoOfStories']) + \
                (self.simple_anova_coefficients[4] * self.target.housing_bg_df['N_MeanFullBathNumber']) + \
                (self.simple_anova_coefficients[5] * self.target.housing_bg_df['N_perc_area_flood']) + \
                (1 * self.target.housing_bg_df['residuals'])  # JY temp change N_perc_area_flood to perc_fld_area

        elif self.house_choice_mode == 'simple_avoidance_utility' or self.house_choice_mode == 'budget_reduction':  # JY consider moving to method on household agents
            bg_sample['utility'] = (self.simple_anova_coefficients[0]) + \
                (self.simple_anova_coefficients[1] * self.target.housing_bg_df['N_MeanSqfeet']) + \
                (self.simple_anova_coefficients[2] * self.target.housing_bg_df['N_MeanAge']) + \
                (self.simple_anova_coefficients[3] * self.target.housing_bg_df['N_MeanNoOfStories']) + \
                (self.simple_anova_coefficients[4] * self.target.housing_bg_df['N_MeanFullBathNumber']) + \
                (1 * self.target.housing_bg_df['residuals'])

        try:
            self.target.hh_utilities_df = self.target.hh_utilities_df.append(bg_sample[['GEOID', 'hh', 'utility']])
        except AttributeError: # Added to accommodate turning off new agent engines
            self.target.hh_utilities_df = bg_sample[['GEOID', 'hh', 'utility']]

        pass  # to accommodate debugger
