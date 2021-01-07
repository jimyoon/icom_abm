from pynsim import Engine
from model_classes.urban_agents import HHAgent

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

    **Inter-module Outputs/Modifications**:
        s.network.unassigned_hhs (dict): dictionary of HHAgent objects in the location queue (keys are household agent names)
        s.network.get_institution('all_hh_agents') (list): all_hh_agents institution
    """

    def __init__(self, target, growth_mode, growth_rate, no_hhs_per_agent=100, hh_size=4, **kwargs):
        super(NewAgentCreation, self).__init__(target, **kwargs)
        self.growth_mode = growth_mode
        self.growth_rate = growth_rate
        self.no_hhs_per_agent = no_hhs_per_agent
        self.hh_size = hh_size

    def run(self):
        """ Run the NewAgentCreation Engine.
        """

        # creates new agents based upon population growth mode and adds to the unassigned households queue
        if self.growth_mode == 'perc':
            new_population = self.target.total_population * self.growth_rate
            no_of_new_agents = (new_population + self.no_hhs_per_agent // 2) // self.no_hhs_per_agent  # division with rounding to nearest integer
            count = 1
            for a in range(int(no_of_new_agents)):
                name = 'hh_agent_' + str(self.timestep.year) + '_' + str(count)
                self.target.add_component(HHAgent(name=name, location=None, no_hhs_per_agent=self.no_hhs_per_agent,
                                                   hh_size=self.hh_size, year_of_residence=self.timestep.year))  # add household agent to pynsim network
                self.target.get_institution('all_hh_agents').add_component(self.target.components[-1])  # add pynsim household agent to all hh agents institution
                self.target.unassigned_hhs[self.target.components[-1].name] = self.target.components[-1]  # add pynsim household agent to unassigned agent dictionary
                count += 1
        elif self.growth_mode == 'exog':
            # need to complete
            pass
