import logging
import random

from pynsim import Engine
import scipy.stats as stats

from ..model_classes.urban_agents import HouseholdAgent


class NewAgentCreation(Engine):
    """An engine class that creates new agents based upon population growth or exogenous scenario assumptions.

    The NewAgentCreation class is a pynsim engine that creates new agents based upon population growth or exogenous scenario assumptions.
    The target of the engine is the simulation network. Based upon population growth assumptions, the engine creates new household agents
    and adds them to the queue of agents waiting to be assigned to a residence.

    Args:
        target: The simulation network target.
        growth_mode (str): Defined as either "perc" or "exog" depending upon simulation mode.
        growth_rate (float): If growth_mode = "perc", defines the annual percentage population growth rate.
        inc_growth_mode (str): Mode for income growth calculation.
        pop_growth_inc_perc (float): Population growth income percentage.
        inc_growth_perc (float, optional): Income growth percentage. Defaults to 0.05.
        no_households_per_agent (int, optional): Number of households per agent. Defaults to 10.
        household_size (float, optional): Household size. Defaults to 2.7.
        simple_avoidance_perc (float, optional): Simple avoidance percentage. Defaults to 0.10.
        **kwargs: Additional keyword arguments passed to the parent class.

    Inter-module Outputs/Modifications:
        s.network.unassigned_households (dict): Dictionary of HHAgent objects in the location queue (keys are household agent names).
        s.network.get_institution('all_hh_agents') (list): all_hh_agents institution.
    """

    def __init__(self, target, growth_mode: str, growth_rate: float, inc_growth_mode: str, 
                 pop_growth_inc_perc: float, inc_growth_perc: float = 0.05, 
                 no_households_per_agent: int = 10, household_size: float = 2.7,
                 simple_avoidance_perc: float = 0.10, **kwargs) -> None:
        """Initialize the NewAgentCreation engine.

        Args:
            target: The simulation network target.
            growth_mode: Defined as either "perc" or "exog" depending upon simulation mode.
            growth_rate: If growth_mode = "perc", defines the annual percentage population growth rate.
            inc_growth_mode: Mode for income growth calculation.
            pop_growth_inc_perc: Population growth income percentage.
            inc_growth_perc: Income growth percentage.
            no_households_per_agent: Number of households per agent.
            household_size: Household size.
            simple_avoidance_perc: Simple avoidance percentage.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(NewAgentCreation, self).__init__(target, **kwargs)
        self.growth_mode = growth_mode
        self.growth_rate = growth_rate
        self.no_households_per_agent = no_households_per_agent
        self.household_size = household_size
        self.inc_growth_mode = inc_growth_mode
        self.pop_growth_inc_perc = pop_growth_inc_perc
        self.inc_growth_perc = inc_growth_perc
        self.simple_avoidance_perc = simple_avoidance_perc

    def run(self) -> None:
        """Run the NewAgentCreation Engine.

        Creates new agents based upon population growth mode and adds them to the unassigned households queue.
        """
        # Guard: Check if target is a network (has required attributes)
        if not hasattr(self.target, 'total_population') or not hasattr(self.target, 'housing_block_group_df') or \
           not hasattr(self.target, 'unassigned_households') or not hasattr(self.target, 'current_timestep'):
            return
        
        logging.info("Running the new agent creation engine, year " + str(self.target.current_timestep.year))
        # creates new agents based upon population growth mode and adds to the unassigned households queue
        if self.growth_mode == 'perc':
            new_population = self.target.total_population * self.growth_rate
            no_of_new_agents = (new_population / self.household_size + self.no_households_per_agent // 2) // self.no_households_per_agent  # division with rounding to nearest integer

            if self.inc_growth_mode == 'normal_distribution':
                # create gaussian distribution for household income of new population
                lower, upper = 5000, 300000  # truncate distribution to avoid unrealistic incomes
                mu, sigma = self.target.housing_block_group_df.average_income.mean() * (1 + self.inc_growth_perc), self.target.housing_block_group_df.average_income.std()
                X = stats.truncnorm(
                    (lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)

                count = 1
                for a in range(int(no_of_new_agents)):
                    name = 'hh_agent_' + str(self.timestep.year) + '_' + str(count)
                    hh_income = X.rvs(1)[0]  # sample from household income distribution
                    self.target.add_component(HouseholdAgent(name=name, location=None, no_households_per_agent=self.no_households_per_agent,
                                                       household_size=self.household_size, income=hh_income, house_budget_mode='rhea',
                                                      year_of_residence=self.timestep.year, simple_avoidance_perc = self.simple_avoidance_perc))  # add household agent to pynsim network; currently uses landscape avg hh income & size
                    self.target.get_institution('all_household_agents').add_component(self.target.components[-1])  # add pynsim household agent to all household agents institution
                    self.target.unassigned_households[self.target.components[-1].name] = self.target.components[-1]  # add pynsim household agent to unassigned agent dictionary
                    count += 1
            elif self.inc_growth_mode == 'percentile_based':
                # JY ADD CODE HERE
                hh_income = self.target.housing_block_group_df.average_income.quantile(q=self.pop_growth_inc_perc) ### UPDATE WITH LIVE INCOMES!
                count = 1
                for a in range(int(no_of_new_agents)):
                    name = 'hh_agent_' + str(self.timestep.year) + '_' + str(count)
                    self.target.add_component(HouseholdAgent(name=name, location=None, no_households_per_agent=self.no_households_per_agent,
                                                      household_size=self.household_size, income=hh_income, house_budget_mode='rhea',
                                                      year_of_residence=self.timestep.year, simple_avoidance_perc = self.simple_avoidance_perc))  # add household agent to pynsim network; currently uses landscape avg hh income & size
                    self.target.get_institution('all_household_agents').add_component(
                        self.target.components[-1])  # add pynsim household agent to all household agents institution
                    self.target.unassigned_households[self.target.components[-1].name] = self.target.components[
                        -1]  # add pynsim household agent to unassigned agent dictionary
                    count += 1
            elif self.inc_growth_mode == 'random_agent_replication':
                count = 1
                for a in range(int(no_of_new_agents)):
                    name = 'hh_agent_' + str(self.timestep.year) + '_' + str(count)
                    random_agent = random.choice(self.target.get_institution('all_household_agents').components)
                    random_income = random_agent.income
                    self.target.add_component(HouseholdAgent(name=name, location=None, no_households_per_agent=self.no_households_per_agent,
                                                          household_size=self.household_size, income=random_income, house_budget_mode='rhea',
                                                          year_of_residence=self.timestep.year, simple_avoidance_perc = self.simple_avoidance_perc))  # add household agent to pynsim network; currently uses landscape avg hh income & size
                    self.target.get_institution('all_household_agents').add_component(
                        self.target.components[-1])  # add pynsim household agent to all household agents institution
                    self.target.unassigned_households[self.target.components[-1].name] = self.target.components[
                        -1]  # add pynsim household agent to unassigned agent dictionary
                    count += 1
        elif self.growth_mode == 'exog':
            # ADD CODE HERE
            pass

        pass  # to accommodate debugger
