from pynsim import Network
from pynsim import Node
import logging
import statistics
import geopandas as gpd
import pandas as pd
from math import nan
import numpy as np

class ABMLandscape(Network):
    """The ABMLandscape class.

    An ABM Landscape class to set the environment on which agents make residential choice decisions. The landscape contains
    block groups as cells/nodes, as well as attributes that account for unassigned households waiting in the residential
    location queue and a list of available units

    **Attributes**:

        |  *unassigned_hhs* (list / HHAgent) - list of HHAgent objects that are waiting to be assigned
        |  *available_units* (list / str) - list of available units labeled by block group name

    """
    def __init__(self, name, **kwargs):
        super(ABMLandscape, self).__init__(name, **kwargs)
        self.name = name
        self.unassigned_hhs = {}  # dictionary of unassigned new hh agents keyed on hh name (long dict, do not include as property to save memory)
        self.relocating_hhs = {}  # dictionary of existing hh agents that are relocating keyed on hh name (long dict, do not include as property to save memory)
        self.available_units_list = []  # list of available units (long list, do not include as property to save memory)
        self.avg_hh_income = 0
        self.avg_hh_size = 0

    _properties = {
        'total_population': 0,
        'avg_hh_income': 0,
        'avg_hh_size': 0,
        'housing_bg_df': None,  # Currently stores bg dataframe, note history record will correspond to bg status at the beginning of the time period/year
    }

    def setup(self, timestep):
        logging.info('Starting model year: ' + str(self.current_timestep.year))
        # reset various queues and lists
        self.unassigned_hhs = {}
        self.relocating_hhs = {}
        self.available_units_list = []

        if self.current_timestep_idx == 0:  # For first timestep, load housing_bg_df based upon initial agent population
            # reset population sums
            self.total_population = 0

            # calculate various statistics (landscape level) from hh agents
            incomes_landscape = []
            hh_size_landscape = []

            # update master block group pandas dataframe (JY Add engine so this takes place at end of timestep rather than at beginning of next timestep)
            rows_list = []  # first load dictionary for each row into a list, then create the dataframe from the dictionary (much faster!)
            for bg in self.nodes:
                bg_dict = {}
                bg_dict['name'] = bg.name
                bg_dict['no_hh_agents'] = len(bg.hh_agents)

                # calculate various statistics (block level) from hh agents
                bg.population = 0
                incomes_bg = []
                hh_size_bg = []
                bg.no_of_hhs = len(bg.hh_agents)


                for name, a in bg.hh_agents.items():
                    if np.isfinite(a.hh_size) or a.hh_size == 0:  # accounts for 0 or nan hh_size values
                        self.total_population += a.no_hhs_per_agent * a.hh_size
                    else:  # use mean
                        self.total_population += a.no_hhs_per_agent * self.housing_bg_df.hhsize1990.mean()
                    bg.population += a.no_hhs_per_agent * a.hh_size
                    incomes_bg.append(a.income)
                    incomes_landscape.append(a.income)
                    hh_size_bg.append(a.hh_size)
                    hh_size_landscape.append(a.hh_size)

                bg_dict['population'] = bg.population
                if not incomes_bg:  # i.e. no households reside in block group
                    bg_dict['average_income'] = nan
                    bg.mean_hh_income = nan  # update attribute on block group
                else:
                    bg_dict['average_income'] = statistics.mean(incomes_bg)
                    bg.avg_hh_income = statistics.mean(incomes_bg)  # update attribute on block group
                if not hh_size_bg:
                    bg_dict['avg_hh_size'] = nan
                    bg.avg_hh_size = nan  # update attribute on block group
                else:
                    bg_dict['avg_hh_size'] = statistics.mean(hh_size_bg)
                    bg.avg_hh_size = statistics.mean(hh_size_bg)  # update attribute on block group

                # pop density calc
                bg_dict['pop_density'] = bg.population / bg.area
                bg.pop_density = bg.population / bg.area

                #  occupied units calc
                bg_dict['occupied_units'] = bg.occupied_units

                # available units calc
                bg_dict['available_units'] = bg.available_units

                # supply exceeds demand
                bg_dict['demand_exceeds_supply'] = bg.demand_exceeds_supply

                rows_list.append(bg_dict)

            housing_current_df = pd.DataFrame(rows_list)
            self.avg_hh_income = statistics.mean(incomes_landscape)
            self.avg_hh_size = statistics.mean(hh_size_landscape)

            # calculate normalized statistics for block groups
            housing_current_df['average_income_norm'] = housing_current_df['average_income'] / housing_current_df['average_income'].max()

            # merge with housing_bg_df to retain geometry features
            cols_to_use = self.housing_bg_df.columns.difference(housing_current_df.columns)
            self.housing_bg_df = pd.merge(self.housing_bg_df[cols_to_use], housing_current_df, how='left',left_on='GEOID', right_on='name')

            pass  # added to allow for debugger

class BlockGroup(Node):
    """The BlockGroup node class.

    A block group node is representative of a United States census block group. The block groups provide the spatial
    landscape for the ABM. Each block group contains various physical characteristics that can provide amenities/
    disamenities for urban agents. The block groups also contain building stock, tracking the availability of residences

    **Attributes**:

        |  *hh_agents* (list) - list of HHAgent objects that reside in block group
        |  *distance_to_cbd* (list) - distance to central business district
        |  *geometry* (shapely multipolygon object) - shapely multipolygon object (for spatial calculations)

    **Properties**:

        |  *population* (int) - population residing in the block group
        |  *flood_hazard_risk* (int) - flood hazard risk score for block group
        |  *levee_protection* (str) - "no" or "yes"
        |  *years_since_major_flooding* (int) - years since major flooding
        |  *occupied_units* (int) - number of occupied units
        |  *available_units* (int) - number of available units
        |  *pop_density* (int) - population density
        |  *zoning* (str) - "allowed" or "restricted"
        |  *avg_home_price* (int) - average home price ($)
        |  *avg_hh_income* (int) - average household income of residents ($)

    **Inter-module Outputs/Modifications**:

    """
    def __init__(self, name, x, y, county, tract, blkgrpce, geometry, area, init_pop, perc_fld_area,
                 pop90, mhi90, hhsize90, coastdist, cbddist, hhtrans93, salesprice93, salespricesf93, **kwargs):
        super(BlockGroup, self).__init__(name, x, y, **kwargs)
        # fixed attributes
        self.name = name
        self.county = county
        self.tract = tract
        self.blkgrpce = blkgrpce
        self.geometry = geometry
        self.area = area
        self.land_elevation = 0
        self.init_pop = init_pop # JY init pop is deprecated!
        self.perc_fld_area = perc_fld_area
        self.pop90 = pop90
        self.mhi90 = mhi90
        self.hhsize90 = hhsize90
        self.coastdist = coastdist
        self.cbddist = cbddist
        self.hhtrans93 = hhtrans93
        self.salesprice93 = salesprice93
        self.salespricesf93 = salespricesf93

        # pynsim properties
        self.population = pop90 # JY init_pop and pop90 are duplicate, figure out which to use
        self.hh_agents = {}
        self.avg_home_price = 0
        self.flood_hazard_risk = 0
        self.available_units = 0
        self.demand_exceeds_supply = False
        self.new_units_constructed = 0
        self.occupied_units = 0
        self.new_price = salesprice93


    _properties = {
        'population': 0,  # number of individuals residing in block group
        'flood_hazard_risk': 0,
        'available_units': 0,
        'occupied_units': 0,
        'total_units': 0,
        'pop_density': 0,  # number of individuals residing in block group / land area of block group (excludes water)
        'zoning': 'allowed',  # determines whether development is allowed or not allowed
        'levee_protection': "no",
        'new_price': 0,
        'years_since_major_flooding': None,
        'avg_hh_income': 0,
        'no_of_hhs': 0,
        'demand_exceeds_supply': False,
        'new_units_constructed': 0,
    }

    def setup(self, timestep):
        # Note: block group population statistics are updated in the landscape's setup method
        # calculate various block group level statistics based on hh agent population at beginning of each timestep
        # (note: population is updated in the landscape's setup method)

        self.demand_exceeds_supply = False
        self.pop_density = self.population / self.area


