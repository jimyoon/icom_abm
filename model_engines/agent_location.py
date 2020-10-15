from pynsim import Engine
from model_classes.urban_agents import HHAgent
import random

class AgentLocation(Engine):
    def __init__(self, target, pop_growth, no_hhs_per_agent=100, hh_size=4, perc_move=.10, **kwargs):
        super(AgentLocation, self).__init__(target, **kwargs)
        self.pop_growth = pop_growth
        self.no_hhs_per_agent = no_hhs_per_agent
        self.hh_size = hh_size

    def run(self):
        # assign new population to block groups (currently assumes agents move to a random block group)
        new_population = self.target.total_population * self.pop_growth
        no_of_new_agents = (new_population + self.no_hhs_per_agent // 2) // self.no_hhs_per_agent  # division with rounding to nearest integer
        count = 1
        for a in range(int(no_of_new_agents)):
            bg = random.choice(self.target.nodes)
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
            bg_new_location = random.choice(self.target.nodes)
            del bg_old_location.hh_agents[a.name]
            bg_new_location.hh_agents[a.name] = a
            a.location = bg_new_location.name

