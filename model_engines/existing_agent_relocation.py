from pynsim import Engine
import random
import logging
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



        for hh in self.target.relocating_hhs.values():
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
        pass  # to accommodate debugger