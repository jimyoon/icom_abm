from pynsim import Engine
from model_classes.urban_agents import HHAgent
import random

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
    def __init__(self, target, bg_sample_size=10, **kwargs):
        super(NewAgentLocation, self).__init__(target, **kwargs)
        self.bg_sample_size = bg_sample_size


    def run(self):
        """ Run the NewAgentLocation Engine. The target of this engine are all new household agents waiting in the location queue.
            For each agent in the household agent location queue, the engine randomly samples from the available homes
            list, calculating an agent utility for each home.
        """

        for hh in self.target.unassigned_hhs.values():
            bg_sample = random.sample(self.target.available_units_list, self.bg_sample_size)  # Sample from available units
            for bg in bg_sample:
                hh.calc_utility_cobb_douglas(bg)

        pass  # to accommodate debugger


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

