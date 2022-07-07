# Import packages
from model_classes.simulator import ICOMSimulator
from model_classes.institutional_categories import AllHHAgents
from model_engines.agent_creation import NewAgentCreation
from model_engines.existing_agent_relocation import ExistingAgentReloSampler
from model_engines.new_agent_location import NewAgentLocation
from model_engines.existing_agent_relocation import ExistingAgentLocation
from model_engines.housing_market import HousingMarket
from model_engines.building_development import BuildingDevelopment
from model_engines.housing_pricing import HousingPricing
from model_engines.landscape_statistics import LandscapeStatistics
import time
# from model_classes.institutional_agents import CountyZoningManager, RealEstate
# from model_engines.real_estate_prices import RealEstatePrices
# from model_engines.housing_inventory import HousingInventory
# from model_engines.flood_hazard import FloodHazard
# from model_engines.zoning import Zoning

# Adjust pandas setting to allow for expanded view of dataframes
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Record start of model time
start_time = time.time()

# Define simulation options/setup (eventually can use excel, xml, or some other interface file).
# All adjustable model options should be included here. Eventually store all options below on a new dictionary loaded into the network (e.g., s.network.options)
simulation_name = 'ABM_Baltimore_example'
scenario = 'Baseline'
intervention = 'Baseline'
start_year = 2018
no_years = 5  # no of years (model will run for n+1 years)
agent_housing_aggregation = 15  # indicates the level of agent/building aggregation (e.g., 100 indicates that 1 representative agent = 100 households, 1 representative building = 100 residences)
hh_size = 2.7  # define household size (currently assumes all households have the same size, using average from 1990 data)
initial_vacancy = 0.20  # define initial vacancy for all block groups (currently assumes all block groups have same initial vacancy rate)
pop_growth_mode = 'perc'  # indicates which mode of population growth is used for the model run (e.g., percent-based, exogenous time series, etc.) - currently assume constant percentage growth
pop_growth_perc = .01  # annual population percentage growth rate (only used if pop_growth_mode = 'perc')
inc_growth_mode = 'percentile_based' # defines the mode of income growth for incoming agents (e.g., 'normal_distribution', 'percentile_based', etc.)
pop_growth_inc_perc = .90  # defines the income percentile for the in-migrating population
bld_growth_perc = .01  # indicates the percentage of building stock increase if demand exceeds supply
perc_move = .10  # indicates the percentage of households that move each time step
perc_move_mode = 'random'  # indicates the mode by which relocating households are selected (random, disutility, flood, etc.)
house_budget_mode = 'rhea'  # indicates the mode by which agent's housing budget is calculated (specified percent, rhea, etc.)
house_choice_mode = 'budget_reduction'  # indicates the mode of household location choice model (cobb_douglas_utility, simple_flood_utility, simple_avoidance_utility, budget_reduction)
simple_anova_coefficients = [189680, 129080, 122136, 169503, -1000000]  # coefficients for simple anova experiment [sqfeet, age, stories, baths, flood]
simple_avoidance_perc = .10  # defines the percentage of agents that avoid the flood plain
budget_reduction_perc = .90  # defines the percentage that a household reduces budget for housing good (to reserve for flood insurance costs)
print(simple_anova_coefficients)  # JY Temp
stock_increase_mode = 'simple_perc'  # indicates the mode in which prices increase for homes that are in high demand (simple perc, etc.)
stock_increase_perc = .05  # indicates the percentage increase in price
housing_pricing_mode = 'simple_perc'
price_increase_perc = .05

# Define census geography files / data (all external files that define the domain/city should be defined here)
landscape_name = 'Baltimore'
geo_filename = 'baltimore_blck3.shp'  # accommodates census geographies in IPUMS/NHGIS and imported as QGIS Geopackage
pop_filename = 'balt_blck_population_2020.csv'  # accommodates census data in IPUMS/NHGIS and imported as csv
pop_fieldname = 'pop2020'  # from IPUMS/NHGIS metadata
flood_filename = 'blck_perc_100yr_flood_inheritedFBG.csv'  # FEMA 100-yr flood area data (see pre_"processing/flood_risk_calcs.py")
housing_filename = 'blck_housing_1993_InheritedFromBG_v2.csv'  # housing characteristic data and other information from early 90s (for initialization)
hedonic_filename = 'simple_anova_hedonic_blck_fromBGMean.csv'  # simple ANOVA hedonic regression conducted by Alfred

# Create pynsim simulation object and set timesteps, landscape on simulation
s = ICOMSimulator(network=None, record_time=False, progress=False, max_iterations=1,
                  name=simulation_name, scenario=scenario, intervention=intervention, start_year=start_year, no_of_years=no_years)
s.set_timestep_information()  # sets up timestep information based on model options (start_year, no_years)

# Load geography/landscape information to simulation object
s.set_landscape(landscape_name=landscape_name, geo_filename=geo_filename, pop_filename=pop_filename,
                pop_fieldname=pop_fieldname, flood_filename=flood_filename,
                housing_filename=housing_filename, hedonic_filename=hedonic_filename)

# # Create a county-level institution (agent) that will make zoning decisions (DEACTIVATE for sensitivity experiments)
# s.network.add_institution(CountyZoningManager(name='zoning_manager_005'))
# for bg in s.network.nodes:
#     if bg.county == '005':
#         s.network.get_institution('zoning_manager_005').add_node(bg)

# # Create a real estate agent that will perform analysis of market (hedonic regression) and inform buyers/sellers on prices (DEACTIVATE for sensitivity experiments)
# s.network.add_institution(RealEstate(name='real_estate'))

# Create an institution (categorical) that will contain all household agents
s.network.add_institution(AllHHAgents(name='all_hh_agents'))

# Create household agents based on initial population data
s.convert_initial_population_to_agents(no_hhs_per_agent=agent_housing_aggregation, simple_avoidance_perc=simple_avoidance_perc)

# Initialize available units on block groups based on initial population data
s.initialize_available_building_units(initial_vacancy=initial_vacancy)

# # Load real estate pricing engine to simulation object (DEACTIVATED for sensitivity experiments)
# target = s.network.get_institution('real_estate')
# estimation_mode = "OLS_hedonic"
# s.add_engine(RealEstatePrices(target, estimation_mode=estimation_mode))

# Load new agent creation engine to simulation object
target = s.network
s.add_engine(NewAgentCreation(target, growth_mode=pop_growth_mode, growth_rate=pop_growth_perc, inc_growth_mode=inc_growth_mode,
                              pop_growth_inc_perc=pop_growth_inc_perc, no_hhs_per_agent=agent_housing_aggregation, hh_size=hh_size,
                              simple_avoidance_perc=simple_avoidance_perc))

# Load existing agent sampler (for re-location) to simulation object
target = s.network
s.add_engine(ExistingAgentReloSampler(target, perc_move=perc_move))

# Load housing inventory engine  # JY: deprecated; housing inventory tracked via housing bg df
# target = s.network
# s.add_engine(HousingInventory(target, residences_per_unit=agent_housing_aggregation))

# Load new agent location engine to simulation object
bg_sample_size = 10  # the number of homes that a new agent samples for residential choice
s.add_engine(NewAgentLocation(target, bg_sample_size, house_choice_mode=house_choice_mode, simple_anova_coefficients=simple_anova_coefficients, budget_reduction_perc=budget_reduction_perc))

# Load existing agent re-location engine to simulation object
target = s.network
bg_sample_size = 10  # the number of homes that a re-locating agent samples for residential choice
s.add_engine(ExistingAgentLocation(target, bg_sample_size=bg_sample_size, house_choice_mode=house_choice_mode, simple_anova_coefficients=simple_anova_coefficients))

# Load housing market engine to simulation object
target = s.network
market_mode = 'top_candidate'
s.add_engine(HousingMarket(target, market_mode=market_mode, bg_sample_size=bg_sample_size))

# Load housing market engine to simulation object  # JY to complete
target = s.network
s.add_engine(BuildingDevelopment(target, stock_increase_mode=stock_increase_mode, stock_increase_perc=stock_increase_perc))

# Load housing market engine to simulation object  # JY to complete
target = s.network
s.add_engine(HousingPricing(target, housing_pricing_mode=housing_pricing_mode, price_increase_perc=price_increase_perc))

# # Load flood hazard engine to simulation object (DEACTIVATED for sensitivity run)
# target = s.network
# s.add_engine(FloodHazard(target))

# # Load Zoning engine to simulation object (DEACTIVATED for sensitivity run)
# target = s.network.get_institution('zoning_manager_005')
# s.add_engine(Zoning(target))

# Load landscape statistics engine to simulation object  # JY to complete
target = s.network
s.add_engine(LandscapeStatistics(target))

# Run simulation
s.start()

# Record end time
end_time = time.time()
sim_time = end_time-start_time
print("Simulation took (seconds):  %s" % sim_time)