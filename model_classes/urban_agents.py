from pynsim.components.component import Component
import random
import math

class HHAgent(Component):
    """The HHAgent component class.

    A HHAgent is representative of a household agent. Household agents represent an aggregation of households of similar
    socioeconomic characteristics and make residential choice decisions by calculating their utility for available
    residences in the landscape.

    **Attributes**:

        |  *no_hhs_per_agent* (int) - the number of similar households that the agent represents
        |  *hh_size* (int) - average number of individuals in the household
        |  *income* (float) - average household income
        |  *age* (float) - average resident age


    **Properties**:

        |  *year_of_residence* (int) - the year in which the agent moved to the current residence
        |  *location* (str) - the BlockGroup object name in which the agent currently resides
        |  *hh_utilities* (dict {str:float}) - a dictionary of calculated utilities for a sample of block groups (keys are block group names; values are utilities)


    **Inter-module Outputs/Modifications**:
    """

    def __init__(self, name, location=None, no_hhs_per_agent=100, hh_size=4, year_of_residence=2018, income=None,
                 hh_budget_perc=0.33, house_budget_mode='rhea', simple_avoidance_perc=.10, **kwargs):
        super(HHAgent, self).__init__(name, **kwargs)
        self.name = name
        self.location = location
        self.no_hhs_per_agent = no_hhs_per_agent
        self.hh_size = hh_size
        self.year_of_residence = year_of_residence
        ### Other potential attributes
        self.income = income
        self.average_age = 0
        self.hh_budget_perc = hh_budget_perc

        random_avoidance = random.uniform(0, 1)   # indicates whether agent avoids flood zone (used in "simple avoidance utility" model)
        if random_avoidance <= simple_avoidance_perc:
            self.avoidance = True
        else:
            self.avoidance = False

        # calculate housing budget
        if house_budget_mode == 'rhea':
            self.house_budget = math.exp(4.96 + (0.63 * math.log(self.income))) # See de Koning and Filatova, 2020 supplemental materials
        elif house_budget_mode == 'perc':
            self.house_budget = self.income / self.hh_budget_perc

    _properties = {
        'location': None,  # number of individuals residing in block group
        'hh_utilities': {},
    }

    def setup(self, timestep):
        """Setup for a household agent
        """
        self.hh_utilities = {}  # reset any previously calculated utilities

    def calc_utility_cobb_douglas(self, bg):
        """Calculates utility of a residence for a household agent. Assumes simple cobb-douglas function with
        income, distance to CBD, and flood risk as main factors

        **Args**:
        bg (str): name of BlockGroup object

        **Inter-module Outputs/Modifications**:
        self.hh_utilities
        """
        income = self.network.housing_bg_df[(self.network.housing_bg_df.name == bg)]['average_income_norm'].values[0]
        distance = self.network.housing_bg_df[(self.network.housing_bg_df.GEOID == bg)]['prox_cbd_norm'].values[0]
        flood = self.network.housing_bg_df[(self.network.housing_bg_df.GEOID == bg)]['flood_risk_norm'].values[0]
        a = 0.4  # temporary, need to define higher up
        b = 0.4
        c = 0.2
        cobb_douglas_utility = (income**a) * (distance**b) * (flood**c)
        self.hh_utilities[bg] = cobb_douglas_utility

    def calc_utility_anova_simple(self, bg):
        """Calculates utility of a residence for a household agent. Assumes simple utility function based on ANOVA hedonic
        regression. See Alfred's analysis (e-mail 9/23/2021 for details).

        **Args**:
        bg (str): name of BlockGroup object

        **Inter-module Outputs/Modifications**:
        self.hh_utilities
        """

    def calc_utility_random(self, bg):
        """Calculates utility of a residence for a household agent.

        **Args**:
        bg (str): name of BlockGroup object

        **Inter-module Outputs/Modifications**:
        self.hh_utilities
        """
        self.hh_utilities[bg] = random.uniform(0, 1)  # temporarily calculate random utility value