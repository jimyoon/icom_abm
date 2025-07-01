"""
Pytest configuration and common fixtures for chance_c tests.
"""
import warnings

# Suppress warnings that are expected during testing
warnings.filterwarnings("ignore", category=UserWarning, message="Column names longer than 10 characters will be truncated when saved to ESRI Shapefile.")
warnings.filterwarnings("ignore", category=RuntimeWarning, message="Normalized/laundered field name:.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, message="The 'shapely.geos' module is deprecated.*")

import pytest
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon
import tempfile
import os
from unittest.mock import Mock, patch

from chance_c import (
    Model, SimulationConfig, FieldMapper,
    ICOMSimulator, ABMLandscape, BlockGroup, HouseholdAgent,
    AllHouseholdAgents, CountyZoningManager, RealEstate,
    NewAgentCreation, HousingMarket, BuildingDevelopment
)


@pytest.fixture
def sample_config():
    """Create a sample SimulationConfig for testing."""
    return SimulationConfig(
        simulation_name="test_simulation",
        scenario="test_scenario",
        start_year=2020,
        n_years=2,
        agent_housing_aggregation=10,
        landscape_name="test_landscape"
    )


@pytest.fixture
def sample_block_groups():
    """Create sample block group data for testing."""
    # Create sample geometries
    geometries = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
        Polygon([(0, 1), (1, 1), (1, 2), (0, 2)])
    ]
    
    # Create sample data
    data = {
        'GEOID': ['bg_001', 'bg_002', 'bg_003'],
        'population': [1000, 1500, 800],
        'income': [50000, 75000, 45000],
        'housing_units': [400, 600, 300],
        'vacant_units': [40, 60, 30],
        'flood_risk': [0.1, 0.05, 0.2],
        'geometry': geometries
    }
    
    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def sample_household_agents():
    """Create sample household agents for testing."""
    agents = []
    for i in range(5):
        agent = HouseholdAgent(
            name=f"household_{i}",
            location=f"bg_{i % 3 + 1:03d}",
            income=50000 + i * 10000,
            household_size=2.5 + (i % 3) * 0.5
        )
        agents.append(agent)
    return agents


@pytest.fixture
def mock_network():
    """Create a mock network for testing."""
    network = Mock()
    network.nodes = {}
    network.components = []
    network.institutions = {}
    network.history = {}
    
    # Mock methods
    network.add_component = Mock()
    network.add_institution = Mock()
    network.get_institution = Mock()
    network.get_history = Mock(return_value=pd.DataFrame())
    
    return network


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_csv_data():
    """Create sample CSV data for testing data loading."""
    data = {
        'GEOID': ['bg_001', 'bg_002', 'bg_003'],
        'population': [1000, 1500, 800],
        'income': [50000, 75000, 45000],
        'housing_units': [400, 600, 300],
        'flood_risk': [0.1, 0.05, 0.2]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_yaml_config():
    """Create a sample YAML configuration string for testing."""
    return """
simulation_name: test_simulation
scenario: test_scenario
start_year: 2020
n_years: 2
agent_housing_aggregation: 10
household_size: 2.7
initial_vacancy: 0.20
pop_growth_mode: perc
pop_growth_perc: 0.01
landscape_name: test_landscape
geo_filename: test_geo.shp
pop_filename: test_pop.csv
flood_filename: test_flood.csv
housing_filename: test_housing.csv
hedonic_filename: test_hedonic.csv
"""


@pytest.fixture
def mock_timestep():
    """Create a mock timestep for testing."""
    timestep = Mock()
    timestep.year = 2020
    timestep.iteration = 1
    return timestep


@pytest.fixture
def sample_field_mapping():
    """Create sample field mapping for testing."""
    return {
        'population': 'pop',
        'income': 'inc',
        'housing_units': 'housing',
        'flood_risk': 'flood',
        'geometry': 'geom'
    }


class MockBlockGroup:
    """Mock BlockGroup class for testing."""
    
    def __init__(self, geoid, population=1000, income=50000, housing_units=400):
        self.geoid = geoid
        self.population = population
        self.income = income
        self.housing_units = housing_units
        self.vacant_units = int(housing_units * 0.1)
        self.flood_risk = 0.1
        self.geometry = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        self.history = {}
    
    def get_history(self, name):
        return self.history.get(name, pd.DataFrame())
    
    def add_history(self, name, data):
        if name not in self.history:
            self.history[name] = []
        self.history[name].append(data)


@pytest.fixture
def sample_block_group_objects():
    """Create sample BlockGroup objects for testing."""
    return [
        MockBlockGroup('bg_001', 1000, 50000, 400),
        MockBlockGroup('bg_002', 1500, 75000, 600),
        MockBlockGroup('bg_003', 800, 45000, 300)
    ]


# Test utilities
def create_mock_landscape():
    """Create a mock landscape for testing."""
    landscape = Mock()
    landscape.block_groups = sample_block_group_objects()
    landscape.geo_data = sample_block_groups()
    return landscape


def assert_dataframe_columns(df, expected_columns):
    """Assert that a DataFrame has the expected columns."""
    assert all(col in df.columns for col in expected_columns), \
        f"Expected columns {expected_columns}, got {list(df.columns)}"


def assert_dataframe_not_empty(df):
    """Assert that a DataFrame is not empty."""
    assert len(df) > 0, "DataFrame is empty"


def assert_numeric_column(df, column):
    """Assert that a column contains numeric data."""
    assert pd.api.types.is_numeric_dtype(df[column]), \
        f"Column {column} is not numeric"


def assert_geodataframe_valid(gdf):
    """Assert that a GeoDataFrame is valid."""
    assert isinstance(gdf, gpd.GeoDataFrame), "Not a GeoDataFrame"
    assert len(gdf) > 0, "GeoDataFrame is empty"
    assert 'geometry' in gdf.columns, "No geometry column"
    assert gdf.crs is not None, "No CRS defined" 