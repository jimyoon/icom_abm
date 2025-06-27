import datetime
import logging

import geopandas as gpd
import pandas as pd
import numpy as np
from pynsim import Simulator

from .landscape import ABMLandscape, BlockGroup
from .urban_agents import HouseholdAgent


class ICOMSimulator(Simulator):
    """An ICOM Simulator class for agent-based modeling simulations.
    
    This class extends the pynsim Simulator to provide specialized functionality
    for Integrated Coastal and Ocean Modeling (ICOM) simulations. It manages
    landscape setup, agent creation, and simulation parameters.
    
    Args:
        network: The network object for the simulation.
        record_time (bool): Whether to record simulation time.
        progress (bool): Whether to show progress indicators.
        max_iterations (int): Maximum number of iterations for the simulation.
        name (str): Name identifier for the simulator.
        scenario (str): Scenario identifier for the simulation.
        intervention (str): Intervention type for the simulation.
        start_year (int): Starting year for the simulation.
        n_years (int): Number of years to simulate.
    """
    
    def __init__(
            self, 
            network, 
            record_time: bool = False, 
            progress: bool = False, 
            max_iterations: int = 100, 
            name: str = 'chance-c', 
            scenario: str = 'default', 
            intervention: str = 'default', 
            start_year: int = 1990, 
            n_years: int = 1
    ) -> None:
        """Initialize the ICOM Simulator.
        
        Args:
            network: The network object for the simulation.
            record_time: Whether to record simulation time.
            progress: Whether to show progress indicators.
            max_iterations: Maximum number of iterations for the simulation.
            name: Name identifier for the simulator.
            scenario: Scenario identifier for the simulation.
            intervention: Intervention type for the simulation.
            start_year: Starting year for the simulation.
            n_years: Number of years to simulate.
        """
        super(ICOMSimulator, self).__init__(network, record_time, progress, max_iterations)
        # set simulator characteristics
        self.name = name
        self.scenario = scenario
        self.intervention = intervention

        # set timestep information
        self.start_year = start_year
        self.n_years = n_years

    def set_timestep_information(self) -> None:
        """Set up timestep information for the simulation.
        
        Creates a list of datetime objects representing each year in the
        simulation period, starting from the specified start year.
        """
        logging.info("Setting up timestep information")
        timesteps = [datetime.datetime.strptime(str(self.start_year), '%Y')]
        for y in range(self.n_years):
            new_year = timesteps[-1].year + 1
            timesteps.append(datetime.datetime.strptime(str(new_year), '%Y'))
        self.set_timesteps(timesteps)
        logging.info("The first timestep is " + str(self.timesteps[0]))
        logging.info("The last timestep is " + str(self.timesteps[-1]))

    def set_landscape(
            self, 
            landscape_name: str, 
            geo_filename: str, 
            pop_filename: str, 
            pop_fieldname: str, 
            flood_filename: str, 
            housing_filename: str, 
            hedonic_filename: str,
            field_mappings: dict = None,
            **kwargs
    ) -> None:
        """Create landscape based on census geographies and data.
        
        Assumes data structure follows IPUMS/NHGIS format. Loads and processes
        geographic, population, flood, housing, and hedonic data to create
        block group nodes for the simulation landscape.
        
        Args:
            landscape_name: Name identifier for the landscape.
            geo_filename: Path to geographic boundary file.
            pop_filename: Path to population data file.
            pop_fieldname: Field name containing population data.
            flood_filename: Path to flood data file.
            housing_filename: Path to housing data file.
            hedonic_filename: Path to hedonic regression data file.
            field_mappings: Optional dictionary containing field mappings.
        """
        logging.info("Setting up model landscape")
        landscape = ABMLandscape(name=landscape_name)

        # Import FieldMapper here to avoid circular imports
        try:
            from ..field_mapper import FieldMapper
        except ImportError:
            FieldMapper = None
            
        # Initialize field mapper if mappings are provided
        mapper = FieldMapper(mappings=field_mappings) if field_mappings and FieldMapper else None

        # Load geographic data
        block_group = gpd.read_file(geo_filename)
        
        # Apply field mapping for geo file if mapper is available
        if mapper:
            block_group = mapper.map_dataframe(block_group, 'geo')
        
        # Enforce specific data types for geo_file columns
        geo_dtype_specs = {
            'GISJOIN': 'object',
            'GEOID': 'object', 
            'COUNTYFP': 'object',
            'TRACTCE': 'object',
            'BLKGRPCE': 'object',
            'ALAND': 'float64'
            # geometry column is already handled by geopandas
        }
        
        # Apply data type conversions
        for col, dtype in geo_dtype_specs.items():
            if col in block_group.columns:
                try:
                    if dtype == 'object':
                        block_group[col] = block_group[col].astype(str)
                    elif dtype == 'float64':
                        block_group[col] = pd.to_numeric(block_group[col], errors='coerce').astype('float64')
                except Exception as e:
                    logging.warning(f"Could not convert column {col} to {dtype}: {e}")
        
        # Load other data files
        pop = pd.read_csv(pop_filename)
        flood = pd.read_csv(flood_filename)
        housing = pd.read_csv(housing_filename)
        hedonic = pd.read_csv(hedonic_filename)
        
        # Apply field mapping for other files if mapper is available
        if mapper:
            pop = mapper.map_dataframe(pop, 'pop')
            flood = mapper.map_dataframe(flood, 'flood')
            housing = mapper.map_dataframe(housing, 'housing')
            hedonic = mapper.map_dataframe(hedonic, 'hedonic')
        
        # Enforce specific data types for population file columns
        # Note: After field mapping, the population field is always named 'AJWME001'
        pop_dtype_specs = {
            'GISJOIN': 'object',
            'AJWME001': 'int64'
        }
        
        # Apply data type conversions for population file
        for col, dtype in pop_dtype_specs.items():
            if col in pop.columns:
                try:
                    if dtype == 'object':
                        pop[col] = pop[col].astype(str)
                    elif dtype == 'int64':
                        pop[col] = pd.to_numeric(pop[col], errors='coerce').astype('int64')
                except Exception as e:
                    logging.warning(f"Could not convert population column {col} to {dtype}: {e}")
        
        # Enforce specific data types for flood file columns
        flood_dtype_specs = {
            'GISJOIN': 'object',
            'Shape_Area': 'float64',
            'fld_area': 'float64',
            'perc_fld_area': 'float64'
        }
        
        # Apply data type conversions for flood file
        for col, dtype in flood_dtype_specs.items():
            if col in flood.columns:
                try:
                    if dtype == 'object':
                        flood[col] = flood[col].astype(str)
                    elif dtype == 'float64':
                        flood[col] = pd.to_numeric(flood[col], errors='coerce').astype('float64')
                except Exception as e:
                    logging.warning(f"Could not convert flood column {col} to {dtype}: {e}")
        
        # Enforce specific data types for housing file columns
        housing_dtype_specs = {
            'GISJOIN': 'object',
            'pop1990': 'int64',
            'mhi1990': 'int64',
            'hhsize1990': 'float64',
            'coastdist': 'float64',
            'cbddist': 'float64',
            'hhtrans1993': 'float64',
            'salesprice1993': 'float64',
            'salespricesf1993': 'float64'
        }
        
        # Apply data type conversions for housing file
        for col, dtype in housing_dtype_specs.items():
            if col in housing.columns:
                try:
                    if dtype == 'object':
                        housing[col] = housing[col].astype(str)
                    elif dtype == 'int64':
                        housing[col] = pd.to_numeric(housing[col], errors='coerce').astype('int64')
                    elif dtype == 'float64':
                        housing[col] = pd.to_numeric(housing[col], errors='coerce').astype('float64')
                except Exception as e:
                    logging.warning(f"Could not convert housing column {col} to {dtype}: {e}")
        
        # Enforce specific data types for hedonic file columns
        hedonic_dtype_specs = {
            'GISJOIN': 'object',
            'N_MeanSqfeet': 'float64',
            'N_MeanAge': 'float64',
            'N_MeanNoOfStories': 'float64',
            'N_MeanFullBathNumber': 'float64',
            'residuals': 'float64',
            'N_perc_area_flood': 'float64'
        }
        
        # Apply data type conversions for hedonic file
        for col, dtype in hedonic_dtype_specs.items():
            if col in hedonic.columns:
                try:
                    if dtype == 'object':
                        hedonic[col] = hedonic[col].astype(str)
                    elif dtype == 'float64':
                        hedonic[col] = pd.to_numeric(hedonic[col], errors='coerce').astype('float64')
                except Exception as e:
                    logging.warning(f"Could not convert hedonic column {col} to {dtype}: {e}")

        # join census/population data to block groups
        # Note: After field mapping, the population field is always named 'AJWME001'
        block_group = pd.merge(block_group, pop[['GISJOIN', 'AJWME001']], how='left', on='GISJOIN')
        block_group = pd.merge(block_group, flood[['GISJOIN', 'perc_fld_area']], how='left', on='GISJOIN')
        block_group['perc_fld_area'] = block_group['perc_fld_area'].fillna(0)
        block_group = pd.merge(block_group, housing, how='left', on='GISJOIN')

        # load table with hedonic regression information for utility function
        block_group = pd.merge(block_group, hedonic[['GISJOIN', 'N_MeanSqfeet', 'N_MeanAge', 'N_MeanNoOfStories','N_MeanFullBathNumber','N_perc_area_flood','residuals']], how='left', on='GISJOIN')

        # determine relative cbd proximity and relative flood risk for input to household utility calcs (JY consider moving into an if statement so only loads with specified utility formulation)
        block_group['rel_prox_cbd'] = block_group['cbddist'].max() + 1 - block_group['cbddist']
        block_group['rel_flood_risk'] = block_group['perc_fld_area'].max() + 1 - block_group['perc_fld_area']

        # calculate normalized values for cbd proximity and flood risk
        block_group['prox_cbd_norm'] = block_group['rel_prox_cbd'] / block_group['rel_prox_cbd'].max()
        block_group['flood_risk_norm'] = block_group['rel_flood_risk'] / block_group['rel_flood_risk'].max()

        # calculate housing budget based on 1990-1993 data
        block_group['housing_budget_perc'] = block_group['mhi1990'] / block_group['salesprice1993']

        # replace 0 mhi1990 values with non-zero minimum
        non_zero_min = block_group[(block_group.mhi1990 > 0)].mhi1990.min()
        block_group.loc[block_group['mhi1990'] == 0, 'mhi1990'] = non_zero_min

        for index, row in block_group.iterrows():  # JY fill in missing sales price and hedonic regression values with nearest neighbor values that have data (this can be pre-processed to save computation time)
            if np.isnan(row['salesprice1993']) or np.isnan(row['N_MeanSqfeet']):
                location = row['geometry']
                block_group_subset = block_group[(block_group.GEOID != row['GEOID']) & (np.isfinite(block_group.salesprice1993)) & (np.isfinite(block_group.N_MeanSqfeet))]
                polygon_index = block_group_subset.distance(location).sort_values().index[0]
                block_group.at[index, 'salesprice1993'] = block_group_subset.loc[polygon_index, 'salesprice1993']
                block_group.at[index, 'N_MeanSqfeet'] = block_group_subset.loc[polygon_index, 'N_MeanSqfeet']
                block_group.at[index, 'N_MeanAge'] = block_group_subset.loc[polygon_index, 'N_MeanAge']
                block_group.at[index, 'N_MeanNoOfStories'] = block_group_subset.loc[polygon_index, 'N_MeanNoOfStories']
                block_group.at[index, 'N_MeanFullBathNumber'] = block_group_subset.loc[polygon_index, 'N_MeanFullBathNumber']
                block_group.at[index, 'N_perc_area_flood'] = block_group_subset.loc[polygon_index, 'N_perc_area_flood']
                block_group.at[index, 'residuals'] = block_group_subset.loc[polygon_index, 'residuals']
                block_group.at[index, 'salespricesf1993'] = block_group_subset.loc[polygon_index, 'salespricesf1993']

        # initialize new price for updating
        block_group['new_price'] = block_group['salesprice1993']

        # for each entry in census table, create pysnim-based block group cell/node
        cells = []
        for index, row in block_group.iterrows():
            x = row['geometry'].centroid.x  # gets x-coord of centroid on polygon from shapely geometric object
            y = row['geometry'].centroid.y  # gets x-coord of centroid on polygon from shapely geometric object
            cells.append(
                BlockGroup(
                    name=row['GEOID'], 
                    x=x, 
                    y=y, 
                    county=row['COUNTYFP'], 
                    tract=row['TRACTCE'],
                    blkgrpce=row['BLKGRPCE'], 
                    area=row['ALAND'], 
                    geometry=row['geometry'],
                    init_pop=row['AJWME001'], 
                    perc_fld_area=row['perc_fld_area'],
                    pop90=row['pop1990'], 
                    mhi90=row['mhi1990'], 
                    household_size90=row['hhsize1990'],
                    coastdist=row['coastdist'], 
                    cbddist=row['cbddist'], 
                    hhtrans93=row['hhtrans1993'],
                    salesprice93=row['salesprice1993'], 
                    salespricesf93=row['salespricesf1993']
                )
            )

        # store the block_group pandas dataframe on the network object as a reference
        landscape.housing_block_group_df = block_group

        landscape.add_nodes(*cells)

        self.add_network(landscape)
        logging.info(str(len(self.network.nodes)) + " block group nodes were added to the network")
        
        # Log the final data types for verification
        logging.info("Geographic data column types after processing:")
        for col in ['GISJOIN', 'GEOID', 'COUNTYFP', 'TRACTCE', 'BLKGRPCE', 'ALAND', 'geometry']:
            if col in block_group.columns:
                logging.info(f"  {col}: {block_group[col].dtype}")
        
        logging.info("Population data column types after processing:")
        for col in ['GISJOIN', 'AJWME001']:
            if col in pop.columns:
                logging.info(f"  {col}: {pop[col].dtype}")
        
        logging.info("Flood data column types after processing:")
        for col in ['GISJOIN', 'Shape_Area', 'fld_area', 'perc_fld_area']:
            if col in flood.columns:
                logging.info(f"  {col}: {flood[col].dtype}")
        
        logging.info("Housing data column types after processing:")
        for col in ['GISJOIN', 'pop1990', 'mhi1990', 'hhsize1990', 'coastdist', 'cbddist', 'hhtrans1993', 'salesprice1993', 'salespricesf1993']:
            if col in housing.columns:
                logging.info(f"  {col}: {housing[col].dtype}")
        
        logging.info("Hedonic data column types after processing:")
        for col in ['GISJOIN', 'N_MeanSqfeet', 'N_MeanAge', 'N_MeanNoOfStories', 'N_MeanFullBathNumber', 'residuals', 'N_perc_area_flood']:
            if col in hedonic.columns:
                logging.info(f"  {col}: {hedonic[col].dtype}")

    def convert_initial_population_to_agents(self, no_households_per_agent=10, simple_avoidance_perc=.10):
        logging.info("Converting initial population to agents and adding to the simulation")
        count = 1
        for block_group in self.network.nodes:
            if block_group.household_size90 != 0 and np.isfinite(block_group.household_size90):
                no_of_households = round(block_group.pop90 / block_group.household_size90)

            else:  # if household size is 0 or nan (i.e., data error) using median household size for population
                no_of_households = round(block_group.pop90 / self.network.housing_block_group_df["hhsize1990"].median())

            no_of_agents = (no_of_households + no_households_per_agent // 2) // no_households_per_agent  # division with rounding to nearest integer
            
            for a in range(no_of_agents):
                name = 'hh_agent_initial_' + str(count)
                self.network.add_component(
                    HouseholdAgent(
                        name=name, 
                        location=block_group.name, 
                        no_households_per_agent=no_households_per_agent,
                        household_size=block_group.household_size90, 
                        income=block_group.mhi90, 
                        house_budget_mode='rhea',
                        year_of_residence=self.start_year, 
                        simple_avoidance_perc=simple_avoidance_perc
                    )
                )  # add household agent to pynsim network

                block_group.household_agents[self.network.components[-1].name] = self.network.components[-1]  # add pynsim household agent to associated block group node
                block_group.occupied_units += 1  # add occupied unit to associated block group node
                self.network.get_institution('all_household_agents').add_component(self.network.components[-1])  # add pynsim household agent to all household agents institution
                count += 1
        logging.info(str(count) + " initial agents added to the simulation")

    def initialize_available_building_units(self, initial_vacancy=.20):
        # currently assume a fixed initial vacancy rate across all block groups at the initial_vacancy percentage
        logging.info("Converting initial population to building availability")
        for block_group in self.network.nodes:
            block_group.available_units = round((initial_vacancy * block_group.occupied_units) / (1 - initial_vacancy))
