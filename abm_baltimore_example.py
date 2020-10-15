# Import packages
from model_classes.simulator import ICOMSimulator
from model_classes.institutional_categories import AllHHAgents
from model_engines.agent_location import AgentLocation
from model_engines.flood_hazard import FloodHazard
import time

# Record start of model time
start_time = time.time()

# Define simulation options/setup (eventually can use excel interface file)
simulation_name = 'ABM_Baltimore_example'
scenario = 'Baseline'
intervention = 'Baseline'

# Define census geographies files / data
landscape_name = 'Baltimore'
geo_filename = 'blck_grp_extract.gpkg'  # accommodates census geographies in IPUMS/NHGIS and imported as QGIS Geopackage
pop_filename = 'balt_bg_population_2018.csv'  # accommodates census data in IPUMS/NHGIS and imported as csv
pop_fieldname = 'AJWME001'  # from IPUMS/NHGIS metadata
start_year = 2018
no_years = 5

# Create pynsim simulation object and set timesteps, landscape on simulation
s = ICOMSimulator(network=None, record_time=False, progress=False, max_iterations=1,
                  name=simulation_name, scenario=scenario, intervention=intervention, start_year=start_year, no_of_years=no_years)
s.set_timestep_information()

# Load geography/landscape information to simulation object
s.set_landscape(landscape_name=landscape_name, geo_filename=geo_filename, pop_filename=pop_filename, pop_fieldname=pop_fieldname)

# Create an institution that will contain all household agents
s.network.add_institution(AllHHAgents(name='all_hh_agents'))

# Create initial household agents based on initial population data
no_hhs_per_agent = 100
hh_size = 4
s.convert_initial_population_to_agents(no_hhs_per_agent=no_hhs_per_agent, hh_size=hh_size)

# Load agent location engine to simulation object
target = s.network
perc_move = .10
pop_growth = .01
s.add_engine(AgentLocation(target, pop_growth=pop_growth, no_hhs_per_agent=no_hhs_per_agent, hh_size=hh_size, perc_move=perc_move))

# Load flood hazard engine to simulation object
s.add_engine(FloodHazard(target))

# Run simulation
s.start()

# Record end time
end_time = time.time()
sim_time = end_time-start_time
print("Simulation took (seconds):  %s" % sim_time)