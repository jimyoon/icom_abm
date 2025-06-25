from dataclasses import dataclass
from typing import Tuple

import yaml


@dataclass
class SimulationConfig:
    """Configuration class for ABM simulation parameters.
    
    A dataclass that holds all configuration parameters for an Agent-Based Model
    simulation, including simulation setup, agent parameters, growth rates,
    housing choice models, and file paths for data sources.
    
    Attributes:
        simulation_name: Name identifier for the simulation run.
        scenario: Scenario identifier for the simulation.
        intervention: Intervention type being simulated.
        start_year: Starting year for the simulation.
        no_years: Number of years to run the simulation (model runs for n+1 years).
        agent_housing_aggregation: Level of agent/building aggregation (e.g., 100
            means 1 representative agent = 100 households).
        hh_size: Average household size across all households.
        initial_vacancy: Initial vacancy rate for all block groups.
        pop_growth_mode: Population growth calculation method ('perc', etc.).
        pop_growth_perc: Annual population percentage growth rate.
        inc_growth_mode: Income growth method for incoming agents.
        pop_growth_inc_perc: Income percentile for in-migrating population.
        inc_growth_perc: Mean income increase for in-migrating population.
        bld_growth_perc: Building stock increase percentage when demand exceeds supply.
        perc_move: Percentage of households that move each timestep.
        perc_move_mode: Method for selecting relocating households.
        house_budget_mode: Method for calculating agent housing budgets.
        house_choice_mode: Household location choice model type.
        simple_anova_coefficients: Coefficients for ANOVA utility calculation.
        simple_avoidance_perc: Percentage of agents that avoid flood plains.
        budget_reduction_perc: Budget reduction percentage for flood insurance costs.
        stock_increase_mode: Method for price increases in high demand areas.
        stock_increase_perc: Percentage increase in housing stock prices.
        housing_pricing_mode: Method for housing price calculations.
        price_increase_perc: Percentage increase for housing prices.
        landscape_name: Geographic area name for the simulation.
        geo_filename: Shapefile containing census geographies.
        pop_filename: CSV file containing population data.
        pop_fieldname: Field name for population data in the CSV.
        flood_filename: CSV file containing FEMA 100-year flood data.
        housing_filename: CSV file containing housing characteristics data.
        hedonic_filename: CSV file containing hedonic regression results.
    """
    
    # Simulation setup
    simulation_name: str = 'ABM_Baltimore_example'
    scenario: str = 'Baseline'
    intervention: str = 'Baseline'
    start_year: int = 2018
    no_years: int = 2
    
    # Agent and housing parameters
    agent_housing_aggregation: int = 10
    hh_size: float = 2.7
    initial_vacancy: float = 0.20
    
    # Population growth parameters
    pop_growth_mode: str = 'perc'
    pop_growth_perc: float = 0.01
    
    # Income growth parameters
    inc_growth_mode: str = 'random_agent_replication'
    pop_growth_inc_perc: float = 0.90
    inc_growth_perc: float = 0.05
    
    # Building and movement parameters
    bld_growth_perc: float = 0.01
    perc_move: float = 0.10
    perc_move_mode: str = 'random'
    
    # Housing choice parameters
    house_budget_mode: str = 'rhea'
    house_choice_mode: str = 'simple_avoidance_utility'
    simple_anova_coefficients: Tuple[int, ...] = (-121428, 294707, 130553, 128990, 154887, -500000)
    simple_avoidance_perc: float = 0.95
    budget_reduction_perc: float = 0.90
    
    # Stock and pricing parameters
    stock_increase_mode: str = 'simple_perc'
    stock_increase_perc: float = 0.05
    housing_pricing_mode: str = 'simple_perc'
    price_increase_perc: float = 0.05
    
    # File paths and data sources
    landscape_name: str = 'Baltimore'
    geo_filename: str = 'blck_grp_extract_prj.shp'
    pop_filename: str = 'balt_bg_population_2018.csv'
    pop_fieldname: str = 'AJWME001'
    flood_filename: str = 'bg_perc_100yr_flood.csv'
    housing_filename: str = 'bg_housing_1993.csv'
    hedonic_filename: str = 'simple_anova_hedonic_without_flood_bg0418.csv'
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'SimulationConfig':
        """Load configuration from a YAML file.
        
        Args:
            yaml_path: Path to the YAML configuration file.
            
        Returns:
            SimulationConfig: Configuration object populated from YAML data.
        """
        with open(yaml_path, 'r') as file:
            config_dict = yaml.safe_load(file)
        return cls(**config_dict)
    
    def to_yaml(self, yaml_path: str) -> None:
        """Save configuration to a YAML file.
        
        Args:
            yaml_path: Path where the YAML file should be saved.
        """
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
