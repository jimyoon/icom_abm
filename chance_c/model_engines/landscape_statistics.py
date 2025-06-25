import statistics
from math import nan

from pynsim import Engine
import numpy as np
import pandas as pd


class LandscapeStatistics(Engine):
    """An engine class that calculates and updates landscape-level and block group-level statistics.
    
    The LandscapeStatistics class is a pynsim engine that computes various demographic
    and housing statistics from household agents. It calculates population, income,
    household size, population density, and housing inventory statistics at both
    the landscape and block group levels, then updates the housing dataframe with
    current values.
    
    Args:
        target: The simulation network target containing block group nodes and household data.
        **kwargs: Additional keyword arguments passed to the parent class.
    
    Inter-module Outputs/Modifications:
        target.total_population (int): Total population across all block groups.
        target.avg_hh_income (float): Average household income across the landscape.
        target.avg_hh_size (float): Average household size across the landscape.
        target.housing_bg_df (pandas.DataFrame): Updated housing dataframe with 
            current statistics for each block group.
        bg.population (int): Population count for each block group node.
        bg.avg_hh_income (float): Average household income for each block group node.
        bg.avg_hh_size (float): Average household size for each block group node.
        bg.pop_density (float): Population density for each block group node.
    """
    
    def __init__(self, target, **kwargs) -> None:
        """Initialize the LandscapeStatistics engine.
        
        Args:
            target: The simulation network target containing block group nodes and household data.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(LandscapeStatistics, self).__init__(target, **kwargs)

    def run(self) -> None:
        """Execute the landscape statistics calculation process.
        
        Calculates population, income, household size, and housing inventory
        statistics from household agents. Updates both block group node attributes
        and the housing dataframe with current values. Handles edge cases such as
        empty block groups and invalid household size values.
        """
        # reset population sums
        self.target.total_population = 0

        # calculate various statistics (landscape level) from hh agents
        incomes_landscape = []
        hh_size_landscape = []

        # self.target.housing_bg_df['population'] = 0
        # update master block group pandas dataframe
        rows_list = []  # first load dictionary for each row into a list, then create the dataframe from the dictionary (much faster!)
        for bg in self.target.nodes:
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
                    self.target.total_population += a.no_hhs_per_agent * a.hh_size
                else:  # use mean
                    self.target.total_population += a.no_hhs_per_agent * self.target.housing_bg_df.hhsize1990.mean()
                bg.population += a.no_hhs_per_agent * a.hh_size
                incomes_bg.append(a.income)
                incomes_landscape.append(a.income)
                hh_size_bg.append(a.hh_size)
                hh_size_landscape.append(a.hh_size)

            bg_dict['population'] = bg.population
            # self.target.housing_bg_df.loc[self.target.housing_bg_df['GEOID'] == bg.name, 'population'] = bg.population
            if not incomes_bg:  # i.e. no households reside in block group
                bg_dict['average_income'] = nan
                # self.target.housing_bg_df.loc[
                #     self.target.housing_bg_df['GEOID'] == bg.name, 'average_income'] = nan
                bg.mean_hh_income = nan  # update attribute on block group
            else:
                bg_dict['average_income'] = statistics.mean(incomes_bg)
                # self.target.housing_bg_df.loc[
                #     self.target.housing_bg_df['GEOID'] == bg.name, 'average_income'] = statistics.mean(incomes_bg)
                bg.avg_hh_income = statistics.mean(incomes_bg)  # update attribute on block group
            if not hh_size_bg:
                bg_dict['avg_hh_size'] = nan
                # self.target.housing_bg_df.loc[
                #     self.target.housing_bg_df['GEOID'] == bg.name, 'avg_hh_size'] = nan
                bg.avg_hh_size = nan  # update attribute on block group
            else:
                bg_dict['avg_hh_size'] = statistics.mean(hh_size_bg)
                # self.target.housing_bg_df.loc[
                #     self.target.housing_bg_df['GEOID'] == bg.name, 'avg_hh_size'] = statistics.mean(hh_size_bg)
                bg.avg_hh_size = statistics.mean(hh_size_bg)  # update attribute on block group

            # pop density calc
            bg_dict['pop_density'] = bg.population / bg.area
            # self.target.housing_bg_df.loc[
            #     self.target.housing_bg_df['GEOID'] == bg.name, 'pop_density'] = bg.population / bg.area
            bg.pop_density = bg.population / bg.area

            #  occupied units calc
            bg_dict['occupied_units'] = bg.occupied_units
            # self.target.housing_bg_df.loc[
            #     self.target.housing_bg_df['GEOID'] == bg.name, 'occupied_units'] = bg.occupied_units

            # available units calc
            bg_dict['available_units'] = bg.available_units
            # self.target.housing_bg_df.loc[
            #     self.target.housing_bg_df['GEOID'] == bg.name, 'available_units'] = bg.available_units

            # supply exceeds demand
            bg_dict['demand_exceeds_supply'] = bg.demand_exceeds_supply
            # self.target.housing_bg_df.loc[
            #     self.target.housing_bg_df['GEOID'] == bg.name, 'demand_exceeds_supply'] = bg.demand_exceeds_supply

            rows_list.append(bg_dict)

        housing_current_df = pd.DataFrame(rows_list)
        self.target.avg_hh_income = statistics.mean(incomes_landscape)
        self.target.avg_hh_size = statistics.mean(hh_size_landscape)

        # calculate normalized statistics for block groups
        housing_current_df['average_income_norm'] = housing_current_df['average_income'] / housing_current_df['average_income'].max()

        # merge with housing_bg_df to retain geometry features
        cols_to_use = self.target.housing_bg_df.columns.difference(housing_current_df.columns)
        self.target.housing_bg_df = pd.merge(self.target.housing_bg_df[cols_to_use], housing_current_df, how='left',left_on='GEOID', right_on='name')
