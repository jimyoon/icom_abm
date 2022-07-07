from pynsim import Engine
import random
import logging
import pandas as pd

class agent_out_migration(Engine):
    """An engine class to identify agents to migrate out of the study area.

    The agent_out_migration class is a pynsim engine that determines which agents wish to outmigrate.
    The target of the engine is the model landscape.

    Target:
        s.network: the simulation network

    Args:
        None

    Attributes:
        perc_move (float): the percentage of agents that desire to move in any given time period

    """
    def __init__(self, target, perc_migrate, **kwargs):
        super(agent_out_migration, self).__init__(target, **kwargs)
        self.perc_migrate = perc_migrate


    def run(self):
        """ Run the agent_out_migration Engine. The target of this engine is the simulation landscape.
            For each block group, we randomly sample a percentage of the existing household population to out-migrate.
            The engine vacates the agent's existing property (adding the property to the block group's available unit)
            and mark the agent as out-migrated.
        """
        logging.info("Running the agent out-migration engine, year " + str(self.target.current_timestep.year))

        for bg in self.target.nodes:
            no_of_agents = len(bg.hh_agents)  # number of representative household agents
            no_of_agents_migrating = round(abs(self.perc_migrate) * no_of_agents)  # number of representative household agents that are migrating out
            agents_migrating = random.sample(list(bg.hh_agents), no_of_agents_migrating)  # randomly sample agents that will out-migrate
            for hh in agents_migrating:
                bg_old_location = self.target.get_node(self.target.get_institution('all_hh_agents')._component_map[hh].location)
                del bg_old_location.hh_agents[hh]  # remove agent from old location
                bg_old_location.occupied_units -= 1  # adjust occupied units
                bg_old_location.available_units += 1  # adjust available units
                self.target.get_institution('all_hh_agents')._component_map[hh].location = 'outmigrated'
        pass  # to accommodate debugger