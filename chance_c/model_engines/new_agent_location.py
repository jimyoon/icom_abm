import random
import logging

from pynsim import Engine
import pandas as pd

from ..model_classes.urban_agents import HHAgent


class NewAgentLocation(Engine):
    """Calculate new household agent's utility for available homes.
    
    A pynsim engine that calculates utility scores for new household agents
    considering a sample of available homes. The engine processes unlocated
    agents in the queue, samples from available homes, and calculates utility
    functions for each home based on the specified choice mode.
    
    Args:
        target: The simulation network containing housing data and agents.
        bg_sample_size: Number of block groups to sample for each agent.
            Defaults to 10.
        house_choice_mode: Method for calculating housing utility. Options:
            'simple_anova_utility', 'cobb_douglas_utility', 'simple_flood_utility',
            'simple_avoidance_utility', 'budget_reduction'. Defaults to
            'simple_anova_utility'.
        simple_anova_coefficients: Coefficients for ANOVA-based utility
            calculation. Defaults to empty list.
        budget_reduction_perc: Percentage reduction in budget for flood-prone
            areas when using budget_reduction mode. Defaults to 0.10.
        **kwargs: Additional keyword arguments passed to parent class.
    
    Attributes:
        bg_sample_size: Number of block groups to sample per agent.
        house_choice_mode: Selected utility calculation method.
        simple_anova_coefficients: Coefficients for ANOVA utility calculation.
        budget_reduction_perc: Budget reduction percentage for flood areas.
    """
    
    def __init__(
        self, 
        target, 
        bg_sample_size: int = 10, 
        house_choice_mode: str = 'simple_anova_utility', 
        simple_anova_coefficients: list = None, 
        budget_reduction_perc: float = 0.10, 
        **kwargs
    ) -> None:
        """Initialize the NewAgentLocation engine.
        
        Args:
            target: The simulation network target.
            bg_sample_size: Number of block groups to sample for each agent.
            house_choice_mode: Method for calculating housing utility.
            simple_anova_coefficients: Coefficients for ANOVA-based utility.
            budget_reduction_perc: Budget reduction percentage for flood areas.
            **kwargs: Additional keyword arguments.
        """
        super(NewAgentLocation, self).__init__(target, **kwargs)
        self.bg_sample_size = bg_sample_size
        self.house_choice_mode = house_choice_mode
        self.simple_anova_coefficients = simple_anova_coefficients or []
        self.budget_reduction_perc = budget_reduction_perc

    def run(self) -> None:
        """Run the NewAgentLocation engine.
        
        Processes all new household agents waiting in the location queue.
        For each agent, samples from available homes and calculates utility
        scores based on the specified house choice mode. Agents that cannot
        afford any homes are marked as outmigrated.
        """
        logging.info("Running the new agent location engine, year " + str(self.target.current_timestep.year))

        # for hh in self.target.unassigned_hhs.values():
        #     bg_budget = self.target.housing_bg_df[(self.target.housing_bg_df.salesprice1993 <= hh.house_budget)]
        #     bg_sample = bg_budget.sample(n=10, replace=True, weights='available_units').GEOID.to_list() # Sample from available units
        #     if not bg_sample:
        #         logging.info(hh.name + ' cannot afford any available homes!')
        #     for bg in bg_sample:
        #         hh.calc_utility_cobb_douglas(bg)

        first = True
        to_delete_unassigned_hhs = []
        for hh in self.target.unassigned_hhs.values():
            bg_all = self.target.housing_bg_df
            # JY restart here
            if self.house_choice_mode == 'simple_avoidance_utility':
                if hh.avoidance == True:
                    # bg_budget = bg_all[(bg_all.perc_fld_area <= bg_all.perc_fld_area.quantile(.9))]  # JY parameterize which flood quantile risk averse agents avoid
                    bg_budget = bg_all[(bg_all.perc_fld_area <= .10)]  # JY threshold for flood zone (10 percent of building footprint inundated)
                else:
                    bg_budget = bg_all
                bg_budget = bg_budget[(bg_budget.new_price <= hh.house_budget)]
            elif self.house_choice_mode == 'budget_reduction':
                bg_all['house_budget'] = hh.house_budget
                # bg_all.loc[(bg_all.perc_fld_area >= bg_all.perc_fld_area.quantile(.9)), 'house_budget'] = hh.house_budget * (1.0 - self.budget_reduction_perc)
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
                bg_sample['a'] = 0.4  # JY revise - only need this for Cobb-Douglas
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
                bg_append['a'] = 0.4  # JY revise - only need this for Cobb-Douglas
                bg_append['b'] = 0.4
                bg_append['c'] = 0.2
                bg_sample = pd.concat([bg_sample, bg_append], ignore_index=True)

            first = False

        if self.house_choice_mode == 'cobb_douglas_utility':  # consider moving to method on household agents

            def cobb_douglas_utility(row):
                return (row['average_income_norm'] ** row['a']) * (row['prox_cbd_norm'] ** row['b']) * (
                            row['flood_risk_norm'] ** row['c'])

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

        self.target.hh_utilities_df = bg_sample[['GEOID', 'hh', 'utility']]


    def run_old_version(self):
        """ Run the NewAgentLocation Engine. The target of this engine are all new household agents waiting in the location queue.
        This version of the engine is a simple proof-of-concept version to illustrate pynsim functionality.
        """
        # identify block groups in which new residents/development is allowed
        bg_dev_allowed = []
        for bg in self.target.nodes:
            if bg.zoning == 'allowed':
                bg_dev_allowed.append(bg)

        # assign new population to block groups (currently assumes agents move to a random block group)
        new_population = self.target.total_population * self.pop_growth
        no_of_new_agents = (new_population + self.no_hhs_per_agent // 2) // self.no_hhs_per_agent  # division with rounding to nearest integer
        count = 1
        for a in range(int(no_of_new_agents)):
            bg = random.choice(bg_dev_allowed)
            name = 'hh_agent_' + str(self.timestep.year) + '_' + str(count)
            self.target.add_component(HHAgent(name=name, location=bg.name, no_hhs_per_agent=self.no_hhs_per_agent,
                                               hh_size=self.hh_size, year_of_residence=self.timestep.year))  # add household agent to pynsim network
            bg.hh_agents[self.target.components[-1].name] = self.target.components[-1]  # add pynsim household agent to associated block group node
            self.target.get_institution('all_hh_agents').add_component(self.target.components[-1])  # add pynsim household agent to all hh agents institution
            count += 1

        # make agent relocation decisions (currently assumes that 10% of randomly selected agents move to a random block group)
        no_agents_moving = int(len(self.target.get_institution('all_hh_agents').components) * .10)
        agent_move_list = random.sample(self.target.get_institution('all_hh_agents').components, no_agents_moving)
        for a in agent_move_list:
            bg_old_location = self.target.get_node(a.location)
            bg_new_location = random.choice(bg_dev_allowed)
            del bg_old_location.hh_agents[a.name]
            bg_new_location.hh_agents[a.name] = a
            a.location = bg_new_location.name

