from pynsim import Engine
import random
import logging
import numpy as np
import pandas as pd

class ExistingAgentReloSampler(Engine):
    """An engine class to identify existing agents to relocate and determine utility for homes.

    The ExistingAgentRelocation class is a pynsim engine that determines which agents wish to relocate.
    The target of the engine is the model landscape.

    Target:
        s.network: the simulation network

    Args:
        None

    Attributes:
        perc_move (float): the percentage of agents that desire to move in any given time period

    """
    def __init__(self, target, perc_move=.10, **kwargs):
        super(ExistingAgentReloSampler, self).__init__(target, **kwargs)
        self.perc_move = perc_move


    def run(self):
        """ Run the ExistingAgentRelocation Engine. The target of this engine is the simulation landscape.
            For each block group, we randomly sample a percentage of the existing household population to relocate.
            The engine vacates the agent's existing property (adding the property to the block group's available unit)
            and adds the agent to the unassigned hh agents queue.
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
    """An engine class to determine calculate existing (relocating) household agent's utility for homes.

    The ExistingAgentLocation class is a pynsim engine that calculates an existing/relocating household agent's utility for a sample of available homes.
    The target of the engine is a list of relocating existing agents in the queue. For each relocating agent, the engine samples from available
    homes and calculates a utility function for each of those homes.

    Target:
        s.network: the simulation network

    Args:
        None

    Attributes:
        sample_size (integer): a single value that indicates the sample size for new agent's housing search

    """
    def __init__(self, target, bg_sample_size=10, house_choice_mode='simple_anova_utility', simple_anova_coefficients=[], budget_reduction_perc=.10, **kwargs):
        super(ExistingAgentLocation, self).__init__(target, **kwargs)
        self.bg_sample_size = bg_sample_size
        self.house_choice_mode = house_choice_mode
        self.simple_anova_coefficients = simple_anova_coefficients
        self.budget_reduction_perc = budget_reduction_perc


    def run(self):
        """ Run the ExistingAgentLocation Engine. The target of this engine are all existing household agents waiting in the re-location queue.
            For each agent in the re-location queue, the engine randomly samples from the available homes
            list, calculating an agent utility for each home.
        """

        logging.info("Running the existing agent relocation engine, year " + str(self.target.current_timestep.year))

        # for hh in self.target.relocating_hhs.values():
        #     bg_budget = self.target.housing_bg_df[(self.target.housing_bg_df.salesprice1993 <= hh.house_budget)]
        #     if bg_budget.empty:
        #         logging.info(hh.name + ' cannot afford any available homes!')
        #     else:
        #         bg_sample = bg_budget.sample(n=10, replace=True, weights='available_units').GEOID.to_list()  # Sample from available units
        #     for bg in bg_sample:
        #         hh.calc_utility_cobb_douglas(bg)

        first = True
        for hh in self.target.relocating_hhs.values():
            bg_all = self.target.housing_bg_df.copy()
            column_index = self.target.column_index.copy()
            # JY restart here
            if self.house_choice_mode == 'simple_avoidance_utility':
                if hh.avoidance == True:
                    mask = (bg_all[:, column_index['perc_fld_area']] <= np.percentile(
                        bg_all[:, column_index['perc_fld_area']], 90))
                    bg_budget = bg_all[mask, :]  # JY parameterize which flood quantile risk averse agents avoid
                else:
                    bg_budget = bg_all
                mask = (bg_budget[:, column_index['new_price']] <= hh.house_budget)
                bg_budget = bg_budget[mask, :]
            elif self.house_choice_mode == 'budget_reduction':
                bg_all = np.append(bg_all, np.array([hh.house_budget for i in range(0, bg_all.shape[0])]).reshape(
                    bg_all.shape[0], 1), axis=1)
                column_index['house_budget'] = bg_all.shape[1] - 1
                index = (bg_all[:, column_index['perc_fld_area']] >= np.percentile(
                    bg_all[:, column_index['perc_fld_area']], 90))
                bg_all[index, column_index['house_budget']] = hh.house_budget * (1.0 - self.budget_reduction_perc)
                mask = (bg_all[:, column_index['new_price']] <= bg_all[:, column_index['house_budget']])
                bg_budget = bg_all[mask, :]
            else:
                mask = (bg_all[:, column_index['new_price']] <= hh.house_budget)
                bg_budget = bg_all[mask, :]  # JY revise to pin to dynamic prices
            if first:
                try:
                    avail = bg_budget[:, column_index['available_units']]
                    weights = np.array(avail / sum(avail), dtype='float64')
                    index = np.random.choice(list(range(bg_budget.shape[0])), size=10, replace=True, p=weights)
                    bg_sample = bg_budget[index, :]  # Sample from available units (JY revisit this weighting)
                except (ValueError, ZeroDivisionError):
                    logging.info(
                        hh.name + ' cannot afford any available homes!')  # JY: need to pull out of unassigned_hhs
                    hh.location = 'outmigrated'
                    continue
                else:
                    bg_sample = np.append(bg_sample, np.array([hh.name for i in range(0, bg_sample.shape[0])]).reshape(
                        bg_sample.shape[0], 1), axis=1)
                    column_index['hh'] = bg_sample.shape[1] - 1
                    bg_sample = np.append(bg_sample,
                                          np.array([0.4 for i in range(0, bg_sample.shape[0])]).reshape(
                                              bg_sample.shape[0],
                                              1), axis=1)
                    column_index['a'] = bg_sample.shape[1] - 1
                    bg_sample = np.append(bg_sample,
                                          np.array([0.4 for i in range(0, bg_sample.shape[0])]).reshape(
                                              bg_sample.shape[0],
                                              1), axis=1)
                    column_index['b'] = bg_sample.shape[1] - 1
                    bg_sample = np.append(bg_sample,
                                          np.array([0.2 for i in range(0, bg_sample.shape[0])]).reshape(
                                              bg_sample.shape[0],
                                              1), axis=1)
                    column_index['c'] = bg_sample.shape[1] - 1

            else:
                try:
                    avail = bg_budget[:, column_index['available_units']]
                    weights = np.array(avail / sum(avail), dtype='float64')
                    index = np.random.choice(list(range(bg_budget.shape[0])), size=10, replace=True, p=weights)
                    bg_append = bg_budget[index, :]  # Sample from available units
                except (ValueError, ZeroDivisionError):
                    logging.info(
                        hh.name + ' cannot afford any available homes!')  # JY: need to pull out of unassigned_hhs
                    hh.location = 'outmigrated'
                    continue
                else:
                    bg_append = np.append(bg_append, np.array([hh.name for i in range(0, bg_append.shape[0])]).reshape(
                        bg_append.shape[0], 1), axis=1)
                    column_index['hh'] = bg_append.shape[1] - 1
                    bg_append = np.append(bg_append, np.array([0.4 for i in range(0, bg_append.shape[0])]).reshape(
                        bg_append.shape[0], 1), axis=1)
                    column_index['a'] = bg_append.shape[1] - 1
                    bg_append = np.append(bg_append, np.array([0.4 for i in range(0, bg_append.shape[0])]).reshape(
                        bg_append.shape[0], 1), axis=1)
                    column_index['b'] = bg_append.shape[1] - 1
                    bg_append = np.append(bg_append, np.array([0.2 for i in range(0, bg_append.shape[0])]).reshape(
                        bg_append.shape[0], 1), axis=1)
                    column_index['c'] = bg_append.shape[1] - 1
                    bg_sample = np.vstack((bg_sample, bg_append))



            first = False

        if self.house_choice_mode == 'cobb_douglas_utility':  # consider moving to method on household agents

            def cobb_douglas_utility(row):
                return (row[column_index['average_income_norm']] ** row[column_index['a']]) * (
                            row[column_index['prox_cbd_norm']] ** row[column_index['b']]) * (
                               row[column_index['flood_risk_norm']] ** row[column_index['c']])

            utility = np.apply_along_axis(cobb_douglas_utility, 1, bg_sample)
            bg_sample = np.append(bg_sample, np.array(utility).reshape(bg_sample.shape[0], 1), axis=1)
            column_index['utility'] = bg_sample.shape[1] - 1

        elif self.house_choice_mode == 'simple_flood_utility':  # JY consider moving to method on household agents
            utility = (self.simple_anova_coefficients[0]) + (
                    self.simple_anova_coefficients[1] * bg_sample[:, column_index['N_MeanSqfeet']]) \
                      + (self.simple_anova_coefficients[2] * bg_sample[:, column_index['N_MeanAge']]) \
                      + (self.simple_anova_coefficients[3] * bg_sample[:, column_index['N_MeanNoOfStories']]) \
                      + (self.simple_anova_coefficients[4] * bg_sample[:, column_index['N_MeanFullBathNumber']]) \
                      + (self.simple_anova_coefficients[5] * bg_sample[:, column_index['N_perc_area_flood']]) \
                      + (1 * bg_sample[:, column_index['residuals']])
            bg_sample = np.append(bg_sample, np.array(utility).reshape(bg_sample.shape[0], 1), axis=1)
            column_index['utility'] = bg_sample.shape[1] - 1

        elif self.house_choice_mode == 'simple_avoidance_utility' or self.house_choice_mode == 'budget_reduction':  # JY consider moving to method on household agents
            utility = (self.simple_anova_coefficients[0]) + (
                    self.simple_anova_coefficients[1] * bg_sample[:, column_index['N_MeanSqfeet']]) \
                      + (self.simple_anova_coefficients[2] * bg_sample[:, column_index['N_MeanAge']]) \
                      + (self.simple_anova_coefficients[3] * bg_sample[:, column_index['N_MeanNoOfStories']]) \
                      + (self.simple_anova_coefficients[4] * bg_sample[:, column_index['N_MeanFullBathNumber']]) \
                      + (1 * bg_sample[:, column_index['residuals']])
            bg_sample = np.append(bg_sample, np.array(utility).reshape(bg_sample.shape[0], 1), axis=1)
            column_index['utility'] = bg_sample.shape[1] - 1

        bg_sample = bg_sample[:, [column_index['GEOID'], column_index['hh'], column_index['utility']]]
        self.target.hh_utilities_df = np.vstack((self.target.hh_utilities_df, bg_sample))

        pass  # to accommodate debugger
