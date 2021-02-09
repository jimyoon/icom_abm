from pynsim import Network
from pynsim import Node
import logging

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

    _properties = {
        'total_population': 0,
    }

    def setup(self, timestep):
        logging.info('Starting model year: ' + str(self.current_timestep.year))
        # reset various queues and lists
        self.unassigned_hhs = {}
        self.relocating_hhs = {}
        self.available_units_list = []
        # calculate total population based on bg status
        self.total_population = 0
        for bg in self.nodes:
            bg.population = 0
            for name, a in bg.hh_agents.items():
                self.total_population += a.no_hhs_per_agent * a.hh_size
                bg.population += a.no_hhs_per_agent * a.hh_size

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
    def __init__(self, name, x, y, county, tract, blkgrpce, geometry, area, init_pop, perc_fld_area, **kwargs):
        super(BlockGroup, self).__init__(name, x, y, **kwargs)
        # fixed attributes
        self.name = name
        self.county = county
        self.tract = tract
        self.blkgrpce = blkgrpce
        self.geometry = geometry
        self.area = area
        self.land_elevation = 0
        self.init_pop = init_pop
        self.perc_fld_area = perc_fld_area

        # pynsim properties
        self.population = init_pop
        self.hh_agents = {}
        self.avg_home_price = 0
        self.distance_to_cbd = 0
        self.flood_hazard_risk = 0
        self.available_units = 0


    _properties = {
        'population': 0,  # number of individuals residing in block group
        'flood_hazard_risk': 0,
        'available_units': 0,
        'occupied_units': 0,
        'total_units': 0,
        'pop_density': 0,  # number of individuals residing in block group / land area of block group (excludes water)
        'zoning': 'allowed',  # determines whether development is allowed or not allowed
        'levee_protection': "no",
        'avg_home_price': 0,
        'years_since_major_flooding': None,
        'median_hh_income': 0,
    }

    def setup(self, timestep):
        # calculate various block group level statistics based on hh agent population at beginning of each timestep
        # (note: population is updated at the landscape level)

        self.pop_density = self.population / self.area

