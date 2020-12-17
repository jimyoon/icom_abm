from pynsim import Network
from pynsim import Node

class ABMLandscape(Network):
    _properties = {
        'total_population': 0,
    }

    def setup(self, timestep):
        self.total_population = 0
        for bg in self.nodes:
            bg.population = 0
            for name, a in bg.hh_agents.items():
                self.total_population += a.no_hhs_per_agent * a.hh_size
                bg.population += a.no_hhs_per_agent * a.hh_size

class BlockGroup(Node):
    """The BlockGroup node class.

    A block group node is representative of a unit stress/observation location in the groundwater system. For the Jordan
    model, there is one groundwater node per subdistrict, per usage type (agricultural or urban), per layer. The groundwater
    head response at each node is calculated via the GWResponseEngine, which consolidates pumping values at all groundwater
    nodes in the system and calculates system response based upon a response matrix approach. Each node contains a groundwater
    lift value, which also account for in-well drawdown and a bias correction to match starting head conditions in 2009.

    **Properties**:

        |  *pumping* (int) - pumping volume for current time step [m3/s]
        |  *lift* (int) - lift, i.e. distance from pumping water level to ground surface [m]
        |  *head* (int) - lift, i.e. distance from pumping water level to ground surface [m]
        |  *check_dry* (bool) - boolean to check whether aquifer dry (pumping water level < aquifer bottom)

    **Outputs to Other Modules**:

        |  *pumping* (int) - pumping volume for current time step [m3/s]
        |  *lift* (int) - lift, i.e. distance from pumping water level to ground surface [m]
        |  *head* (int) - lift, i.e. distance from pumping water level to ground surface [m]
        |  *check_dry* (bool) - boolean to check whether aquifer dry (pumping water level < aquifer bottom)

    """
    def __init__(self, name, x, y, county, tract, blkgrpce, geometry, area, init_pop, **kwargs):
        super(BlockGroup, self).__init__(name, x, y, **kwargs)
        self.name = name
        self.county = county
        self.tract = tract
        self.blkgrpce = blkgrpce
        self.geometry = geometry
        self.area = area
        self.init_pop = init_pop
        self.population = init_pop
        self.hh_agents = {}
        self.avg_home_price = 0
        # Other potential attributes
        self.distance_to_cbd = 0
        self.flood_hazard_risk = 0
        self.available_units = 0

    _properties = {
        'population': 0,  # number of individuals residing in block group
        'added_population': 0,
        'flood_hazard_risk': 0,
        'available_units': 0,
        'occupied_units': 0,
        'pop_density': 0,  # number of individuals residing in block group / land area of block group (excludes water)
        'zoning': 'allowed',  # determines whether development is allowed or not allowed
        'levee_protection': 0,
        'avg_home_price':0,
    }

    def setup(self, timestep):
        self.pop_density = self.population / self.area

