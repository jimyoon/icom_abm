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
        bg_sample_size (int, optional): Number of market iterations to perform. 
            Defaults to 10.
        **kwargs: Additional keyword arguments passed to the parent class.

    Inter-module Outputs/Modifications:
        target.unassigned_hhs (dict): Dictionary of unassigned household agents.
        target.relocating_hhs (dict): Dictionary of relocating household agents.
        target.get_institution('all_hh_agents'): Institution containing all household agents.
        target.get_node(bg).hh_agents (dict): Household agents assigned to block group nodes.
        target.get_node(bg).occupied_units (int): Updated occupied units in block group.
        target.get_node(bg).available_units (int): Updated available units in block group.
        target.get_node(bg).demand_exceeds_supply (bool): Flag indicating demand exceeds supply.
    """

    def __init__(self, target, market_mode: str = 'top_candidate', 
                 bg_sample_size: int = 10, **kwargs) -> None:
        """Initialize the HousingMarket engine.
        
        Args:
            target: The simulation network target containing block group nodes and household data.
            market_mode: Mode for market matching algorithm.
            bg_sample_size: Number of market iterations to perform.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(HousingMarket, self).__init__(target, **kwargs)
        self.market_mode = market_mode
        self.bg_sample_size = bg_sample_size

    def run(self) -> None:
        """Execute the housing market matching process.
        
        Performs iterative matching between households and block groups based on
        utility preferences and income. Handles both new households and relocating
        households, with priority given to higher-income households when demand
        exceeds supply. Households unable to find affordable housing are marked
        as outmigrated.
        """
        logging.info("Running the housing market engine, year " + str(self.target.current_timestep.year))

        for market_iter in range(self.bg_sample_size):

            logging.info('Housing market iteration: ' + str(market_iter))

            to_delete_unassigned_hhs = []  # list of households to delete from unassigned dicts for market iteration
            to_delete_relocating_hhs = []  # list of households to delete from unassigned dicts for market iteration

            if not self.target.unassigned_hhs and not self.target.relocating_hhs:  # break out of market iteration loop if no more unassigned households
                break
            bg_demand = {}  # a dictionary that will identify hh's and top candidate bg's
            for hh in self.target.unassigned_hhs.values():
                hh_utilities_subset = self.target.hh_utilities_df[(self.target.hh_utilities_df.hh == hh.name)]
                hh_utilities_dict = dict(zip(hh_utilities_subset.GEOID, hh_utilities_subset.utility))
                sorted_bg_candidates = sorted(((v,k) for k,v in hh_utilities_dict.items()))  # sort bg candidates from lowest to highest
                try:
                    top_candidate_bg = sorted_bg_candidates[-1-market_iter][1]  # get the bg name for the top candidate (excluding previous top candidates from previous iterations)
                    top_candidate_utility = hh_utilities_dict[top_candidate_bg]
                    if top_candidate_bg in bg_demand.keys():
                        bg_demand[top_candidate_bg][hh.name] = hh.income # JY replace top_candidate_utility with hh.income (every agent has same utility fx, assume agents with highest income outcompete)
                    else:
                        bg_demand[top_candidate_bg] = {}
                        bg_demand[top_candidate_bg][hh.name] = hh.income
                except IndexError:  # if list index is out of range, indicates that no available units are affordable for agent
                    logging.info(hh.name + ' cannot afford any properties and is assumed to migrate outside of domain')
                    # del self.target.unassigned_hhs[hh.name]
                    to_delete_unassigned_hhs.append(hh.name)
                    self.target.get_institution('all_hh_agents')._component_map[hh.name].location = 'outmigrated'
            for hh in self.target.relocating_hhs.values():
                hh_utilities_subset = self.target.hh_utilities_df[(self.target.hh_utilities_df.hh == hh.name)]
                hh_utilities_dict = dict(zip(hh_utilities_subset.GEOID, hh_utilities_subset.utility))
                sorted_bg_candidates = sorted(((v,k) for k,v in hh_utilities_dict.items()))  # sort bg candidates from lowest to highest
                try:
                    top_candidate_bg = sorted_bg_candidates[-1-market_iter][1]  # get the bg name for the top candidate (excluding previous top candidates from previous iterations)
                    top_candidate_utility = hh_utilities_dict[top_candidate_bg]
                    if top_candidate_bg in bg_demand.keys():
                        bg_demand[top_candidate_bg][hh.name] = hh.income
                    else:
                        bg_demand[top_candidate_bg] = {}
                        bg_demand[top_candidate_bg][hh.name] = hh.income
                except IndexError: # if list index is out of range, indicates that no available units are affordable for agent
                    logging.info(hh.name + ' cannot afford any properties and is assumed to migrate outside of domain')
                    to_delete_relocating_hhs.append(hh.name)
                    self.target.get_institution('all_hh_agents')._component_map[hh.name].location = 'outmigrated'

            for hh in to_delete_unassigned_hhs:
                del self.target.unassigned_hhs[hh]
            for hh in to_delete_relocating_hhs:
                del self.target.relocating_hhs[hh]

            for bg in bg_demand.keys():
                no_of_hhs = len(bg_demand[bg])
                if self.target.get_node(bg).available_units >= no_of_hhs:  # if bg has enough available units to accommodate all matching agents, move all agents to location
                    for hh_match in bg_demand[bg].keys():
                        if self.target.get_institution('all_hh_agents')._component_map[hh_match].year_of_residence == self.timestep.year and \
                                self.target.get_institution('all_hh_agents')._component_map[hh_match].name[9:16] != 'initial':  # if agent is new to domain
                            self.target.get_node(bg).hh_agents[hh_match] = self.target.get_institution('all_hh_agents')._component_map[hh_match]  # add pynsim household agent to associated block group node
                            self.target.get_node(bg).occupied_units += 1  # adjust occupied units
                            self.target.get_node(bg).available_units -= 1  # adjust available units
                            self.target.get_institution('all_hh_agents')._component_map[hh_match].location = bg  # change location attribute on household agent
                            del self.target.unassigned_hhs[hh_match]  # delete matched agent from unassigned hh dict
                        else:  # if agent already exists (i.e., agent re-locating within domain)
                            self.target.get_node(bg).hh_agents[hh_match] = self.target.get_institution('all_hh_agents')._component_map[hh_match]  # add agent to new block group node
                            self.target.get_node(bg).occupied_units += 1  # adjust occupied units
                            self.target.get_node(bg).available_units -= 1  # adjust available units
                            self.target.get_institution('all_hh_agents')._component_map[hh_match].location = bg  # change location attribute on household agent
                            del self.target.relocating_hhs[hh_match]  # delete matched agent from relocating hh dict
                    bg_demand[bg] = {}  # delete all matched agents from hh/bg matching dict
                else:  # else move only those agents with highest utility for bg up to the amount of available units / JY revise this to highest budgets!
                    self.target.get_node(bg).demand_exceeds_supply = True  # JY to implement
                    top_matches = dict(sorted(bg_demand[bg].items(), key=itemgetter(1), reverse=True)[:self.target.get_node(bg).available_units])
                    for hh_match in top_matches.keys():
                        if self.target.get_institution('all_hh_agents')._component_map[hh_match].year_of_residence == self.timestep.year and \
                                self.target.get_institution('all_hh_agents')._component_map[hh_match].name[9:16] != 'initial':  # if agent is new to domain
                            self.target.get_node(bg).hh_agents[hh_match] = self.target.get_institution('all_hh_agents')._component_map[hh_match]  # add pynsim household agent to associated block group node
                            self.target.get_node(bg).occupied_units += 1  # adjust occupied units
                            self.target.get_node(bg).available_units -= 1  # adjust available units
                            self.target.get_institution('all_hh_agents')._component_map[hh_match].location = bg  # change location attribute on household agent
                            del self.target.unassigned_hhs[hh_match]  # delete matched agent from unassigned hh dict
                        else:  # if agent already exists (i.e., agent re-locating within domain)
                            self.target.get_node(bg).hh_agents[hh_match] = self.target.get_institution('all_hh_agents')._component_map[hh_match]  # add agent to new block group node
                            self.target.get_node(bg).occupied_units += 1  # adjust occupied units
                            self.target.get_node(bg).available_units -= 1  # adjust available units
                            self.target.get_institution('all_hh_agents')._component_map[hh_match].location = bg  # change location attribute on household agent
                            del self.target.relocating_hhs[hh_match]  # delete matched agent from unassigned hh dict

        # for any households remaining in queue, assume they migrate
        for hh in self.target.unassigned_hhs.values():
            self.target.get_institution('all_hh_agents')._component_map[hh.name].location = 'outmigrated'
        for hh in self.target.relocating_hhs.values():
            self.target.get_institution('all_hh_agents')._component_map[hh.name].location = 'outmigrated'
        pass  # to accommodate debugger
