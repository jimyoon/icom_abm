from pynsim import Engine
from model_classes.urban_agents import HHAgent
import scipy.stats as stats
import logging

class NewAgentCreation(Engine):
    """An engine class that creates new agent's based upon population growth or exogenous scenario assumptions.

    The NewAgentCreation class is a pynsim engine that creates new agents based upon population growth or exogenous scenario assumptions.
    The target of the engine is the simulation network. Based upon population growth assumptions, the engine creates new household agents
    and adds them to the queue of agents waiting to be assigned to a residence

    **Target**:
        s.network

    **Args**:
        growth_mode (string): defined as either "perc" or "exog" depending upon simulation mode
        growth_rate (float): if growth_mode = "perc", defines the annual percentage population growth rate
        growth_inc (float): if growth_mode = "perc", defines the increase in the mean income for incoming population

    **Inter-module Outputs/Modifications**:
        s.network.unassigned_hhs (dict): dictionary of HHAgent objects in the location queue (keys are household agent names)
        s.network.get_institution('all_hh_agents') (list): all_hh_agents institution
    """

    def __init__(self, target, growth_mode, growth_rate, inc_growth_mode, pop_growth_inc_perc, no_hhs_per_agent=10, hh_size=2.7,
                 simple_avoidance_perc=.10, **kwargs):
        super(NewAgentCreation, self).__init__(target, **kwargs)
        self.growth_mode = growth_mode
        self.growth_rate = growth_rate
        self.no_hhs_per_agent = no_hhs_per_agent
        self.hh_size = hh_size
        self.inc_growth_mode = inc_growth_mode
        self.pop_growth_inc_perc = pop_growth_inc_perc
        self.simple_avoidance_perc = simple_avoidance_perc

    def run(self):
        """ Run the NewAgentCreation Engine.
        """

        logging.info("Running the new agent creation engine, year " + str(self.target.current_timestep.year))
        # creates new agents based upon population growth mode and adds to the unassigned households queue
        if self.growth_mode == 'perc':
            new_population = self.target.total_population * self.growth_rate
            no_of_new_agents = (new_population + self.no_hhs_per_agent // 2) // self.no_hhs_per_agent  # division with rounding to nearest integer
            print("no_of_new_agent is: "+ no_of_new_agents)

            if self.inc_growth_mode == 'normal_distribution':
                # create gaussian distribution for household income of new population
                lower, upper = 5000, 300000  # truncate distribution to avoid unrealistic incomes
                mu, sigma = self.target.housing_bg_df.average_income.mean() * (1 + self.growth_inc), self.target.housing_bg_df.average_income.std()
                X = stats.truncnorm(
                    (lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)

                count = 1
                for a in range(int(no_of_new_agents)):
                    name = 'hh_agent_' + str(self.timestep.year) + '_' + str(count)
                    hh_income = X.rvs(1)[0]  # sample from household income distribution
                    self.target.add_component(HHAgent(name=name, location=None, no_hhs_per_agent=self.no_hhs_per_agent,
                                                       hh_size=self.hh_size, income=hh_income, house_budget_mode='rhea',
                                                      year_of_residence=self.timestep.year, simple_avoidance_perc = self.simple_avoidance_perc))  # add household agent to pynsim network; currently uses landscape avg hh income & size
                    self.target.get_institution('all_hh_agents').add_component(self.target.components[-1])  # add pynsim household agent to all hh agents institution
                    self.target.unassigned_hhs[self.target.components[-1].name] = self.target.components[-1]  # add pynsim household agent to unassigned agent dictionary
                    count += 1
            elif self.inc_growth_mode == 'percentile_based':
                # JY ADD CODE HERE
                hh_income = self.target.housing_bg_df.average_income.quantile(q=self.pop_growth_inc_perc) ### UPDATE WITH LIVE INCOMES!
                count = 1
                for a in range(int(no_of_new_agents)):
                    name = 'hh_agent_' + str(self.timestep.year) + '_' + str(count)
                    self.target.add_component(HHAgent(name=name, location=None, no_hhs_per_agent=self.no_hhs_per_agent,
                                                      hh_size=self.hh_size, income=hh_income, house_budget_mode='rhea',
                                                      year_of_residence=self.timestep.year, simple_avoidance_perc = self.simple_avoidance_perc))  # add household agent to pynsim network; currently uses landscape avg hh income & size
                    self.target.get_institution('all_hh_agents').add_component(
                        self.target.components[-1])  # add pynsim household agent to all hh agents institution
                    self.target.unassigned_hhs[self.target.components[-1].name] = self.target.components[
                        -1]  # add pynsim household agent to unassigned agent dictionary
                    count += 1
        elif self.growth_mode == 'exog':
            # ADD CODE HERE
            pass

        pass  # to accommodate debugger
