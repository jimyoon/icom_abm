import logging
from math import nan
import statistics

import geopandas as gpd
import pandas as pd
import numpy as np
from pynsim import Network
from pynsim import Node


class ABMLandscape(Network):
    """Agent-based model landscape for residential choice decisions.
    
    An ABM Landscape class that sets the environment on which agents make 
    residential choice decisions. The landscape contains block groups as 
    cells/nodes, as well as attributes that account for unassigned households 
    waiting in the residential location queue and a list of available units.
    
    Attributes:
        unassigned_households: Dictionary of unassigned new household agents keyed 
            on household name.
        relocating_households: Dictionary of existing household agents that are 
            relocating keyed on household name.
        available_units_list: List of available units.
        avg_hh_income: Average household income across the landscape.
        avg_hh_size: Average household size across the landscape.
        total_population: Total population across all block groups.
        housing_block_group_df: DataFrame containing block group housing data.
    """
    
    def __init__(
            self, 
            name: str, 
            avg_hh_income: float = 0,
            avg_hh_size: float = 0,
            total_population: int = 0,
            housing_block_group_df: pd.DataFrame = None,
            **kwargs
    ) -> None:
        """Initialize the ABMLandscape.
        
        Args:
            name: The name identifier for this landscape.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(ABMLandscape, self).__init__(name, **kwargs)
        self.name = name
        self.unassigned_households = {}  # dictionary of unassigned new household agents keyed on household name (long dict, do not include as property to save memory)
        self.relocating_households = {}  # dictionary of existing household agents that are relocating keyed on household name (long dict, do not include as property to save memory)
        self.available_units_list = []  # list of available units (long list, do not include as property to save memory)
        self.avg_hh_income = avg_hh_income
        self.avg_hh_size = avg_hh_size
        self.total_population = total_population
        self.housing_block_group_df = housing_block_group_df

    _properties = {
        'total_population': 0,
        'avg_hh_income': 0,
        'avg_hh_size': 0,
        'housing_block_group_df': None,  # Currently stores block_group dataframe, note history record will correspond to block_group status at the beginning of the time period/year
    }

    def setup(self, timestep: int) -> None:
        """Set up the landscape for a given timestep.
        
        Resets various queues and lists, and for the first timestep, loads 
        housing_block_group_df based upon initial agent population.
        
        Args:
            timestep: The current timestep for setup operations.
        """
        logging.info('Starting model year: ' + str(self.current_timestep.year))
        # reset various queues and lists
        self.unassigned_households = {}
        self.relocating_households = {}
        self.available_units_list = []

        if self.current_timestep_idx == 0:  # For first timestep, load housing_block_group_df based upon initial agent population
            # reset population sums
            self.total_population = 0

            # calculate various statistics (landscape level) from household agents
            incomes_landscape = []
            household_sizes_landscape = []

            # update master block group pandas dataframe (JY Add engine so this takes place at end of timestep rather than at beginning of next timestep)
            rows_list = []  # first load dictionary for each row into a list, then create the dataframe from the dictionary (much faster!)
            for block_group in self.nodes:
                block_group_dict = {}
                block_group_dict['name'] = block_group.name
                block_group_dict['no_hh_agents'] = len(block_group.household_agents)

                # calculate various statistics (block level) from household agents
                block_group.population = 0
                incomes_block_group = []
                household_size_block_group = []
                block_group.no_of_households = len(block_group.household_agents)

                for a in block_group.household_agents.values():
                    if hasattr(a, 'household_size') and a.household_size > 0:
                        self.total_population += a.no_households_per_agent * a.household_size
                    else:  # use mean
                        self.total_population += a.no_households_per_agent * self.housing_block_group_df["hhsize1990"].mean()
                    block_group.population += a.no_households_per_agent * a.household_size
                    incomes_block_group.append(a.income)
                    incomes_landscape.append(a.income)
                    household_size_block_group.append(a.household_size)
                    household_sizes_landscape.append(a.household_size)

                block_group_dict['population'] = block_group.population
                if not incomes_block_group:  # i.e. no households reside in block group
                    block_group_dict['average_income'] = nan
                    block_group.mean_hh_income = nan  # update attribute on block group
                else:
                    block_group_dict['average_income'] = statistics.mean(incomes_block_group)
                    block_group.avg_hh_income = statistics.mean(incomes_block_group)  # update attribute on block group
                if not household_size_block_group:
                    block_group_dict['avg_hh_size'] = nan
                    block_group.avg_hh_size = nan  # update attribute on block group
                else:
                    block_group_dict['avg_hh_size'] = statistics.mean(household_size_block_group)
                    block_group.avg_hh_size = statistics.mean(household_size_block_group)  # update attribute on block group

                # pop density calc
                block_group_dict['pop_density'] = block_group.population / block_group.area
                block_group.pop_density = block_group.population / block_group.area

                #  occupied units calc
                block_group_dict['occupied_units'] = block_group.occupied_units

                # available units calc
                block_group_dict['available_units'] = block_group.available_units

                # supply exceeds demand
                block_group_dict['demand_exceeds_supply'] = block_group.demand_exceeds_supply

                rows_list.append(block_group_dict)

            housing_current_df = pd.DataFrame(rows_list)
            self.avg_hh_income = statistics.mean(incomes_landscape)
            self.avg_hh_size = statistics.mean(household_sizes_landscape)

            # calculate normalized statistics for block groups
            housing_current_df['average_income_norm'] = housing_current_df['average_income'] / housing_current_df['average_income'].max()

            # merge with housing_block_group_df to retain geometry features
            cols_to_use = self.housing_block_group_df.columns.difference(housing_current_df.columns)
            self.housing_block_group_df = pd.merge(self.housing_block_group_df[cols_to_use], housing_current_df, how='left',left_on='GEOID', right_on='name')

            pass  # added to allow for debugger


class BlockGroup(Node):
    """Represents a United States census block group node.
    
    A block group node provides the spatial landscape for the ABM. Each block 
    group contains various physical characteristics that can provide amenities/
    disamenities for urban agents. The block groups also contain building stock, 
    tracking the availability of residences.
    
    Args:
        name (str): The name identifier for this block group.
        x (float): X coordinate of the block group centroid.
        y (float): Y coordinate of the block group centroid.
        county (str): County identifier.
        tract (str): Census tract identifier.
        blkgrpce (str): Block group identifier.
        geometry: Shapely multipolygon object for spatial calculations.
        area (float): Land area of the block group (excludes water).
        init_pop (int): Initial population (deprecated).
        perc_fld_area (float): Percentage of area in flood zone.
        pop90 (int): Population in 1990.
        mhi90 (float): Median household income in 1990.
        household_size90 (float): Average household size in 1990.
        coastdist (float): Distance to coast.
        cbddist (float): Distance to central business district.
        hhtrans93 (float): Household transportation data from 1993.
        salesprice93 (float): Sales price in 1993.
        salespricesf93 (float): Sales price per square foot in 1993.
        **kwargs: Additional keyword arguments passed to the parent class.
    
    Attributes:
        hh_agents (dict): Dictionary of HHAgent objects that reside in block group.
        distance_to_cbd (list): Distance to central business district.
        geometry: Shapely multipolygon object for spatial calculations.
        population (int): Population residing in the block group.
        flood_hazard_risk (int): Flood hazard risk score for block group.
        levee_protection (str): "no" or "yes".
        years_since_major_flooding (int): Years since major flooding.
        occupied_units (int): Number of occupied units.
        available_units (int): Number of available units.
        pop_density (float): Population density.
        zoning (str): "allowed" or "restricted".
        avg_home_price (float): Average home price ($).
        avg_hh_income (float): Average household income of residents ($).
    """
    
    def __init__(
            self, 
            name: str, 
            x: float, 
            y: float, 
            county: str, 
            tract: str, 
            blkgrpce: str, 
            geometry, 
            area: float, 
            init_pop: int, 
            perc_fld_area: float, 
            pop90: int, 
            mhi90: float, 
            household_size90: float, 
            coastdist: float, 
            cbddist: float, 
            hhtrans93: float, 
            salesprice93: float, 
            salespricesf93: float, 
            **kwargs
    ) -> None:
        """Initialize the BlockGroup node.
        
        Args:
            name: The name identifier for this block group.
            x: X coordinate of the block group centroid.
            y: Y coordinate of the block group centroid.
            county: County identifier.
            tract: Census tract identifier.
            blkgrpce: Block group identifier.
            geometry: Shapely multipolygon object for spatial calculations.
            area: Land area of the block group (excludes water).
            init_pop: Initial population (deprecated).
            perc_fld_area: Percentage of area in flood zone.
            pop90: Population in 1990.
            mhi90: Median household income in 1990.
            hhsize90: Average household size in 1990.
            coastdist: Distance to coast.
            cbddist: Distance to central business district.
            hhtrans93: Household transportation data from 1993.
            salesprice93: Sales price in 1993.
            salespricesf93: Sales price per square foot in 1993.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(BlockGroup, self).__init__(name, x, y, **kwargs)
        
        # fixed attributes
        self.name = name
        self.county = county
        self.tract = tract
        self.blkgrpce = blkgrpce
        self.geometry = geometry
        self.area = area
        self.land_elevation = 0
        self.init_pop = init_pop  # JY init pop is deprecated!
        self.perc_fld_area = perc_fld_area
        self.pop90 = pop90
        self.mhi90 = mhi90
        self.household_size90 = household_size90
        self.coastdist = coastdist
        self.cbddist = cbddist
        self.hhtrans93 = hhtrans93
        self.salesprice93 = salesprice93
        self.salespricesf93 = salespricesf93

        # pynsim properties
        self.population = pop90  # JY init_pop and pop90 are duplicate, figure out which to use
        self.household_agents = {}
        self.avg_home_price = 0
        self.flood_hazard_risk = 0
        self.available_units = 0
        self.demand_exceeds_supply = False
        self.new_units_constructed = 0
        self.occupied_units = 0
        self.new_price = salesprice93

    _properties = {
        'population': 0,  # number of individuals residing in block group
        'flood_hazard_risk': 0,
        'available_units': 0,
        'occupied_units': 0,
        'total_units': 0,
        'pop_density': 0,  # number of individuals residing in block group / land area of block group (excludes water)
        'zoning': 'allowed',  # determines whether development is allowed or not allowed
        'levee_protection': "no",
        'new_price': 0,
        'years_since_major_flooding': None,
        'avg_hh_income': 0,
        'no_of_households': 0,
        'demand_exceeds_supply': False,
        'new_units_constructed': 0,
    }

    def setup(self, timestep: int) -> None:
        """Set up the block group for a given timestep.
        
        Note: Block group population statistics are updated in the landscape's 
        setup method. This method calculates various block group level statistics 
        based on household agent population at beginning of each timestep.
        
        Args:
            timestep: The current timestep for setup operations.
        """
        # Note: block group population statistics are updated in the landscape's setup method
        # calculate various block group level statistics based on hh agent population at beginning of each timestep
        # (note: population is updated in the landscape's setup method)

        self.demand_exceeds_supply = False
        self.pop_density = self.population / self.area
