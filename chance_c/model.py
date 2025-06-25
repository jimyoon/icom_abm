from typing import Tuple,Union
import logging
import time

from .data_loader import SimulationConfig
from .model_classes.simulator import ICOMSimulator
from .model_classes.institutional_categories import AllHHAgents
from .model_engines.agent_creation import NewAgentCreation
from .model_engines.existing_agent_relocation import ExistingAgentReloSampler
from .model_engines.new_agent_location import NewAgentLocation
from .model_engines.existing_agent_relocation import ExistingAgentLocation
from .model_engines.housing_market import HousingMarket
from .model_engines.building_development import BuildingDevelopment
from .model_engines.housing_pricing import HousingPricing
from .model_engines.landscape_statistics import LandscapeStatistics
from .model_classes.institutional_agents import CountyZoningManager, RealEstate
from .model_engines.real_estate_prices import RealEstatePrices
from .model_engines.flood_hazard import FloodHazard
from .model_engines.zoning import Zoning


# Setup logging
logging.basicConfig(level=logging.INFO)


def simulate(
        config_file_path: Union[str, None] = None,
        simulation_name: str = 'ABM_Baltimore_example',
        scenario: str = 'Baseline',
        intervention: str = 'Baseline',
        start_year: int = 2018,
        no_years: int = 2,
        agent_housing_aggregation: int = 10,
        hh_size: float = 2.7,
        initial_vacancy: float = 0.20,
        pop_growth_mode: str = 'perc',
        pop_growth_perc: float = 0.01,
        inc_growth_mode: str = 'random_agent_replication',
        pop_growth_inc_perc: float = 0.90,
        inc_growth_perc: float = 0.05,
        bld_growth_perc: float = 0.01,
        perc_move: float = 0.10,
        perc_move_mode: str = 'random',
        house_budget_mode: str = 'rhea',
        house_choice_mode: str = 'simple_avoidance_utility',
        simple_anova_coefficients: Tuple[int] = (-121428, 294707, 130553, 128990, 154887, -500000),
        simple_avoidance_perc: float = 0.95,
        budget_reduction_perc: float = 0.90,
        stock_increase_mode: str = 'simple_perc',
        stock_increase_perc: float = 0.05,
        housing_pricing_mode: str = 'simple_perc',
        price_increase_perc: float = 0.05,
        landscape_name: str = 'Baltimore',
        geo_filename: str = 'blck_grp_extract_prj.shp',
        pop_filename: str = 'balt_bg_population_2018.csv',
        pop_fieldname: str = 'AJWME001',
        flood_filename: str = 'bg_perc_100yr_flood.csv',
        housing_filename: str = 'bg_housing_1993.csv',
        hedonic_filename: str = 'simple_anova_hedonic_without_flood_bg0418.csv',
        record_time: bool = False,
        progress: bool = False,
        max_iterations: int = 1,
        name: str = 'ABM_Baltimore_example',
        write_config: bool = False,
        config_output_file_path: str = 'config.yaml',
        network = None,
        sensitivity_run: bool = False,
        county_agent_id: str = '005',
        bg_sample_size: int = 10, # the number of homes that a new agent samples for residential choice
        zoning_mode: str = 'simple_perc',
        zoning_perc: float = 0.05,
        market_mode: str = 'top_candidate',
):
    start_time = time.time()

    if config_file_path is not None:
        config = SimulationConfig.from_yaml(config_file_path)
    else:
        config = SimulationConfig(
            simulation_name=simulation_name,
            scenario=scenario,
            intervention=intervention,
            start_year=start_year,
            no_years=no_years,
            agent_housing_aggregation=agent_housing_aggregation,
            hh_size=hh_size,
            initial_vacancy=initial_vacancy,
            pop_growth_mode=pop_growth_mode,
            pop_growth_perc=pop_growth_perc,
            inc_growth_mode=inc_growth_mode,
            pop_growth_inc_perc=pop_growth_inc_perc,
            inc_growth_perc=inc_growth_perc,
            bld_growth_perc=bld_growth_perc,
            perc_move=perc_move,
            perc_move_mode=perc_move_mode,
            house_budget_mode=house_budget_mode,
            house_choice_mode=house_choice_mode,
            simple_anova_coefficients=simple_anova_coefficients,
            simple_avoidance_perc=simple_avoidance_perc,
            budget_reduction_perc=budget_reduction_perc,
            stock_increase_mode=stock_increase_mode,
            stock_increase_perc=stock_increase_perc,
            housing_pricing_mode=housing_pricing_mode,
            price_increase_perc=price_increase_perc,
            landscape_name=landscape_name,
            geo_filename=geo_filename,
            pop_filename=pop_filename,
            pop_fieldname=pop_fieldname,
            flood_filename=flood_filename,
            housing_filename=housing_filename,
            hedonic_filename=hedonic_filename,
        )
    
    config.record_time = record_time
    config.progress = progress
    config.max_iterations = max_iterations
    config.name = name
    config.sensitivity_run = sensitivity_run
    config.bg_sample_size = bg_sample_size
    config.market_mode = market_mode

    if config.sensitivity_run is False:
        config.county_agent_id = county_agent_id
        config.zoning_mode = zoning_mode
        config.zoning_perc = zoning_perc

    if write_config:
        config.to_yaml(config_output_file_path)
        logging.info(f"Config written to {config_output_file_path}")


    # Create pynsim simulation object and set timesteps, landscape on simulation
    s = ICOMSimulator(
        network=None, 
        record_time=config.record_time, 
        progress=config.progress, 
        max_iterations=config.max_iterations,
        name=config.simulation_name, 
        scenario=config.scenario, 
        intervention=config.intervention, 
        start_year=config.start_year, 
        no_of_years=config.no_years
    )

    # sets up timestep information based on model options (start_year, no_years)
    s.set_timestep_information() 

    # Load geography/landscape information to simulation object
    s.set_landscape(
        landscape_name=config.landscape_name, 
        geo_filename=config.geo_filename, 
        pop_filename=config.pop_filename,
        pop_fieldname=config.pop_fieldname, 
        flood_filename=config.flood_filename,
        housing_filename=config.housing_filename, 
        hedonic_filename=config.hedonic_filename
    )
    
    if sensitivity_run is False:
        # Create a county-level institution (agent) that will make zoning decisions (DEACTIVATE for sensitivity experiments)
        s.network.add_institution(CountyZoningManager(name=f'zoning_manager_{county_agent_id}'))
        for bg in s.network.nodes:
            if bg.county == county_agent_id:
                s.network.get_institution(f'zoning_manager_{county_agent_id}').add_node(bg)

    if sensitivity_run is False:
        # Create a real estate agent that will perform analysis of market (hedonic regression) and inform buyers/sellers on prices (DEACTIVATE for sensitivity experiments)
        s.network.add_institution(RealEstate(name='real_estate'))

    # Create an institution (categorical) that will contain all household agents
    s.network.add_institution(AllHHAgents(name='all_hh_agents'))

    # Create household agents based on initial population data
    s.convert_initial_population_to_agents(
        no_hhs_per_agent=config.agent_housing_aggregation, 
        simple_avoidance_perc=config.simple_avoidance_perc
    )

    # Initialize available units on block groups based on initial population data
    s.initialize_available_building_units(initial_vacancy=config.initial_vacancy)

    if sensitivity_run is False:
        # Load real estate pricing engine to simulation object (DEACTIVATED for sensitivity experiments)
        target = s.network.get_institution('real_estate')
        estimation_mode = "OLS_hedonic"
        s.add_engine(RealEstatePrices(target, estimation_mode=estimation_mode))

    # Load new agent creation engine to simulation object
    target = s.network
    s.add_engine(NewAgentCreation(
            target, 
            growth_mode=config.pop_growth_mode, 
            growth_rate=config.pop_growth_perc, 
            inc_growth_mode=config.inc_growth_mode,
            pop_growth_inc_perc=config.pop_growth_inc_perc, 
            inc_growth_perc=config.inc_growth_perc, 
            no_hhs_per_agent=config.agent_housing_aggregation, 
            hh_size=config.hh_size,
            simple_avoidance_perc=config.simple_avoidance_perc
        )
    )

    # Load existing agent sampler (for re-location) to simulation object
    target = s.network
    s.add_engine(ExistingAgentReloSampler(target, perc_move=config.perc_move))

    # Load new agent location engine to simulation object
    s.add_engine(NewAgentLocation(target, bg_sample_size, house_choice_mode=config.house_choice_mode, simple_anova_coefficients=config.simple_anova_coefficients, budget_reduction_perc=config.budget_reduction_perc))

    # Load existing agent re-location engine to simulation object
    target = s.network
    bg_sample_size = 10  # the number of homes that a re-locating agent samples for residential choice
    s.add_engine(ExistingAgentLocation(target, bg_sample_size=bg_sample_size, house_choice_mode=config.house_choice_mode, simple_anova_coefficients=config.simple_anova_coefficients))

    # Load housing market engine to simulation object
    target = s.network
    s.add_engine(HousingMarket(target, market_mode=config.market_mode, bg_sample_size=bg_sample_size))

    # Load housing market engine to simulation object  # JY to complete
    target = s.network
    s.add_engine(BuildingDevelopment(target, stock_increase_mode=config.stock_increase_mode, stock_increase_perc=config.stock_increase_perc))

    # Load housing market engine to simulation object  # JY to complete
    target = s.network
    s.add_engine(HousingPricing(target, housing_pricing_mode=config.housing_pricing_mode, price_increase_perc=config.price_increase_perc))

    if config.sensitivity_run is False:
        # Load flood hazard engine to simulation object (DEACTIVATED for sensitivity run)
        target = s.network
        s.add_engine(FloodHazard(target))

    if config.sensitivity_run is False: 
        # Load Zoning engine to simulation object (DEACTIVATED for sensitivity run)
        target = s.network.get_institution(f'zoning_manager_{config.county_agent_id}')
        s.add_engine(Zoning(target, zoning_mode=config.zoning_mode, zoning_perc=config.zoning_perc))


    # Load landscape statistics engine to simulation object  # JY to complete
    target = s.network
    s.add_engine(LandscapeStatistics(target))

    # Run simulation
    s.start()

    # Record end time
    end_time = time.time()
    sim_time = end_time-start_time
    logging.info("Simulation took (seconds):  %s" % sim_time)

    # return the simulation object
    return s
