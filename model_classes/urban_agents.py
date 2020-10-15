from pynsim.components.component import Component

class HHAgent(Component):
    def __init__(self, name, location=None, no_hhs_per_agent=100, hh_size=4, year_of_residence=2018, **kwargs):
        super(HHAgent, self).__init__(name, **kwargs)
        self.name = name
        self.location = location
        self.no_hhs_per_agent = no_hhs_per_agent
        self.hh_size = hh_size
        self.year_of_residence = year_of_residence

    _properties = {
        'location': 0,  # number of individuals residing in block group
    }

    def calc_cobb_douglas_utility(self):
        pass