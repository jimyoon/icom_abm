import statistics
from math import nan

from pynsim import Engine
import numpy as np
import pandas as pd
import polars as pl
from pynsim import Engine
import logging
from chance_c.utils.polars_utils import fast_merge_polars, fast_normalize_polars, fast_statistics_polars


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

        # calculate various statistics (landscape level) from household agents
        incomes_landscape = []
        household_sizes_landscape = []

        # Use Polars for faster data collection
        rows_data = []
        
        for block_group in self.target.nodes:
            # Calculate block group statistics
            block_group.population = 0
            incomes_block_group = []
            household_size_block_group = []
            block_group.no_of_households = len(block_group.household_agents)

            for a in block_group.household_agents.values():
                if hasattr(a, 'household_size') and a.household_size > 0:
                    pop_contribution = a.no_households_per_agent * a.household_size
                else:  # use mean
                    pop_contribution = a.no_households_per_agent * self.target.housing_block_group_df["hhsize1990"].mean()
                
                self.target.total_population += pop_contribution
                block_group.population += pop_contribution
                incomes_block_group.append(a.income)
                incomes_landscape.append(a.income)
                household_size_block_group.append(a.household_size)
                household_sizes_landscape.append(a.household_size)

            # Calculate statistics for this block group
            avg_income = statistics.mean(incomes_block_group) if incomes_block_group else nan
            avg_hh_size = statistics.mean(household_size_block_group) if household_size_block_group else nan
            
            # Update block group attributes
            block_group.avg_hh_income = avg_income
            block_group.avg_hh_size = avg_hh_size
            block_group.pop_density = block_group.population / block_group.area

            # Prepare row data for Polars DataFrame
            row_data = {
                'name': block_group.name,
                'no_hh_agents': len(block_group.household_agents),
                'population': block_group.population,
                'average_income': avg_income,
                'avg_hh_size': avg_hh_size,
                'pop_density': block_group.pop_density,
                'occupied_units': block_group.occupied_units,
                'available_units': block_group.available_units,
                'demand_exceeds_supply': block_group.demand_exceeds_supply
            }
            rows_data.append(row_data)

        # Create Polars DataFrame for current statistics
        housing_current_df = pl.DataFrame(rows_data)
        
        # Calculate landscape-level statistics
        self.target.avg_hh_income = statistics.mean(incomes_landscape)
        self.target.avg_hh_size = statistics.mean(household_sizes_landscape)

        # Calculate normalized statistics using Polars
        max_income = housing_current_df.select(pl.col('average_income').max()).item()
        if max_income != 0 and not np.isnan(max_income):
            housing_current_df = housing_current_df.with_columns(
                (pl.col('average_income') / max_income).alias('average_income_norm')
            )
        else:
            housing_current_df = housing_current_df.with_columns(
                pl.lit(0.0).alias('average_income_norm')
            )

        # Drop all columns except those with dtype number, bool, datetime, or string
        df = self.target.housing_block_group_df
        allowed_kinds = {'i', 'u', 'f', 'b', 'M'}  # int, uint, float, bool, datetime64
        keep_cols = [col for col in df.columns if df[col].dtype.kind in allowed_kinds or pd.api.types.is_string_dtype(df[col])]
        existing_df = pl.from_pandas(df[keep_cols])
        
        # Fast merge using Polars
        merged_df = fast_merge_polars(
            left_df=existing_df,
            right_df=housing_current_df,
            left_on='GEOID',
            right_on='name',
            how='left'
        )
        
        # Convert back to pandas for compatibility
        self.target.housing_block_group_df = merged_df.to_pandas()
