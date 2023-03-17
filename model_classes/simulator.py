from pynsim import Simulator
from model_classes.landscape import ABMLandscape, BlockGroup
from model_classes.urban_agents import HHAgent
import datetime
import geopandas as gpd
import pandas as pd
import logging
import numpy as np

class ICOMSimulator(Simulator):
    """An ICOM Simulator class (a child of the pynsim Simulator class)
    """
    def __init__(self, network, record_time, progress, max_iterations, name, scenario, intervention, start_year, no_of_years):
        super(ICOMSimulator, self).__init__(network, record_time, progress, max_iterations)
        # set simulator characteristics
        self.name = name
        self.scenario = scenario
        self.intervention = intervention

        #set timestep information
        self.start_year = start_year
        self.no_of_years = no_of_years

    def set_timestep_information(self):
        logging.info("Setting up timestep information")
        timesteps = [datetime.datetime.strptime(str(self.start_year), '%Y')]
        for y in range(self.no_of_years):
            new_year = timesteps[-1].year + 1
            timesteps.append(datetime.datetime.strptime(str(new_year), '%Y'))
        self.set_timesteps(timesteps)
        logging.info("The first timestep is " + str(self.timesteps[0]))
        logging.info("The last timestep is " + str(self.timesteps[-1]))

    def set_landscape(self, landscape_name, geo_filename, pop_filename, pop_fieldname, flood_filename, housing_filename, hedonic_filename):
        """Create landscape based on census geographies / data (assumes data structure follows IPUMS/NHGIS format
        """
        logging.info("Setting up model landscape")
        landscape = ABMLandscape(name=landscape_name)

        bg = gpd.read_file('data_inputs/' + geo_filename)
        pop = pd.read_csv('data_inputs/' + pop_filename)
        flood = pd.read_csv('data_inputs/' + flood_filename)
        housing = pd.read_csv('data_inputs/' + housing_filename)
        hedonic = pd.read_csv('data_inputs/' + hedonic_filename)

        # join census/population data to block groups
        bg = pd.merge(bg, pop[['GISJOIN', pop_fieldname]], how='left', on='GISJOIN')
        bg = pd.merge(bg, flood[['GISJOIN', 'perc_fld_area']], how='left', on='GISJOIN')
        bg['perc_fld_area'] = bg['perc_fld_area'].fillna(0)
        bg = pd.merge(bg, housing, how='left', on='GISJOIN')

        # load table with hedonic regression information for utility function
        bg = pd.merge(bg, hedonic[['GISJOIN', 'N_MeanSqfeet', 'N_MeanAge', 'N_MeanNoOfStories','N_MeanFullBathNumber','N_perc_area_flood','residuals']], how='left', on='GISJOIN')

        # determine relative cbd proximity and relative flood risk for input to hh utility calcs (JY consider moving into an if statement so only loads with specified utility formulation)
        bg['rel_prox_cbd'] = bg['cbddist'].max() + 1 - bg['cbddist']
        bg['rel_flood_risk'] = bg['perc_fld_area'].max() + 1 - bg['perc_fld_area']

        # calculate normalized values for cbd proximity and flood risk
        bg['prox_cbd_norm'] = bg['rel_prox_cbd'] / bg['rel_prox_cbd'].max()
        bg['flood_risk_norm'] = bg['rel_flood_risk'] / bg['rel_flood_risk'].max()

        # calculate housing budget based on 1990-1993 data
        bg['housing_budget_perc'] = bg['mhi1990'] / bg['salesprice1993']

        # replace 0 mhi1990 values with non-zero minimum
        non_zero_min = bg[(bg.mhi1990 > 0)].mhi1990.min()
        bg.loc[bg['mhi1990'] == 0, 'mhi1990'] = non_zero_min

        for index, row in bg.iterrows():  # JY fill in missing sales price and hedonic regression values with nearest neighbor values that have data (this can be pre-processed to save computation time)
            if np.isnan(row['salesprice1993']) or np.isnan(row['N_MeanSqfeet']):
                location = row['geometry']
                bg_subset = bg[(bg.GEOID != row['GEOID']) & (np.isfinite(bg.salesprice1993)) & (np.isfinite(bg.N_MeanSqfeet))]
                polygon_index = bg_subset.distance(location).sort_values().index[0]
                bg.at[index, 'salesprice1993'] = bg_subset.loc[[polygon_index]]['salesprice1993']
                bg.at[index, 'N_MeanSqfeet'] = bg_subset.loc[[polygon_index]]['N_MeanSqfeet']
                bg.at[index, 'N_MeanAge'] = bg_subset.loc[[polygon_index]]['N_MeanAge']
                bg.at[index, 'N_MeanNoOfStories'] = bg_subset.loc[[polygon_index]]['N_MeanNoOfStories']
                bg.at[index, 'N_MeanFullBathNumber'] = bg_subset.loc[[polygon_index]]['N_MeanFullBathNumber']
                bg.at[index, 'N_perc_area_flood'] = bg_subset.loc[[polygon_index]]['N_perc_area_flood']
                bg.at[index, 'residuals'] = bg_subset.loc[[polygon_index]]['residuals']
                bg.at[index, 'salespricesf1993'] = bg_subset.loc[[polygon_index]]['salespricesf1993']

        # initialize new price for updating
        bg['new_price'] = bg['salesprice1993']

        # for each entry in census table, create pysnim-based block group cell/node
        cells = []
        for index, row in bg.iterrows():
            x = row['geometry'].centroid.x  # gets x-coord of centroid on polygon from shapely geometric object
            y = row['geometry'].centroid.y  # gets x-coord of centroid on polygon from shapely geometric object
            cells.append(BlockGroup(name=row['GEOID'], x=x, y=y, county=row['COUNTYFP'], tract=row['TRACTCE'],
                                    blkgrpce=row['BLKGRPCE'], area=row['ALAND'], geometry=row['geometry'],
                                    init_pop=row[pop_fieldname], perc_fld_area=row['perc_fld_area'],
                                    pop90=row['pop1990'], mhi90=row['mhi1990'], hhsize90=row['hhsize1990'],
                                    coastdist=row['coastdist'], cbddist=row['cbddist'], hhtrans93=row['hhtrans1993'],
                                    salesprice93=row['salesprice1993'], salespricesf93=row['salespricesf1993']))

        # store the bg pandas dataframe on the network object as a reference
        landscape.housing_bg_df = bg

        landscape.add_nodes(*cells)

        self.add_network(landscape)
        logging.info(str(len(self.network.nodes)) + " block group nodes were added to the network")


    def convert_initial_population_to_agents(self, no_hhs_per_agent=10, simple_avoidance_perc=.10):
        logging.info("Converting initial population to agents and adding to the simulation")
        count = 1
        for bg in self.network.nodes:
            if bg.hhsize90 != 0 and np.isfinite(bg.hhsize90):
                no_of_hhs = round(bg.pop90 / bg.hhsize90)
            else:  # if hh size is 0 or nan (i.e., data error) using median household size for population
                no_of_hhs = round(bg.pop90 / self.network.housing_bg_df.hhsize1990.median())
            no_of_agents = (no_of_hhs + no_hhs_per_agent // 2) // no_hhs_per_agent  # division with rounding to nearest integer
            for a in range(no_of_agents):
                name = 'hh_agent_initial_' + str(count)
                self.network.add_component(HHAgent(name=name, location=bg.name, no_hhs_per_agent=no_hhs_per_agent,
                                                   hh_size=bg.hhsize90, income=bg.mhi90, house_budget_mode='rhea',
                                                   year_of_residence=self.start_year, simple_avoidance_perc=simple_avoidance_perc))  # add household agent to pynsim network
                bg.hh_agents[self.network.components[-1].name] = self.network.components[-1]  # add pynsim household agent to associated block group node
                bg.occupied_units += 1  # add occupied unit to associated block group node
                self.network.get_institution('all_hh_agents').add_component(self.network.components[-1])  # add pynsim household agent to all hh agents institution
                count += 1
        logging.info(str(count) + " initial agents added to the simulation")

    def initialize_available_building_units(self, initial_vacancy=.20):
        # currently assume a fixed initial vacancy rate across all block groups at the initial_vacancy percentage
        logging.info("Converting initial population to building availability")
        for bg in self.network.nodes:
            bg.available_units = round((initial_vacancy * bg.occupied_units) / (1 - initial_vacancy))



