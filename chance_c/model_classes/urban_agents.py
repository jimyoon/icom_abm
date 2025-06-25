import math
import random

from pynsim.components.component import Component


class HHAgent(Component):
    """Represents a household agent for residential choice decisions.
    
    A household agent represents an aggregation of households with similar
    socioeconomic characteristics that make residential choice decisions by
    calculating utility for available residences in the landscape.
    
    Args:
        name (str): The name identifier for this household agent.
        location (str, optional): The BlockGroup object name where the agent 
            currently resides. Defaults to None.
        no_hhs_per_agent (int, optional): Number of similar households that 
            the agent represents. Defaults to 100.
        hh_size (int, optional): Average number of individuals in the household. 
            Defaults to 4.
        year_of_residence (int, optional): Year the agent moved to current 
            residence. Defaults to 2018.
        income (float, optional): Average household income. Defaults to None.
        hh_budget_perc (float, optional): Percentage of income for housing 
            budget. Defaults to 0.33.
        house_budget_mode (str, optional): Method for calculating housing budget. 
            Options: 'rhea' or 'perc'. Defaults to 'rhea'.
        simple_avoidance_perc (float, optional): Percentage chance of avoiding 
            flood zones. Defaults to 0.10.
        **kwargs: Additional keyword arguments passed to the parent class.
    
    Attributes:
        name (str): The name identifier for this household agent.
        location (str): The BlockGroup object name where the agent currently 
            resides.
        no_hhs_per_agent (int): Number of similar households that the agent 
            represents.
        hh_size (int): Average number of individuals in the household.
        year_of_residence (int): Year the agent moved to current residence.
        income (float): Average household income.
        average_age (float): Average resident age.
        hh_budget_perc (float): Percentage of income for housing budget.
        avoidance (bool): Whether the agent avoids flood zones.
        house_budget (float): Calculated housing budget amount.
    """
    
    def __init__(self, name: str, location: str = None, no_hhs_per_agent: int = 100, 
                 hh_size: int = 4, year_of_residence: int = 2018, income: float = None,
                 hh_budget_perc: float = 0.33, house_budget_mode: str = 'rhea', 
                 simple_avoidance_perc: float = 0.10, **kwargs) -> None:
        """Initialize the HHAgent.
        
        Args:
            name: The name identifier for this household agent.
            location: The BlockGroup object name where the agent currently 
                resides.
            no_hhs_per_agent: Number of similar households that the agent 
                represents.
            hh_size: Average number of individuals in the household.
            year_of_residence: Year the agent moved to current residence.
            income: Average household income.
            hh_budget_perc: Percentage of income for housing budget.
            house_budget_mode: Method for calculating housing budget.
            simple_avoidance_perc: Percentage chance of avoiding flood zones.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(HHAgent, self).__init__(name, **kwargs)
        self.name = name
        self.location = location
        self.no_hhs_per_agent = no_hhs_per_agent
        self.hh_size = hh_size
        self.year_of_residence = year_of_residence
        self.income = income
        self.average_age = 0
        self.hh_budget_perc = hh_budget_perc

        # Determine if agent avoids flood zones
        random_avoidance = random.uniform(0, 1)
        self.avoidance = random_avoidance <= simple_avoidance_perc

        # Calculate housing budget
        if house_budget_mode == 'rhea':
            # See de Koning and Filatova, 2020 supplemental materials
            self.house_budget = math.exp(4.96 + (0.63 * math.log(self.income)))
        elif house_budget_mode == 'perc':
            self.house_budget = self.income / self.hh_budget_perc

    _properties = {
        'location': None,  # BlockGroup object name where agent resides
        'hh_utilities': {},  # Dictionary of calculated utilities for block groups
    }

    def setup(self, timestep: int) -> None:
        """Set up the household agent for a given timestep.
        
        Args:
            timestep: The current timestep for setup operations.
        """
        self.hh_utilities = {}  # Reset any previously calculated utilities

    def calc_utility_cobb_douglas(self, bg: str) -> None:
        """Calculate utility of a residence using Cobb-Douglas function.
        
        Assumes simple Cobb-Douglas function with income, distance to CBD, 
        and flood risk as main factors.
        
        Args:
            bg: Name of BlockGroup object to calculate utility for.
        """
        income = self.network.housing_bg_df[
            (self.network.housing_bg_df.name == bg)
        ]['average_income_norm'].values[0]
        distance = self.network.housing_bg_df[
            (self.network.housing_bg_df.GEOID == bg)
        ]['prox_cbd_norm'].values[0]
        flood = self.network.housing_bg_df[
            (self.network.housing_bg_df.GEOID == bg)
        ]['flood_risk_norm'].values[0]
        
        # Temporary coefficients - need to define higher up
        a = 0.4
        b = 0.4
        c = 0.2
        
        cobb_douglas_utility = (income**a) * (distance**b) * (flood**c)
        self.hh_utilities[bg] = cobb_douglas_utility

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
        self.hh_utilities[bg] = random.uniform(0, 1)  # Temporary random utility