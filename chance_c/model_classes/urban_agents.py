import math
import random

from pynsim.components.component import Component


class HouseholdAgent(Component):
    """A household agent representing a group of households in the simulation.
    
    This class represents household agents that make residential location
    decisions based on utility preferences, income constraints, and
    environmental factors like flood risk.
    
    Args:
        name: Unique identifier for the household agent.
        location: Current location (block group ID) of the household.
        no_households_per_agent: Number of households represented by this agent.
        household_size: Average household size.
        income: Household income.
        house_budget_mode: Mode for calculating housing budget.
        year_of_residence: Year when the household moved to current location.
        simple_avoidance_perc: Percentage of agents that avoid flood-prone areas.
    """
    
    def __init__(
        self, 
        name: str, 
        location: str = None, 
        no_households_per_agent: int = 10, 
        household_size: float = 2.7, 
        income: float = 50000, 
        house_budget_mode: str = 'rhea', 
        year_of_residence: int = 2018, 
        simple_avoidance_perc: float = 0.10, 
        **kwargs
    ) -> None:
        """Initialize the HouseholdAgent.
        
        Args:
            name: Unique identifier for the household agent.
            location: Current location (block group ID) of the household.
            no_households_per_agent: Number of households represented by this agent.
            household_size: Average household size.
            income: Household income.
            house_budget_mode: Mode for calculating housing budget.
            year_of_residence: Year when the household moved to current location.
            simple_avoidance_perc: Percentage of agents that avoid flood-prone areas.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(HouseholdAgent, self).__init__(name, **kwargs)
        self.location = location
        self.no_households_per_agent = no_households_per_agent
        self.household_size = household_size
        self.income = income
        self.house_budget_mode = house_budget_mode
        self.year_of_residence = year_of_residence
        self.simple_avoidance_perc = simple_avoidance_perc
        self.avoidance = random.random() < simple_avoidance_perc
        self.house_budget = self._calculate_house_budget()

    _properties = {
        'location': None,  # BlockGroup object name where agent resides
        'household_utilities': {},  # Dictionary of calculated utilities for block groups
    }

    def setup(self, timestep: int) -> None:
        """Set up the household agent for a given timestep.
        
        Args:
            timestep: The current timestep for setup operations.
        """
        self.household_utilities = {}  # Reset any previously calculated utilities

    def calc_utility_cobb_douglas(self, bg: str) -> None:
        """Calculate utility of a residence using Cobb-Douglas function.
        
        Assumes simple Cobb-Douglas function with income, distance to CBD, 
        and flood risk as main factors.
        
        Args:
            bg: Name of BlockGroup object to calculate utility for.
        """
        income = self.network.housing_block_group_df[
            (self.network.housing_block_group_df.name == bg)
        ]['average_income_norm'].values[0]
        distance = self.network.housing_block_group_df[
            (self.network.housing_block_group_df.GEOID == bg)
        ]['prox_cbd_norm'].values[0]
        flood = self.network.housing_block_group_df[
            (self.network.housing_block_group_df.GEOID == bg)
        ]['flood_risk_norm'].values[0]
        
        # Temporary coefficients - need to define higher up
        a = 0.4
        b = 0.4
        c = 0.2
        
        cobb_douglas_utility = (income**a) * (distance**b) * (flood**c)
        self.household_utilities[bg] = cobb_douglas_utility

    def calc_utility_anova_simple(self, bg: str) -> None:
        """Calculate utility using ANOVA hedonic regression.
        
        Assumes simple utility function based on ANOVA hedonic regression.
        See Alfred's analysis (e-mail 9/23/2021 for details).
        
        Args:
            bg: Name of BlockGroup object to calculate utility for.
        """
        pass

    def calc_utility_random(self, bg: str) -> None:
        """Calculate random utility for a residence.
        
        Args:
            bg: Name of BlockGroup object to calculate utility for.
        """
        self.household_utilities[bg] = random.uniform(0, 1)  # Temporary random utility

    def _calculate_house_budget(self) -> float:
        """Calculate the housing budget based on income and budget mode.
        
        Returns:
            float: The calculated housing budget amount.
        """
        if self.house_budget_mode == 'rhea':
            # See de Koning and Filatova, 2020 supplemental materials
            return math.exp(4.96 + (0.63 * math.log(self.income)))
        elif self.house_budget_mode == 'perc':
            return self.income / 0.33  # 33% of income for housing
        else:
            return self.income * 0.33  # Default to 33% of income