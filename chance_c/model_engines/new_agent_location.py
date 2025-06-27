import random
import logging

from pynsim import Engine
import pandas as pd

from ..model_classes.urban_agents import HouseholdAgent


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

        # for household in self.target.unassigned_households.values():
        #     block_group_budget = self.target.housing_block_group_df[(self.target.housing_block_group_df.salesprice1993 <= household.house_budget)]
        #     block_group_sample = block_group_budget.sample(n=10, replace=True, weights='available_units').GEOID.to_list() # Sample from available units
        #     if not block_group_sample:
        #         logging.info(household.name + ' cannot afford any available homes!')
        #     for block_group in block_group_sample:
        #         household.calc_utility_cobb_douglas(block_group)

        first = True
        to_delete_unassigned_households = []
        for household in self.target.unassigned_households.values():
            block_group_all = self.target.housing_block_group_df
            # JY restart here
            if self.house_choice_mode == 'simple_avoidance_utility':
                if household.avoidance == True:
                    # block_group_budget = block_group_all[(block_group_all.perc_fld_area <= block_group_all.perc_fld_area.quantile(.9))]  # JY parameterize which flood quantile risk averse agents avoid
                    block_group_budget = block_group_all[(block_group_all.perc_fld_area <= .10)]  # JY threshold for flood zone (10 percent of building footprint inundated)
                else:
                    block_group_budget = block_group_all
                block_group_budget = block_group_budget[(block_group_budget.new_price <= household.house_budget)]
            elif self.house_choice_mode == 'budget_reduction':
                block_group_all['house_budget'] = household.house_budget
                # block_group_all.loc[(block_group_all.perc_fld_area >= block_group_all.perc_fld_area.quantile(.9)), 'house_budget'] = household.house_budget * (1.0 - self.budget_reduction_perc)
                block_group_all.loc[(block_group_all.perc_fld_area >= .10), 'house_budget'] = household.house_budget * (1.0 - self.budget_reduction_perc)
                block_group_budget = block_group_all[(block_group_all.new_price <= block_group_all.house_budget)]
            else:
                block_group_budget = block_group_all[(block_group_all.new_price <= household.house_budget)]  # JY revise to pin to dynamic prices
            if first:
                try:
                    block_group_sample = block_group_budget.sample(n=10, replace=True, weights='available_units')  # Sample from available units (JY revisit this weighting)
                except ValueError:
                    logging.info(household.name + ' cannot afford any available homes!')  # JY: need to pull out of unassigned_households
                    household.location = 'outmigrated'
                    continue
                block_group_sample['household'] = household.name
                block_group_sample['a'] = 0.4  # JY revise - only need this for Cobb-Douglas
                block_group_sample['b'] = 0.4
                block_group_sample['c'] = 0.2
            else:
                try:
                    block_group_append = block_group_budget.sample(n=10, replace=True, weights='available_units')  # Sample from available units
                except ValueError:
                    logging.info(household.name + ' cannot afford any available homes!')  # JY: need to pull out of unassigned_households
                    household.location = 'outmigrated'
                    continue
                block_group_append['household'] = household.name
                block_group_append['a'] = 0.4  # JY revise - only need this for Cobb-Douglas
                block_group_append['b'] = 0.4
                block_group_append['c'] = 0.2
                block_group_sample = pd.concat([block_group_sample, block_group_append], ignore_index=True)

            first = False

        if self.house_choice_mode == 'cobb_douglas_utility':  # consider moving to method on household agents

            def cobb_douglas_utility(row):
                return (row['average_income_norm'] ** row['a']) * (row['prox_cbd_norm'] ** row['b']) * (
                            row['flood_risk_norm'] ** row['c'])

            block_group_sample['utility'] = block_group_sample.apply(cobb_douglas_utility, axis=1)

        elif self.house_choice_mode == 'simple_flood_utility':  # JY consider moving to method on household agents
            block_group_sample['utility'] = (self.simple_anova_coefficients[0]) + \
                (self.simple_anova_coefficients[1] * self.target.housing_block_group_df['N_MeanSqfeet']) + \
                (self.simple_anova_coefficients[2] * self.target.housing_block_group_df['N_MeanAge']) + \
                (self.simple_anova_coefficients[3] * self.target.housing_block_group_df['N_MeanNoOfStories']) + \
                (self.simple_anova_coefficients[4] * self.target.housing_block_group_df['N_MeanFullBathNumber']) + \
                (self.simple_anova_coefficients[5] * self.target.housing_block_group_df['N_perc_area_flood']) + \
                (1 * self.target.housing_block_group_df['residuals'])  # JY temp change N_perc_area_flood to perc_fld_area

        elif self.house_choice_mode == 'simple_avoidance_utility' or self.house_choice_mode == 'budget_reduction':  # JY consider moving to method on household agents
            block_group_sample['utility'] = (self.simple_anova_coefficients[0]) + \
                (self.simple_anova_coefficients[1] * self.target.housing_block_group_df['N_MeanSqfeet']) + \
                (self.simple_anova_coefficients[2] * self.target.housing_block_group_df['N_MeanAge']) + \
                (self.simple_anova_coefficients[3] * self.target.housing_block_group_df['N_MeanNoOfStories']) + \
                (self.simple_anova_coefficients[4] * self.target.housing_block_group_df['N_MeanFullBathNumber']) + \
                (1 * self.target.housing_block_group_df['residuals'])

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

