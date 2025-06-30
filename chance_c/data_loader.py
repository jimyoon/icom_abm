from dataclasses import dataclass
from typing import Tuple, Optional
import os
import importlib.resources as pkg_resources

import yaml
from .field_mapper import FieldMapper


def get_default_data_path(filename: str) -> str:
    """Get the path to a default data file in the package.
    
    Args:
        filename: Name of the data file
        
    Returns:
        str: Full path to the data file
    """
    try:
        # Try to get the path from the installed package
        return pkg_resources.resource_filename('chance_c', f'data/example_input_data/{filename}')
    except:
        # Fallback for development/local installation
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, 'data', 'example_input_data', filename)


def get_example_config_path() -> str:
    """Get the path to the example configuration file in the package.
    
    Returns:
        str: Full path to the example configuration file
    """
    try:
        # Try to get the path from the installed package
        return pkg_resources.resource_filename('chance_c', 'data/example_config.yml')
    except:
        # Fallback for development/local installation
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, 'data', 'example_config.yml')


def get_example_field_mapping_path() -> str:
    """Get the path to the example field mapping file in the package.
    
    Returns:
        str: Full path to the example field mapping file
    """
    try:
        # Try to get the path from the installed package
        return pkg_resources.resource_filename('chance_c', 'data/example_field_mapping.yml')
    except:
        # Fallback for development/local installation
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, 'data', 'example_field_mapping.yml')


@dataclass
class SimulationConfig:
    """Configuration class for ABM simulation parameters.
    
    A dataclass that holds all configuration parameters for an Agent-Based Model
    simulation, including simulation setup, agent parameters, growth rates,
    housing choice models, field mappings, and file paths for data sources.
    
    Attributes:
        simulation_name: Name identifier for the simulation run.
        scenario: Scenario identifier for the simulation.
        intervention: Intervention type being simulated.
        start_year: Starting year for the simulation.
        n_years: Number of years to run the simulation (model runs for n+1 years).
        agent_housing_aggregation: Level of agent/building aggregation (e.g., 100
            means 1 representative agent = 100 households).
        household_size: Average household size across all households.
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
        flood_filename: CSV file containing FEMA 100-year flood data.
        housing_filename: CSV file containing housing characteristics data.
        hedonic_filename: CSV file containing hedonic regression results.
        geo_file_mapping: Field mapping for geographic data files.
        pop_file_mapping: Field mapping for population data files.
        flood_file_mapping: Field mapping for flood data files.
        housing_file_mapping: Field mapping for housing data files.
        hedonic_file_mapping: Field mapping for hedonic data files.
        block_group_sample_size: Sample size for block groups.
        zoning_mode: Method for zoning.
        zoning_perc: Percentage of zoning.
        market_mode: Method for market choice.
        log_level: Logging level configuration.
    """
    
    # Simulation setup
    simulation_name: str = 'ABM_Baltimore_example'
    scenario: str = 'Baseline'
    intervention: str = 'Baseline'
    start_year: int = 2018
    n_years: int = 2
    
    # Agent and housing parameters
    agent_housing_aggregation: int = 10
    household_size: float = 2.7
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
    block_group_sample_size: int = 10
    zoning_mode: str = 'simple_perc'
    zoning_perc: float = 0.05
    market_mode: str = 'top_candidate'
    landscape_name: str = 'Baltimore'
    geo_filename: str = ''  # Will be set in __post_init__
    pop_filename: str = ''  # Will be set in __post_init__
    flood_filename: str = ''  # Will be set in __post_init__
    housing_filename: str = ''  # Will be set in __post_init__
    hedonic_filename: str = ''  # Will be set in __post_init__
    
    # Field mapping configurations
    geo_file_mapping: dict = None
    pop_file_mapping: dict = None
    flood_file_mapping: dict = None
    housing_file_mapping: dict = None
    hedonic_file_mapping: dict = None
    
    # Logging configuration
    log_level: str = 'INFO'
    
    def __post_init__(self):
        """Set default file paths and field mappings if not provided."""
        if not self.geo_filename:
            self.geo_filename = get_default_data_path('block_group_extract.shp')
        if not self.pop_filename:
            self.pop_filename = get_default_data_path('block_group_population_2018.csv')
        if not self.flood_filename:
            self.flood_filename = get_default_data_path('block_group_percent_100yr_flood.csv')
        if not self.housing_filename:
            self.housing_filename = get_default_data_path('block_group_housing_1993.csv')
        if not self.hedonic_filename:
            self.hedonic_filename = get_default_data_path('simple_anova_hedonic_without_flood_bg0418.csv')
        
        # Set default field mappings if not provided
        if self.geo_file_mapping is None:
            self.geo_file_mapping = {
                'GISJOIN': 'GISJOIN',
                'GEOID': 'GEOID',
                'COUNTYFP': 'COUNTYFP',
                'TRACTCE': 'TRACTCE',
                'BLKGRPCE': 'BLKGRPCE',
                'ALAND': 'ALAND',
                'geometry': 'geometry'
            }
        
        if self.pop_file_mapping is None:
            self.pop_file_mapping = {
                'GISJOIN': 'GISJOIN',
                'AJWME001': 'AJWME001'
            }
        
        if self.flood_file_mapping is None:
            self.flood_file_mapping = {
                'GISJOIN': 'GISJOIN',
                'Shape_Area': 'Shape_Area',
                'fld_area': 'fld_area',
                'perc_fld_area': 'perc_fld_area'
            }
        
        if self.housing_file_mapping is None:
            self.housing_file_mapping = {
                'GISJOIN': 'GISJOIN',
                'pop1990': 'pop1990',
                'mhi1990': 'mhi1990',
                'hhsize1990': 'hhsize1990',
                'coastdist': 'coastdist',
                'cbddist': 'cbddist',
                'hhtrans1993': 'hhtrans1993',
                'salesprice1993': 'salesprice1993',
                'salespricesf1993': 'salespricesf1993'
            }
        
        if self.hedonic_file_mapping is None:
            self.hedonic_file_mapping = {
                'GISJOIN': 'GISJOIN',
                'N_MeanSqfeet': 'N_MeanSqfeet',
                'N_MeanAge': 'N_MeanAge',
                'N_MeanNoOfStories': 'N_MeanNoOfStories',
                'N_MeanFullBathNumber': 'N_MeanFullBathNumber',
                'N_perc_area_flood': 'N_perc_area_flood',
                'residuals': 'residuals'
            }
    
    def get_field_mapper(self) -> FieldMapper:
        """Get a FieldMapper instance configured with the field mappings.
        
        Returns:
            FieldMapper: Configured field mapper instance.
        """
        mappings = {
            'geo_file_mapping': self.geo_file_mapping,
            'pop_file_mapping': self.pop_file_mapping,
            'flood_file_mapping': self.flood_file_mapping,
            'housing_file_mapping': self.housing_file_mapping,
            'hedonic_file_mapping': self.hedonic_file_mapping
        }
        return FieldMapper(mappings=mappings)
    
    def validate_field_mapping(self) -> bool:
        """Validate the field mapping configuration.
        
        Returns:
            bool: True if valid, False otherwise.
        """
        mapper = self.get_field_mapper()
        return mapper.validate_mappings()
    
    def get_required_columns(self, file_type: str) -> dict:
        """Get required columns for a specific file type.
        
        Args:
            file_type: Type of file ('geo', 'pop', 'flood', 'housing', 'hedonic')
            
        Returns:
            dict: Dictionary mapping required field names to descriptions
        """
        mapper = self.get_field_mapper()
        return mapper.get_required_columns(file_type)
    
    def get_population_field_name(self) -> str:
        """Get the population field name from the field mapping.
        
        Returns:
            str: The population field name (always 'AJWME001' after mapping)
        """
        # After field mapping, the population field is always named 'AJWME001'
        # This is the standard field name used internally by the model
        return 'AJWME001'
    
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
            'n_years': self.n_years,
            'agent_housing_aggregation': self.agent_housing_aggregation,
            'household_size': self.household_size,
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
            'simple_anova_coefficients': list(self.simple_anova_coefficients),
            'simple_avoidance_perc': self.simple_avoidance_perc,
            'budget_reduction_perc': self.budget_reduction_perc,
            'stock_increase_mode': self.stock_increase_mode,
            'stock_increase_perc': self.stock_increase_perc,
            'housing_pricing_mode': self.housing_pricing_mode,
            'price_increase_perc': self.price_increase_perc,
            'landscape_name': self.landscape_name,
            'geo_filename': self.geo_filename,
            'pop_filename': self.pop_filename,
            'flood_filename': self.flood_filename,
            'housing_filename': self.housing_filename,
            'hedonic_filename': self.hedonic_filename,
            'geo_file_mapping': self.geo_file_mapping,
            'pop_file_mapping': self.pop_file_mapping,
            'flood_file_mapping': self.flood_file_mapping,
            'housing_file_mapping': self.housing_file_mapping,
            'hedonic_file_mapping': self.hedonic_file_mapping,
            'block_group_sample_size': self.block_group_sample_size,
            'zoning_mode': self.zoning_mode,
            'zoning_perc': self.zoning_perc,
            'market_mode': self.market_mode,
            'log_level': self.log_level
        }
        
        with open(yaml_path, 'w') as file:
            yaml.dump(config_dict, file, default_flow_style=False, indent=2)
