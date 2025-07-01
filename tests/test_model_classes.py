"""
Tests for model classes in chance_c.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from shapely.geometry import Polygon

from chance_c import (
    HouseholdAgent, AllHouseholdAgents, CountyZoningManager, RealEstate,
    ABMLandscape, BlockGroup, ICOMSimulator
)


class TestHouseholdAgent:
    """Test cases for HouseholdAgent class."""
    
    def test_basic_initialization(self):
        """Test basic HouseholdAgent initialization."""
        agent = HouseholdAgent(
            name="test_agent",
            location="bg_001",
            income=50000,
            household_size=2.5
        )
        
        assert agent.name == "test_agent"
        assert agent.location == "bg_001"
        assert agent.income == 50000
        assert agent.household_size == 2.5
        assert agent.no_households_per_agent == 10  # Default value
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        agent = HouseholdAgent(name="test_agent")
        
        assert agent.name == "test_agent"
        assert agent.location is None
        assert agent.no_households_per_agent == 10
        assert agent.household_size == 2.7
        assert agent.income == 50000
        assert agent.house_budget_mode == 'rhea'
        assert agent.year_of_residence == 2018
        assert agent.simple_avoidance_perc == 0.10
    
    def test_custom_values(self):
        """Test setting custom values."""
        agent = HouseholdAgent(
            name="custom_agent",
            location="bg_002",
            no_households_per_agent=20,
            household_size=3.0,
            income=75000,
            house_budget_mode='perc',
            year_of_residence=2020,
            simple_avoidance_perc=0.15
        )
        
        assert agent.name == "custom_agent"
        assert agent.location == "bg_002"
        assert agent.no_households_per_agent == 20
        assert agent.household_size == 3.0
        assert agent.income == 75000
        assert agent.house_budget_mode == 'perc'
        assert agent.year_of_residence == 2020
        assert agent.simple_avoidance_perc == 0.15
    
    def test_house_budget_calculation(self):
        """Test house budget calculation."""
        agent = HouseholdAgent(
            name="test_agent",
            income=50000,
            house_budget_mode='rhea'
        )
        
        # Test RHEA mode calculation
        expected_budget = agent._calculate_house_budget()
        assert expected_budget > 0
        assert isinstance(expected_budget, float)
        
        # Test percentage mode
        agent.house_budget_mode = 'perc'
        perc_budget = agent._calculate_house_budget()
        assert perc_budget == 50000 / 0.33
    
    def test_agent_setup(self):
        """Test agent setup method."""
        agent = HouseholdAgent(name="test_agent")
        
        # Mock network and timestep
        agent.network = Mock()
        agent.network.housing_block_group_df = pd.DataFrame({
            'name': ['bg_001', 'bg_002'],
            'GEOID': ['bg_001', 'bg_002'],
            'average_income_norm': [0.5, 0.8],
            'prox_cbd_norm': [0.3, 0.7],
            'flood_risk_norm': [0.1, 0.4]
        })
        
        agent.setup(timestep=1)
        
        assert hasattr(agent, 'household_utilities')
        assert agent.household_utilities == {}
    
    def test_utility_calculation_random(self):
        """Test random utility calculation."""
        agent = HouseholdAgent(name="test_agent")
        
        agent.calc_utility_random("bg_001")
        
        assert "bg_001" in agent.household_utilities
        assert 0 <= agent.household_utilities["bg_001"] <= 1
    
    def test_agent_properties(self):
        """Test agent properties."""
        agent = HouseholdAgent(
            name="test_agent",
            location="bg_001",
            income=50000,
            household_size=2.5
        )
        
        assert hasattr(agent, '_properties')
        assert 'location' in agent._properties
        assert 'household_utilities' in agent._properties
    
    def test_agent_str(self):
        """Test string representation of agent."""
        agent = HouseholdAgent(name="test_agent", location="bg_001")
        
        str_repr = str(agent)
        assert "test_agent" in str_repr


class TestInstitutions:
    """Test cases for institutional agent classes."""
    
    def test_all_household_agents_initialization(self):
        """Test AllHouseholdAgents initialization."""
        institution = AllHouseholdAgents(name="all_households")
        
        assert institution.name == "all_households"
        assert hasattr(institution, 'components')
    
    def test_county_zoning_manager_initialization(self):
        """Test CountyZoningManager initialization."""
        manager = CountyZoningManager(name="zoning_manager")
        
        assert manager.name == "zoning_manager"
        assert hasattr(manager, '_properties')
    
    def test_real_estate_initialization(self):
        """Test RealEstate initialization."""
        real_estate = RealEstate(name="real_estate")
        
        assert real_estate.name == "real_estate"
        assert hasattr(real_estate, '_properties')
    
    def test_institution_component_management(self, sample_household_agents):
        """Test institution component management."""
        institution = AllHouseholdAgents(name="test_institution")
        
        # Add components
        for agent in sample_household_agents:
            institution.add_component(agent)
        
        assert len(institution.components) == len(sample_household_agents)
        
        # Test component access
        for agent in sample_household_agents:
            assert agent in institution.components
    
    def test_zoning_decisions(self):
        """Test zoning decision making."""
        manager = CountyZoningManager(name="zoning_manager")
        
        # Test basic functionality
        assert manager.name == "zoning_manager"
        assert hasattr(manager, '_properties')


class TestLandscape:
    """Test cases for landscape classes."""
    
    def test_block_group_initialization(self, sample_block_groups):
        """Test BlockGroup initialization."""
        # Test creating BlockGroup with required parameters
        row = sample_block_groups.iloc[0]
        geometry = row['geometry']
        
        block_group = BlockGroup(
            name=row['GEOID'],
            x=0.5,  # Centroid x
            y=0.5,  # Centroid y
            county="001",
            tract="000100",
            blkgrpce="1",
            geometry=geometry,
            area=1.0,
            init_pop=1000,
            perc_fld_area=0.1,
            pop90=1000,
            mhi90=50000,
            household_size90=2.7,
            coastdist=10.0,
            cbddist=5.0,
            hhtrans93=0.5,
            salesprice93=200000,
            salespricesf93=200
        )
        
        assert block_group.name == row['GEOID']
        assert block_group.county == "001"
        assert block_group.tract == "000100"
        assert block_group.blkgrpce == "1"
        assert block_group.geometry == geometry
        assert block_group.area == 1.0
        assert block_group.pop90 == 1000
        assert block_group.mhi90 == 50000
        assert block_group.household_size90 == 2.7
    
    def test_block_group_properties(self, sample_block_groups):
        """Test BlockGroup properties."""
        row = sample_block_groups.iloc[0]
        geometry = row['geometry']
        
        block_group = BlockGroup(
            name=row['GEOID'],
            x=0.5,
            y=0.5,
            county="001",
            tract="000100",
            blkgrpce="1",
            geometry=geometry,
            area=1.0,
            init_pop=1000,
            perc_fld_area=0.1,
            pop90=1000,
            mhi90=50000,
            household_size90=2.7,
            coastdist=10.0,
            cbddist=5.0,
            hhtrans93=0.5,
            salesprice93=200000,
            salespricesf93=200
        )
        
        # Test properties
        assert hasattr(block_group, '_properties')
        assert block_group.population == 1000  # Should be set to pop90
        assert block_group.household_agents == {}
        assert block_group.avg_home_price == 0
        assert block_group.flood_hazard_risk == 0
        assert block_group.available_units == 0
        assert block_group.demand_exceeds_supply == False
        assert block_group.new_units_constructed == 0
        assert block_group.occupied_units == 0
        assert block_group.new_price == 200000
    
    def test_block_group_history(self, sample_block_groups):
        """Test BlockGroup history tracking."""
        row = sample_block_groups.iloc[0]
        geometry = row['geometry']
        
        block_group = BlockGroup(
            name=row['GEOID'],
            x=0.5,
            y=0.5,
            county="001",
            tract="000100",
            blkgrpce="1",
            geometry=geometry,
            area=1.0,
            init_pop=1000,
            perc_fld_area=0.1,
            pop90=1000,
            mhi90=50000,
            household_size90=2.7,
            coastdist=10.0,
            cbddist=5.0,
            hhtrans93=0.5,
            salesprice93=200000,
            salespricesf93=200
        )
        
        # Test history tracking
        assert hasattr(block_group, 'get_history')
        assert callable(block_group.get_history)
    
    def test_abm_landscape_initialization(self, sample_block_groups):
        """Test ABMLandscape initialization."""
        landscape = ABMLandscape(
            name="test_landscape",
            avg_hh_income=50000,
            avg_hh_size=2.7,
            total_population=10000,
            housing_block_group_df=pd.DataFrame()
        )
        
        assert landscape.name == "test_landscape"
        assert landscape.avg_hh_income == 50000
        assert landscape.avg_hh_size == 2.7
        assert landscape.total_population == 10000
        assert landscape.housing_block_group_df is not None
        assert landscape.unassigned_households == {}
        assert landscape.relocating_households == {}
        assert landscape.available_units_list == []
    
    def test_landscape_block_groups(self, sample_block_groups):
        """Test landscape block group management."""
        landscape = ABMLandscape(
            name="test_landscape",
            avg_hh_income=50000,
            avg_hh_size=2.7,
            total_population=10000,
            housing_block_group_df=pd.DataFrame()
        )
        
        # Test block group management
        assert hasattr(landscape, 'nodes')
        assert hasattr(landscape, 'add_node')
        assert hasattr(landscape, 'get_node')
    
    def test_landscape_statistics(self, sample_block_groups):
        """Test landscape statistics calculation."""
        landscape = ABMLandscape(
            name="test_landscape",
            avg_hh_income=50000,
            avg_hh_size=2.7,
            total_population=10000,
            housing_block_group_df=pd.DataFrame()
        )
        
        # Test statistics properties
        assert landscape.avg_hh_income == 50000
        assert landscape.avg_hh_size == 2.7
        assert landscape.total_population == 10000
        assert landscape.housing_block_group_df is not None


class TestSimulator:
    """Test cases for ICOMSimulator class."""
    
    def test_simulator_initialization(self, mock_network):
        """Test ICOMSimulator initialization."""
        simulator = ICOMSimulator(
            network=mock_network,
            name="test_simulator",
            start_year=2020,
            n_years=3
        )
        
        assert simulator.name == "test_simulator"
        assert simulator.start_year == 2020
        assert simulator.n_years == 3
        assert simulator.network == mock_network
    
    def test_simulator_timestep_setup(self, mock_network):
        """Test simulator timestep setup."""
        simulator = ICOMSimulator(
            network=mock_network,
            name="test_simulator",
            start_year=2020,
            n_years=3
        )
        
        # Test timestep setup
        simulator.set_timestep_information()
        
        # Verify timestep information is set
        assert hasattr(simulator, 'timesteps')
        assert len(simulator.timesteps) == 4  # n_years + 1 (start year + n_years)
    
    def test_simulator_engine_management(self, mock_network):
        """Test simulator engine management."""
        simulator = ICOMSimulator(
            network=mock_network,
            name="test_simulator",
            start_year=2020,
            n_years=3
        )
        
        # Test adding engines
        mock_engine = Mock()
        simulator.add_engine(mock_engine)
        
        assert len(simulator.engines) == 1
        assert mock_engine in simulator.engines
    
    def test_simulator_properties(self, mock_network):
        """Test simulator properties."""
        simulator = ICOMSimulator(
            network=mock_network,
            name="test_simulator",
            start_year=2020,
            n_years=3
        )
        
        assert simulator.start_year == 2020
        assert simulator.n_years == 3
        assert simulator.name == "test_simulator"
        assert simulator.scenario == "default"
        assert simulator.intervention == "default" 