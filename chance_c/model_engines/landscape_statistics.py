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
        target.housing_block_group_df (pandas.DataFrame): Updated housing dataframe with
            new statistics.
        block_group.population (int): Population count for each block group node.
        block_group.avg_hh_income (float): Average household income for each block group node.
        block_group.avg_hh_size (float): Average household size for each block group node.
        block_group.pop_density (float): Population density for each block group node.
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
        for block_group in self.target.nodes:
            block_group_dict = {}
            block_group_dict['name'] = block_group.name
            block_group_dict['no_hh_agents'] = len(block_group.hh_agents)

            # calculate various statistics (block level) from hh agents
            block_group.population = 0
            incomes_block_group = []
            hh_size_block_group = []
            block_group.no_of_hhs = len(block_group.hh_agents)

            for name, a in block_group.hh_agents.items():
                if np.isfinite(a.hh_size) or a.hh_size == 0:  # accounts for 0 or nan hh_size values
                    self.target.total_population += a.no_hhs_per_agent * a.hh_size
                else:  # use mean
                    self.target.total_population += a.no_hhs_per_agent * self.target.housing_block_group_df.hhsize1990.mean()
                block_group.population += a.no_hhs_per_agent * a.hh_size
                incomes_block_group.append(a.income)
                incomes_landscape.append(a.income)
                hh_size_block_group.append(a.hh_size)
                hh_size_landscape.append(a.hh_size)

            block_group_dict['population'] = block_group.population
            # self.target.housing_bg_df.loc[self.target.housing_bg_df['GEOID'] == block_group.name, 'population'] = block_group.population
            if not incomes_block_group:  # i.e. no households reside in block group
                block_group_dict['average_income'] = nan
                # self.target.housing_bg_df.loc[
                #     self.target.housing_bg_df['GEOID'] == block_group.name, 'average_income'] = nan
                block_group.mean_hh_income = nan  # update attribute on block group
            else:
                block_group_dict['average_income'] = statistics.mean(incomes_block_group)
                # self.target.housing_bg_df.loc[
                #     self.target.housing_bg_df['GEOID'] == block_group.name, 'average_income'] = statistics.mean(incomes_bg)
                block_group.avg_hh_income = statistics.mean(incomes_block_group)  # update attribute on block group
            if not hh_size_block_group:
                block_group_dict['avg_hh_size'] = nan
                # self.target.housing_bg_df.loc[
                #     self.target.housing_bg_df['GEOID'] == block_group.name, 'avg_hh_size'] = nan
                block_group.avg_hh_size = nan  # update attribute on block group
            else:
                block_group_dict['avg_hh_size'] = statistics.mean(hh_size_block_group)
                # self.target.housing_bg_df.loc[
                #     self.target.housing_bg_df['GEOID'] == block_group.name, 'avg_hh_size'] = statistics.mean(hh_size_block_group)
                block_group.avg_hh_size = statistics.mean(hh_size_block_group)  # update attribute on block group

            # pop density calc
            block_group_dict['pop_density'] = block_group.population / block_group.area
            # self.target.housing_bg_df.loc[
            #     self.target.housing_bg_df['GEOID'] == block_group.name, 'pop_density'] = block_group.population / block_group.area
            block_group.pop_density = block_group.population / block_group.area

            #  occupied units calc
            block_group_dict['occupied_units'] = block_group.occupied_units
            # self.target.housing_bg_df.loc[
            #     self.target.housing_bg_df['GEOID'] == block_group.name, 'occupied_units'] = block_group.occupied_units

            # available units calc
            block_group_dict['available_units'] = block_group.available_units
            # self.target.housing_bg_df.loc[
            #     self.target.housing_bg_df['GEOID'] == block_group.name, 'available_units'] = block_group.available_units

            # supply exceeds demand
            block_group_dict['demand_exceeds_supply'] = block_group.demand_exceeds_supply
            # self.target.housing_bg_df.loc[
            #     self.target.housing_bg_df['GEOID'] == block_group.name, 'demand_exceeds_supply'] = block_group.demand_exceeds_supply

            rows_list.append(block_group_dict)

        housing_current_df = pd.DataFrame(rows_list)
        self.target.avg_hh_income = statistics.mean(incomes_landscape)
        self.target.avg_hh_size = statistics.mean(hh_size_landscape)

        # calculate normalized statistics for block groups
        housing_current_df['average_income_norm'] = housing_current_df['average_income'] / housing_current_df['average_income'].max()

        # merge with housing_bg_df to retain geometry features
        cols_to_use = self.target.housing_block_group_df.columns.difference(housing_current_df.columns)
        self.target.housing_block_group_df = pd.merge(self.target.housing_block_group_df[cols_to_use], housing_current_df, how='left',left_on='GEOID', right_on='name')
