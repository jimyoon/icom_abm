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

    _properties = {
        'population': 0,  # number of individuals residing in block group
        'added_population': 0,
        'flood_hazard_risk': 0,
        'available_units': 0,
        'occupied_units': 0,
        'pop_density': 0,  # number of individuals residing in block group / land area of block group (excludes water)
    }

    def setup(self, timestep):
        self.pop_density = self.population / self.area

