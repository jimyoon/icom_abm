from pynsim import Engine
from model_classes.urban_agents import HHAgent
import random
import logging
import time
import pandas as pd

class NewAgentLocation(Engine):
    """An engine class to determine calculate new household agent's utility for homes.

    The NewAgentLocation class is a pynsim engine that calculates a new household agent's utility for a sample of available homes.
    The target of the engine is a list of unlocated new agents in the queue. For each unlocated agent, the engine samples from available
    homes and calculates a utility function for each of those homes.

    Target:
        s.network: the simulation network

    Args:
        None

    Attributes:
        sample_size (integer): a single value that indicates the sample size for new agent's housing search

    """
    def __init__(self, target, bg_sample_size=10, house_choice_mode='simple_anova_utility', simple_anova_coefficients=[], budget_reduction_perc=.10, **kwargs):
        super(NewAgentLocation, self).__init__(target, **kwargs)
        self.bg_sample_size = bg_sample_size
        self.house_choice_mode = house_choice_mode
        self.simple_anova_coefficients = simple_anova_coefficients
        self.budget_reduction_perc = budget_reduction_perc


    def run(self):
        """ Run the NewAgentLocation Engine. The target of this engine are all new household agents waiting in the location queue.
            For each agent in the household agent location queue, the engine randomly samples from the available homes
            list, calculating an agent utility for each home.
        """

        logging.info("Running the new agent location engine, year " + str(self.target.current_timestep.year))

        # for hh in self.target.unassigned_hhs.values():
        #     bg_budget = self.target.housing_bg_df[(self.target.housing_bg_df.salesprice1993 <= hh.house_budget)]
        #     bg_sample = bg_budget.sample(n=10, replace=True, weights='available_units').GEOID.to_list() # Sample from available units
        #     if not bg_sample:
        #         logging.info(hh.name + ' cannot afford any available homes!')
        #     for bg in bg_sample:
        #         hh.calc_utility_cobb_douglas(bg)
        if self.house_choice_mode == 'cobb_douglas_utility':  # consider moving to method on household agents

            def cobb_douglas_utility(row):
                return (row['average_income_norm'] ** 0.4) * (row['prox_cbd_norm'] ** 0.4) * (
                            row['flood_risk_norm'] ** 0.2)

            self.target.housing_bg_df['utility'] = self.target.housing_bg_df.apply(cobb_douglas_utility, axis=1)

        elif self.house_choice_mode == 'simple_flood_utility':  # JY consider moving to method on household agents
            self.target.housing_bg_df['utility'] = (self.simple_anova_coefficients[0]) + (self.simple_anova_coefficients[1] * self.target.housing_bg_df['N_MeanSqfeet']) + (self.simple_anova_coefficients[2] * self.target.housing_bg_df['N_MeanAge']) \
                                                                + (self.simple_anova_coefficients[3] * self.target.housing_bg_df['N_MeanNoOfStories']) + (self.simple_anova_coefficients[4] * self.target.housing_bg_df['N_MeanFullBathNumber'])\
                                                                + (self.simple_anova_coefficients[5] * self.target.housing_bg_df['N_perc_area_flood']) + (1 * self.target.housing_bg_df['residuals'])  # JY temp change N_perc_area_flood to perc_fld_area

        elif self.house_choice_mode == 'simple_avoidance_utility' or self.house_choice_mode == 'budget_reduction':  # JY consider moving to method on household agents
            self.target.housing_bg_df['utility'] = (self.simple_anova_coefficients[0]) + (self.simple_anova_coefficients[1] * self.target.housing_bg_df['N_MeanSqfeet']) + (self.simple_anova_coefficients[2] * self.target.housing_bg_df['N_MeanAge']) \
                                                                + (self.simple_anova_coefficients[3] * self.target.housing_bg_df['N_MeanNoOfStories']) + (self.simple_anova_coefficients[4] * self.target.housing_bg_df['N_MeanFullBathNumber'])\
                                                                + (1 * self.target.housing_bg_df['residuals'])

        self.target.hh_utilities_dict = {} #Create empty hh_utilities_dict
        to_delete_unassigned_hhs = []
        for hh in self.target.unassigned_hhs.values():
            bg_all = self.target.housing_bg_df
            # JY restart here
            if self.house_choice_mode == 'simple_avoidance_utility':
                if hh.avoidance == True:
                    bg_budget = bg_all[(bg_all.perc_fld_area <= bg_all.perc_fld_area.quantile(.9))]  # JY parameterize which flood quantile risk averse agents avoid
                else:
                    bg_budget = bg_all
                bg_budget = bg_budget[(bg_budget.new_price <= hh.house_budget)]
            elif self.house_choice_mode == 'budget_reduction':
                bg_all['house_budget'] = hh.house_budget
                bg_all.loc[(bg_all.perc_fld_area >= bg_all.perc_fld_area.quantile(.9)), 'house_budget'] = hh.house_budget * (1.0 - self.budget_reduction_perc)
                bg_budget = bg_all[(bg_all.new_price <= bg_all.house_budget)]
            else:
                bg_budget = bg_all[(bg_all.new_price <= hh.house_budget)]  # JY revise to pin to dynamic prices

            try:
                bg_sample = bg_budget.sample(n=10, replace=True,
                                             weights='available_units')  # Sample from available units (JY revisit this weighting)
                bg_sample = bg_sample[['GEOID', 'utility']]
                dictionary = bg_sample.set_index('GEOID')['utility'].to_dict()
                name = str(hh.income) + hh.name
                self.target.hh_utilities_dict[name] = dictionary

            except ValueError:
                logging.info(hh.name + ' cannot afford any available homes!')  # JY: need to pull out of unassigned_hhs
                hh.location = 'outmigrated'
                continue


    # def run_old_version(self):
    #     """ Run the NewAgentLocation Engine. The target of this engine are all new household agents waiting in the location queue.
    #     This version of the engine is a simple proof-of-concept version to illustrate pynsim functionality.
    #     """
    #     # identify block groups in which new residents/development is allowed
    #     bg_dev_allowed = []
    #     for bg in self.target.nodes:
    #         if bg.zoning == 'allowed':
    #             bg_dev_allowed.append(bg)
    #
    #     # assign new population to block groups (currently assumes agents move to a random block group)
    #     new_population = self.target.total_population * self.pop_growth
    #     no_of_new_agents = (new_population + self.no_hhs_per_agent // 2) // self.no_hhs_per_agent  # division with rounding to nearest integer
    #     count = 1
    #     for a in range(int(no_of_new_agents)):
    #         bg = random.choice(bg_dev_allowed)
    #         name = 'hh_agent_' + str(self.timestep.year) + '_' + str(count)
    #         self.target.add_component(HHAgent(name=name, location=bg.name, no_hhs_per_agent=self.no_hhs_per_agent,
    #                                            hh_size=self.hh_size, year_of_residence=self.timestep.year))  # add household agent to pynsim network
    #         bg.hh_agents[self.target.components[-1].name] = self.target.components[-1]  # add pynsim household agent to associated block group node
    #         self.target.get_institution('all_hh_agents').add_component(self.target.components[-1])  # add pynsim household agent to all hh agents institution
    #         count += 1
    #
    #     # make agent relocation decisions (currently assumes that 10% of randomly selected agents move to a random block group)
    #     no_agents_moving = int(len(self.target.get_institution('all_hh_agents').components) * .10)
    #     agent_move_list = random.sample(self.target.get_institution('all_hh_agents').components, no_agents_moving)
    #     for a in agent_move_list:
    #         bg_old_location = self.target.get_node(a.location)
    #         bg_new_location = random.choice(bg_dev_allowed)
    #         del bg_old_location.hh_agents[a.name]
    #         bg_new_location.hh_agents[a.name] = a
    #         a.location = bg_new_location.name

