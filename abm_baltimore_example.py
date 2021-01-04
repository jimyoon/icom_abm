# Import packages
from model_classes.simulator import ICOMSimulator
from model_classes.institutional_categories import AllHHAgents
from model_classes.institutional_agents import CountyZoningManager
from model_engines.agent_creation import NewAgentCreation
from model_engines.existing_agent_relocation import ExistingAgentReloSampler
from model_engines.housing_inventory import HousingInventory
from model_engines.new_agent_location import NewAgentLocation
from model_engines.existing_agent_relocation import ExistingAgentLocation
from model_engines.housing_market import HousingMarket
from model_engines.flood_hazard import FloodHazard
from model_engines.zoning import Zoning
import time

# Record start of model time
start_time = time.time()

# Define simulation options/setup (eventually can use excel interface file)
simulation_name = 'ABM_Baltimore_example'
scenario = 'Baseline'
intervention = 'Baseline'
start_year = 2018
no_years = 5
agent_housing_aggregation = 100  # indicates the level of agent/building aggregation (e.g., 100 indicates that 1 representative agent = 100 households, 1 representative building = 100 residences)

# Define census geographies files / data
landscape_name = 'Baltimore'
geo_filename = 'blck_grp_extract.gpkg'  # accommodates census geographies in IPUMS/NHGIS and imported as QGIS Geopackage
pop_filename = 'balt_bg_population_2018.csv'  # accommodates census data in IPUMS/NHGIS and imported as csv
pop_fieldname = 'AJWME001'  # from IPUMS/NHGIS metadata

# Create pynsim simulation object and set timesteps, landscape on simulation
s = ICOMSimulator(network=None, record_time=False, progress=False, max_iterations=1,
                  name=simulation_name, scenario=scenario, intervention=intervention, start_year=start_year, no_of_years=no_years)
s.set_timestep_information()

# Load geography/landscape information to simulation object
growth_mode = 'perc'
s.set_landscape(landscape_name=landscape_name, geo_filename=geo_filename, pop_filename=pop_filename, pop_fieldname=pop_fieldname, growth_mode=growth_mode)

# Create a county-level institution (agent) that will make zoning decisions
s.network.add_institution(CountyZoningManager(name='005'))
for bg in s.network.nodes:
    if bg.county == '005':
        s.network.get_institution('005').add_node(bg)

# Create an institution (categorical) that will contain all household agents
s.network.add_institution(AllHHAgents(name='all_hh_agents'))

# Create initial household agents based on initial population data
hh_size = 4
s.convert_initial_population_to_agents(no_hhs_per_agent=agent_housing_aggregation, hh_size=hh_size)

# Load new agent creation engine to simulation object
target = s.network
growth_mode = 'perc'
growth_rate = .01
s.add_engine(NewAgentCreation(target, growth_mode=growth_mode, growth_rate=growth_rate, no_hhs_per_agent=agent_housing_aggregation, hh_size=hh_size))

# Load existing agent sampler (for re-location) to simulation object
target = s.network
perc_move = .10  # percentage of population that is assumed to move
s.add_engine(ExistingAgentReloSampler(target, perc_move=perc_move))

# Load housing inventory engine
target = s.network
s.add_engine(HousingInventory(target, residences_per_unit=agent_housing_aggregation))

# Load new agent location engine to simulation object
bg_sample_size = 10  # the number of homes that a new agent samples for residential choice
s.add_engine(NewAgentLocation(target, bg_sample_size))

# Load existing agent re-location engine to simulation object
target = s.network
bg_sample_size = 10  # the number of homes that a re-locating agent samples for residential choice
s.add_engine(ExistingAgentLocation(target, bg_sample_size=bg_sample_size))

# Load housing market engine to simulation object
target = s.network
market_mode = 'top_candidate'
s.add_engine(HousingMarket(target, market_mode=market_mode, bg_sample_size=bg_sample_size))

# Load flood hazard engine to simulation object
target = s.network
s.add_engine(FloodHazard(target))

# Load Zoning engine to simulation object
target = s.network.get_institution('005')
s.add_engine(Zoning(target))

# Run simulation
s.start()

# Record end time
end_time = time.time()
sim_time = end_time-start_time
print("Simulation took (seconds):  %s" % sim_time)