import logging
from operator import itemgetter

from pynsim import Engine


class HousingMarket(Engine):
    """An engine class that matches buyers with housing inventory representing the housing market.

    The HousingMarket engine matches buyers with sellers in the housing market through
    an iterative process that prioritizes households based on income and utility preferences.
    It handles both new households entering the market and existing households relocating
    within the domain.

    Args:
        target: The simulation network target containing block group nodes and household data.
        market_mode (str, optional): Mode for market matching algorithm. 
            Currently supports 'top_candidate'. Defaults to 'top_candidate'.
        block_group_sample_size (int, optional): Number of market iterations to perform. 
            Defaults to 10.
        **kwargs: Additional keyword arguments passed to the parent class.

    Inter-module Outputs/Modifications:
        target.unassigned_households (dict): Dictionary of unassigned household agents.
        target.relocating_households (dict): Dictionary of relocating household agents.
        target.get_institution('all_household_agents'): Institution containing all household agents.
        target.get_node(bg).household_agents (dict): Household agents assigned to block group nodes.
        target.get_node(bg).occupied_units (int): Updated occupied units in block group.
        target.get_node(bg).available_units (int): Updated available units in block group.
        target.get_node(bg).demand_exceeds_supply (bool): Flag indicating demand exceeds supply.
    """

    def __init__(self, target, market_mode: str = 'top_candidate', 
                 block_group_sample_size: int = 10, **kwargs) -> None:
        """Initialize the HousingMarket engine.
        
        Args:
            target: The simulation network target containing block group nodes and household data.
            market_mode: Mode for market matching algorithm.
            block_group_sample_size: Number of market iterations to perform.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(HousingMarket, self).__init__(target, **kwargs)
        self.market_mode = market_mode
        self.block_group_sample_size = block_group_sample_size

    def run(self) -> None:
        """Execute the housing market matching process.
        
        Performs iterative matching between households and block groups based on
        utility preferences and income. Handles both new households and relocating
        households, with priority given to higher-income households when demand
        exceeds supply. Households unable to find affordable housing are marked
        as outmigrated.
        """
        # Guard: Check if target is a network (has required attributes)
        if not hasattr(self.target, 'nodes') or not hasattr(self.target, 'unassigned_households') or \
           not hasattr(self.target, 'relocating_households') or not hasattr(self.target, 'hh_utilities_df'):
            return
        
        # Guard: If timestep is not set, use target's current_timestep
        if self.timestep is None:
            if self.target.current_timestep is None:
                logging.warning("No timestep available for housing market engine")
                return
            current_year = self.target.current_timestep.year
        else:
            current_year = self.timestep.year
            
        logging.info("Running the housing market engine, year " + str(current_year))

        for market_iter in range(self.block_group_sample_size):

            logging.info('Housing market iteration: ' + str(market_iter))

            to_delete_unassigned_households = []  # list of households to delete from unassigned dicts for market iteration
            to_delete_relocating_households = []  # list of households to delete from unassigned dicts for market iteration

            if not self.target.unassigned_households and not self.target.relocating_households:  # break out of market iteration loop if no more unassigned households
                break

            block_group_demand = {}  # a dictionary that will identify households and top candidate block_group's
            for household in self.target.unassigned_households.values():
                household_utilities_subset = self.target.hh_utilities_df[(self.target.hh_utilities_df.household == household.name)]
                household_utilities_dict = dict(zip(household_utilities_subset.GEOID, household_utilities_subset.utility))
                sorted_block_group_candidates = sorted(((v,k) for k,v in household_utilities_dict.items()))  # sort block_group candidates from lowest to highest
                try:
                    top_candidate_block_group = sorted_block_group_candidates[-1-market_iter][1]  # get the block_group name for the top candidate (excluding previous top candidates from previous iterations)
                    top_candidate_utility = household_utilities_dict[top_candidate_block_group]
                    if top_candidate_block_group in block_group_demand.keys():
                        block_group_demand[top_candidate_block_group][household.name] = household.income # JY replace top_candidate_utility with household.income (every agent has same utility fx, assume agents with highest income outcompete)
                    else:
                        block_group_demand[top_candidate_block_group] = {}
                        block_group_demand[top_candidate_block_group][household.name] = household.income
                except IndexError:  # if list index is out of range, indicates that no available units are affordable for agent
                    # logging.info(household.name + ' cannot afford any properties and is assumed to migrate outside of domain')

                    # del self.target.unassigned_households[household.name]
                    to_delete_unassigned_households.append(household.name)
                    self.target.get_institution('all_household_agents')._component_map[household.name].location = 'outmigrated'
            for household in self.target.relocating_households.values():
                household_utilities_subset = self.target.hh_utilities_df[(self.target.hh_utilities_df.household == household.name)]
                household_utilities_dict = dict(zip(household_utilities_subset.GEOID, household_utilities_subset.utility))
                sorted_block_group_candidates = sorted(((v,k) for k,v in household_utilities_dict.items()))  # sort block_group candidates from lowest to highest
                try:
                    top_candidate_block_group = sorted_block_group_candidates[-1-market_iter][1]  # get the block_group name for the top candidate (excluding previous top candidates from previous iterations)
                    top_candidate_utility = household_utilities_dict[top_candidate_block_group]
                    if top_candidate_block_group in block_group_demand.keys():
                        block_group_demand[top_candidate_block_group][household.name] = household.income
                    else:
                        block_group_demand[top_candidate_block_group] = {}
                        block_group_demand[top_candidate_block_group][household.name] = household.income
                except IndexError: # if list index is out of range, indicates that no available units are affordable for agent
                    # logging.info(household.name + ' cannot afford any properties and is assumed to migrate outside of domain')
                    to_delete_relocating_households.append(household.name)
                    self.target.get_institution('all_household_agents')._component_map[household.name].location = 'outmigrated'

            for household in to_delete_unassigned_households:
                del self.target.unassigned_households[household]
            for household in to_delete_relocating_households:
                del self.target.relocating_households[household]

            for block_group in block_group_demand.keys():
                no_of_households = len(block_group_demand[block_group])
                if self.target.get_node(block_group).available_units >= no_of_households:  # if block_group has enough available units to accommodate all matching agents, move all agents to location
                    for household_match in block_group_demand[block_group].keys():
                        if self.target.get_institution('all_household_agents')._component_map[household_match].year_of_residence == current_year and \
                                self.target.get_institution('all_household_agents')._component_map[household_match].name[9:16] != 'initial':  # if agent is new to domain
                            self.target.get_node(block_group).household_agents[household_match] = self.target.get_institution('all_household_agents')._component_map[household_match]  # add pynsim household agent to associated block group node
                            self.target.get_node(block_group).occupied_units += 1  # adjust occupied units
                            self.target.get_node(block_group).available_units -= 1  # adjust available units
                            self.target.get_institution('all_household_agents')._component_map[household_match].location = block_group  # change location attribute on household agent
                            del self.target.unassigned_households[household_match]  # delete matched agent from unassigned household dict
                        else:  # if agent already exists (i.e., agent re-locating within domain)
                            self.target.get_node(block_group).household_agents[household_match] = self.target.get_institution('all_household_agents')._component_map[household_match]  # add agent to new block group node
                            self.target.get_node(block_group).occupied_units += 1  # adjust occupied units
                            self.target.get_node(block_group).available_units -= 1  # adjust available units
                            self.target.get_institution('all_household_agents')._component_map[household_match].location = block_group  # change location attribute on household agent
                            del self.target.relocating_households[household_match]  # delete matched agent from relocating household dict
                    block_group_demand[block_group] = {}  # delete all matched agents from household/block_group matching dict
                else:  # else move only those agents with highest utility for block_group up to the amount of available units / JY revise this to highest budgets!
                    self.target.get_node(block_group).demand_exceeds_supply = True  # JY to implement
                    top_matches = dict(sorted(block_group_demand[block_group].items(), key=itemgetter(1), reverse=True)[:self.target.get_node(block_group).available_units])
                    for household_match in top_matches.keys():
                        if self.target.get_institution('all_household_agents')._component_map[household_match].year_of_residence == current_year and \
                                self.target.get_institution('all_household_agents')._component_map[household_match].name[9:16] != 'initial':  # if agent is new to domain
                            self.target.get_node(block_group).household_agents[household_match] = self.target.get_institution('all_household_agents')._component_map[household_match]  # add pynsim household agent to associated block group node
                            self.target.get_node(block_group).occupied_units += 1  # adjust occupied units
                            self.target.get_node(block_group).available_units -= 1  # adjust available units
                            self.target.get_institution('all_household_agents')._component_map[household_match].location = block_group  # change location attribute on household agent
                            del self.target.unassigned_households[household_match]  # delete matched agent from unassigned household dict
                        else:  # if agent already exists (i.e., agent re-locating within domain)
                            self.target.get_node(block_group).household_agents[household_match] = self.target.get_institution('all_household_agents')._component_map[household_match]  # add agent to new block group node
                            self.target.get_node(block_group).occupied_units += 1  # adjust occupied units
                            self.target.get_node(block_group).available_units -= 1  # adjust available units
                            self.target.get_institution('all_household_agents')._component_map[household_match].location = block_group  # change location attribute on household agent
                            del self.target.relocating_households[household_match]  # delete matched agent from unassigned household dict

        # for any households remaining in queue, assume they migrate
        for household in self.target.unassigned_households.values():
            self.target.get_institution('all_household_agents')._component_map[household.name].location = 'outmigrated'
        for household in self.target.relocating_households.values():
            self.target.get_institution('all_household_agents')._component_map[household.name].location = 'outmigrated'
        pass  # to accommodate debugger
