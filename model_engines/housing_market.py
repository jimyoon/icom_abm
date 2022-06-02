from pynsim import Engine
from operator import itemgetter
import logging
import time

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
        logging.info("Running the housing market engine, year " + str(self.target.current_timestep.year))

        HH = self.target.hh_utilities_dict.keys()
        income = [float(i.split("hh", 1)[0]) for i in HH]
        diction = dict(zip(HH, income))
        HH2 = sorted(diction.items(), key = lambda x: x[1], reverse = True)#Sort HH agents from richest to the poorest
        HH3 = [i[0] for i in HH2]

        for hh in HH3:
            hh_utilities_subset = self.target.hh_utilities_dict[hh]
            hh_name = 'hh' + hh.split("hh", 1)[1] #Drop the pre-fix income, and get only the hh name
            sorted_bg_candidates = sorted(((v, k) for k, v in hh_utilities_subset.items()))

            for market_iter in range(self.bg_sample_size):
                try:
                    top_candidate_bg = sorted_bg_candidates[-1-market_iter][1]  # get the bg name for the top candidate
                    if self.target.get_node(top_candidate_bg).available_units >= 1:
                        self.target.get_node(top_candidate_bg).hh_agents[hh_name] = \
                            self.target.get_institution('all_hh_agents')._component_map[
                                hh_name]  # add pynsim household agent to associated block group node
                        self.target.get_node(top_candidate_bg).occupied_units += 1  # adjust occupied units
                        self.target.get_node(top_candidate_bg).available_units -= 1  # adjust available units
                        self.target.get_institution('all_hh_agents')._component_map[
                            hh_name].location = top_candidate_bg  # change location attribute on household agent
                        break
                    else:
                        self.target.get_node(top_candidate_bg).demand_exceeds_supply = True
                        if market_iter < 9:
                            continue
                        else:
                            logging.info(
                                hh_name + ' cannot win the competition and is assumed to migrate outside of domain')
                            self.target.get_institution('all_hh_agents')._component_map[
                                hh_name].location = 'outmigrated'
                except IndexError:  # if list index is out of range, indicates that no available units are affordable for agent
                    logging.info(hh_name + ' cannot afford any properties and is assumed to migrate outside of domain')
                    self.target.get_institution('all_hh_agents')._component_map[hh_name].location = 'outmigrated'
