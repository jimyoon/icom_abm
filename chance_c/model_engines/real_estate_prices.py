from pynsim import Engine
from operator import itemgetter
import logging

class RealEstatePrices(Engine):
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

    def __init__(self, target, estimation_mode='OLS_hedonic', **kwargs):
        super(RealEstatePrices, self).__init__(target, **kwargs)
        self.estimation_mode = estimation_mode

    def run(self):
        """ Run the RealEstatePrices engine.
        """
        if self.estimation_mode == 'OLS_hedonic':
            self.target.update_OLS_hedonic_analysis()
        else:  # Other forms of hedonic regression can go here
            pass