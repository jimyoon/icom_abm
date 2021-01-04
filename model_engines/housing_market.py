from pynsim import Engine
from operator import itemgetter

class HousingMarket(Engine):
    """An engine class that matches buyers with housing inventory representing the housing market.

    The HousingMarket engine matches buyers with sellers in the housing market.

    **Target**:
        s.network

    **Args**:
        market_mode (string): defined to indicate the type of market

    **Inter-module Outputs/Modifications**:
        s.network.unassigned_hhs (list): list of HHAgent objects that are in the location queue
        s.network.get_institution('all_hh_agents') (list): all_hh_agents institution
    """

    def __init__(self, target, market_mode='top_candidate', bg_sample_size=10, **kwargs):
        super(HousingMarket, self).__init__(target, **kwargs)
        self.market_mode = market_mode
        self.bg_sample_size = bg_sample_size

    def run(self):
        """ Run the HousingMarket Engine.
        """
        for market_iter in range(self.bg_sample_size):
            if not self.target.unassigned_hhs and not self.target.relocating_hhs:  # break out of market iteration loop if no more unassigned households
                break
            bg_demand = {}  # a dictionary that will identify hh's and top candidate bg's
            for hh in self.target.unassigned_hhs:
                sorted_bg_candidates = sorted(((v,k) for k,v in hh.hh_utilities.items()))  # sort bg candidates from lowest to highest
                top_candidate_bg = sorted_bg_candidates[-1-market_iter][1]  # get the bg name for the top candidate (excluding previous top candidates from previous iterations)
                top_candidate_utility = hh.hh_utilities[top_candidate_bg]
                if top_candidate_bg in bg_demand.keys():
                    bg_demand[top_candidate_bg][hh.name] = top_candidate_utility
                else:
                    bg_demand[top_candidate_bg] = {}
                    bg_demand[top_candidate_bg][hh.name] = top_candidate_utility
            for hh in self.target.relocating_hhs:
                sorted_bg_candidates = sorted(((v,k) for k,v in hh.hh_utilities.items()))  # sort bg candidates from lowest to highest
                top_candidate_bg = sorted_bg_candidates[-1-market_iter][1]  # get the bg name for the top candidate (excluding previous top candidates from previous iterations)
                if top_candidate_bg in bg_demand.keys():
                    bg_demand[top_candidate_bg][hh.name] = top_candidate_utility
                else:
                    bg_demand[top_candidate_bg] = {}
                    bg_demand[top_candidate_bg][hh.name] = top_candidate_utility

            for bg in bg_demand.keys():
                no_of_hhs = len(bg_demand[bg])
                if self.target.get_node(bg).available_units >= no_of_hhs:  # if bg has enough available units to accommodate all matching agents, move all agents to location
                    for hh_match in bg_demand[bg].keys():
                        if self.target.get_institution('all_hh_agents')._component_map[hh_match].year_of_residence == self.timestep.year:  # if agent is new to domain
                            self.target.get_node(bg).hh_agents[hh_match] = self.target.get_institution('all_hh_agents')._component_map[hh_match]  # add pynsim household agent to associated block group node
                            del bg_demand[bg][hh_match]  # delete matched agent from hh/bg matching dict
                            del self.target.unassigned_hhs[hh_match]  # delete matched agent from unassigned hh dict
                        else:  # if agent already exists (i.e., agent re-locating within domain)
                            bg_old_location = self.target.get_node(hh_match.location)
                            del bg_old_location.hh_agents[hh_match]  # remove agent from old location
                            self.target.get_node(bg).hh_agents[hh_match] = self.target.get_institution('all_hh_agents')._component_map[hh_match]  # add agent to new block group node
                            del bg_demand[bg][hh_match]  # delete matched agent from hh/bg matching dict
                            del self.target.relocating_hhs[hh_match]  # delete matched agent from unassigned hh dict
                else:  # else move only those agents with highest utility for bg up to the amount of available units
                    top_matches = dict(sorted(bg_demand[bg].items(), key=itemgetter(1), reverse=True)[:self.target.get_node(bg).available_units])
                    for hh_match in top_matches.keys():
                        if self.target.get_institution('all_hh_agents')._component_map[hh_match].year_of_residence == self.timestep.year:  # if agent is new to domain
                            self.target.get_node(bg).hh_agents[hh_match] = self.target.get_institution('all_hh_agents')._component_map[hh_match]  # add pynsim household agent to associated block group node
                            del bg_demand[bg][hh_match]  # delete matched agent from hh/bg matching dict
                            del self.target.unassigned_hhs[hh_match]  # delete matched agent from unassigned hh dict
                        else:  # if agent already exists (i.e., agent re-locating within domain)
                            bg_old_location = self.target.get_node(hh_match.location)
                            del bg_old_location.hh_agents[hh_match]  # remove agent from old location
                            self.target.get_node(bg).hh_agents[hh_match] = self.target.get_institution('all_hh_agents')._component_map[hh_match]  # add agent to new block group node
                            del bg_demand[bg][hh_match]  # delete matched agent from hh/bg matching dict
                            del self.target.relocating_hhs[hh_match]  # delete matched agent from unassigned hh dict