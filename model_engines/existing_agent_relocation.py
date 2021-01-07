from pynsim import Engine
import random

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
        #
        for bg in self.target.nodes:
            no_of_agents = len(bg.hh_agents)  # number of representative household agents
            no_of_agents_moving = round(self.perc_move * no_of_agents)  # number of representative household agents that are moving
            agents_moving = random.sample(list(bg.hh_agents), no_of_agents_moving)  # randomly sample agents that will move
            for hh in agents_moving:
                self.target.relocating_hhs[hh] = self.target.get_institution('all_hh_agents')._component_map[hh]  # add agent to unassigned hh list (is there a better way in pynsim rather than accessing _components_map)
                # need to adjust available units in block group that agent is moving from

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
    def __init__(self, target, bg_sample_size=10, **kwargs):
        super(ExistingAgentLocation, self).__init__(target, **kwargs)
        self.bg_sample_size = bg_sample_size


    def run(self):
        """ Run the ExistingAgentLocation Engine. The target of this engine are all existing household agents waiting in the re-location queue.
            For each agent in the re-location queue, the engine randomly samples from the available homes
            list, calculating an agent utility for each home.
        """
        # Sample from available units
        bg_sample = random.sample(self.target.available_units_list, self.bg_sample_size)

        for hh in self.target.relocating_hhs.values():
            for bg in bg_sample:
                hh.calc_utility(bg)