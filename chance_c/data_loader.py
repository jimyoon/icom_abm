from dataclasses import dataclass
from typing import Tuple
import yaml


@dataclass
class SimulationConfig:
    """Configuration class for ABM simulation parameters."""
    
    # Simulation setup
    simulation_name: str = 'ABM_Baltimore_example'
    scenario: str = 'Baseline'
    intervention: str = 'Baseline'
    start_year: int = 2018
    no_years: int = 2  # no of years (model will run for n+1 years)
    
    # Agent and housing parameters
    agent_housing_aggregation: int = 10  # indicates the level of agent/building aggregation (e.g., 100 indicates that 1 representative agent = 100 households, 1 representative building = 100 residences)
    hh_size: float = 2.7  # define household size (currently assumes all households have the same size, using average from 1990 data)
    initial_vacancy: float = 0.20  # define initial vacancy for all block groups (currently assumes all block groups have same initial vacancy rate)
    
    # Population growth parameters
    pop_growth_mode: str = 'perc'  # indicates which mode of population growth is used for the model run (e.g., percent-based, exogenous time series, etc.) - currently assume constant percentage growth
    pop_growth_perc: float = 0.01  # annual population percentage growth rate (only used if pop_growth_mode = 'perc')
    
    # Income growth parameters
    inc_growth_mode: str = 'random_agent_replication'  # defines the mode of income growth for incoming agents (e.g., 'normal_distribution', 'percentile_based', 'random_agent_replication', etc.)
    pop_growth_inc_perc: float = 0.90  # defines the income percentile for the in-migrating population (if inc_growth_mode is 'percentile_based')
    inc_growth_perc: float = 0.05  # defines the increase mean incomes of the in-migrating population (if inc_growth_mode is 'normal_distribution')
    
    # Building and movement parameters
    bld_growth_perc: float = 0.01  # indicates the percentage of building stock increase if demand exceeds supply
    perc_move: float = 0.10  # indicates the percentage of households that move each time step
    perc_move_mode: str = 'random'  # indicates the mode by which relocating households are selected (random, disutility, flood, etc.)
    
    # Housing choice parameters
    house_budget_mode: str = 'rhea'  # indicates the mode by which agent's housing budget is calculated (specified percent, rhea, etc.)
    house_choice_mode: str = 'simple_avoidance_utility'  # indicates the mode of household location choice model (cobb_douglas_utility, simple_flood_utility, simple_avoidance_utility, budget_reduction)
    simple_anova_coefficients: Tuple[int] = (-121428, 294707, 130553, 128990, 154887, -500000)  # coefficients for simple anova experiment [intercept, sqfeet, age, stories, baths, flood]
    simple_avoidance_perc: float = 0.95  # defines the percentage of agents that avoid the flood plain
    budget_reduction_perc: float = 0.90  # defines the percentage that a household reduces budget for housing good (to reserve for flood insurance costs)
    
    # Stock and pricing parameters
    stock_increase_mode: str = 'simple_perc'  # indicates the mode in which prices increase for homes that are in high demand (simple perc, etc.)
    stock_increase_perc: float = 0.05  # indicates the percentage increase in price
    housing_pricing_mode: str = 'simple_perc'
    price_increase_perc: float = 0.05
    
    # File paths and data sources
    landscape_name: str = 'Baltimore'
    geo_filename: str = 'blck_grp_extract_prj.shp'  # accommodates census geographies in IPUMS/NHGIS and imported as QGIS Geopackage
    pop_filename: str = 'balt_bg_population_2018.csv'  # accommodates census data in IPUMS/NHGIS and imported as csv
    pop_fieldname: str = 'AJWME001'  # from IPUMS/NHGIS metadata
    flood_filename: str = 'bg_perc_100yr_flood.csv'  # FEMA 100-yr flood area data (see pre_"processing/flood_risk_calcs.py")
    housing_filename: str = 'bg_housing_1993.csv'  # housing characteristic data and other information from early 90s (for initialization)
    hedonic_filename: str = 'simple_anova_hedonic_without_flood_bg0418.csv'  # simple ANOVA hedonic regression conducted by Alfred
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'SimulationConfig':
        """Load configuration from a YAML file."""
        with open(yaml_path, 'r') as file:
            config_dict = yaml.safe_load(file)
        return cls(**config_dict)
    
    def to_yaml(self, yaml_path: str) -> None:
        """Save configuration to a YAML file."""
        config_dict = {
            'simulation_name': self.simulation_name,
            'scenario': self.scenario,
            'intervention': self.intervention,
            'start_year': self.start_year,
            'no_years': self.no_years,
            'agent_housing_aggregation': self.agent_housing_aggregation,
            'hh_size': self.hh_size,
            'initial_vacancy': self.initial_vacancy,
            'pop_growth_mode': self.pop_growth_mode,
            'pop_growth_perc': self.pop_growth_perc,
            'inc_growth_mode': self.inc_growth_mode,
            'pop_growth_inc_perc': self.pop_growth_inc_perc,
            'inc_growth_perc': self.inc_growth_perc,
            'bld_growth_perc': self.bld_growth_perc,
            'perc_move': self.perc_move,
            'perc_move_mode': self.perc_move_mode,
            'house_budget_mode': self.house_budget_mode,
            'house_choice_mode': self.house_choice_mode,
            'simple_anova_coefficients': self.simple_anova_coefficients,
            'simple_avoidance_perc': self.simple_avoidance_perc,
            'budget_reduction_perc': self.budget_reduction_perc,
            'stock_increase_mode': self.stock_increase_mode,
            'stock_increase_perc': self.stock_increase_perc,
            'housing_pricing_mode': self.housing_pricing_mode,
            'price_increase_perc': self.price_increase_perc,
            'landscape_name': self.landscape_name,
            'geo_filename': self.geo_filename,
            'pop_filename': self.pop_filename,
            'pop_fieldname': self.pop_fieldname,
            'flood_filename': self.flood_filename,
            'housing_filename': self.housing_filename,
            'hedonic_filename': self.hedonic_filename
        }
        
        with open(yaml_path, 'w') as file:
            yaml.dump(config_dict, file, default_flow_style=False, indent=2)
