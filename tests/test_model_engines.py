"""
Tests for model engines in chance_c.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

from chance_c import (
    NewAgentCreation, ExistingAgentReloSampler, NewAgentLocation,
    HousingMarket, BuildingDevelopment, HousingPricing, LandscapeStatistics,
    RealEstatePrices, FloodHazard, Zoning, FloodGenerator
)


class TestAgentCreationEngine:
    """Test cases for NewAgentCreation engine."""
    
    def test_engine_initialization(self, mock_network):
        """Test NewAgentCreation initialization."""
        engine = NewAgentCreation(
            target=mock_network,
            growth_mode="perc",
            growth_rate=0.01,
            inc_growth_mode="random_agent_replication",
            pop_growth_inc_perc=0.90
        )
        
        assert engine.target == mock_network
        assert engine.growth_mode == "perc"
        assert engine.growth_rate == 0.01
        assert engine.inc_growth_mode == "random_agent_replication"
        assert engine.pop_growth_inc_perc == 0.90
    
    def test_engine_run_method(self, mock_network, mock_timestep):
        """Test NewAgentCreation run method."""
        engine = NewAgentCreation(
            target=mock_network,
            growth_mode="perc",
            growth_rate=0.01,
            inc_growth_mode="random_agent_replication",
            pop_growth_inc_perc=0.90
        )
        
        # Mock network properties
        mock_network.total_population = 10000
        mock_network.housing_block_group_df = pd.DataFrame({
            'average_income': [50000, 60000, 70000]
        })
        
        # Mock institution with components
        mock_institution = Mock()
        mock_institution.components = [Mock(), Mock(), Mock()]  # Add some mock agents
        mock_network.get_institution = Mock(return_value=mock_institution)
        mock_network.components = []
        mock_network.unassigned_households = {}
        
        # Mock timestep
        engine.timestep = mock_timestep
        
        # Mock the agent creation to avoid income calculation issues
        with patch('chance_c.model_engines.agent_creation.HouseholdAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            
            # Mock add_component to properly track components
            def mock_add_component(agent):
                mock_network.components.append(agent)
            mock_network.add_component = mock_add_component
            
            # Test run method
            engine.run()
            
            # Verify that agents were created
            assert len(mock_network.components) > 0
    
    def test_agent_creation_logic(self, mock_network, mock_timestep):
        """Test agent creation logic."""
        engine = NewAgentCreation(
            target=mock_network,
            growth_mode="perc",
            growth_rate=0.01,
            inc_growth_mode="random_agent_replication",
            pop_growth_inc_perc=0.90
        )
        
        # Mock network properties
        mock_network.total_population = 10000
        mock_network.housing_block_group_df = pd.DataFrame({
            'average_income': [50000, 60000, 70000]
        })
        
        # Mock institution with components
        mock_institution = Mock()
        mock_institution.components = [Mock(), Mock(), Mock()]  # Add some mock agents
        mock_network.get_institution = Mock(return_value=mock_institution)
        mock_network.components = []
        mock_network.unassigned_households = {}
        
        # Mock timestep
        engine.timestep = mock_timestep
        
        # Mock the agent creation to avoid income calculation issues
        with patch('chance_c.model_engines.agent_creation.HouseholdAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            
            # Mock add_component to properly track components
            def mock_add_component(agent):
                mock_network.components.append(agent)
            mock_network.add_component = mock_add_component
            
            # Test different growth modes
            engine.growth_mode = "perc"
            engine.run()
            
            # Verify that agents were created
            assert len(mock_network.components) > 0
    
    def test_engine_validation(self):
        """Test engine parameter validation."""
        # Test with None target
        with pytest.raises(TypeError):
            NewAgentCreation(None)


class TestAgentRelocationEngine:
    """Test cases for ExistingAgentReloSampler engine."""
    
    def test_engine_initialization(self, mock_network):
        """Test ExistingAgentReloSampler initialization."""
        engine = ExistingAgentReloSampler(mock_network)
        
        assert engine.target == mock_network
    
    def test_engine_run_method(self, mock_network, mock_timestep):
        """Test ExistingAgentReloSampler run method."""
        engine = ExistingAgentReloSampler(mock_network)
        
        # Mock network properties
        mock_network.get_institution = Mock(return_value=Mock())
        
        # Test run method
        engine.run()
        
        # Verify that the engine ran without errors
        assert engine is not None


class TestAgentLocationEngine:
    """Test cases for NewAgentLocation engine."""
    
    def test_engine_initialization(self, mock_network):
        """Test NewAgentLocation initialization."""
        engine = NewAgentLocation(mock_network)
        
        assert engine.target == mock_network
        assert hasattr(engine, 'house_choice_mode')
        assert hasattr(engine, 'simple_anova_coefficients')
    
    def test_engine_run_method(self, mock_network, mock_timestep):
        """Test NewAgentLocation run method."""
        # Create engine with proper coefficients
        engine = NewAgentLocation(
            mock_network,
            simple_anova_coefficients=np.array([-121428, 294707, 130553, 128990, 154887, -500000], dtype=np.float64)
        )
        
        # Mock network properties with required data
        mock_network.unassigned_households = {
            'agent1': Mock(),
            'agent2': Mock()
        }
        
        # Mock housing block group dataframe with required columns
        mock_network.housing_block_group_df = pd.DataFrame({
            'GEOID': ['bg_001', 'bg_002'],
            'new_price': [200000, 250000],
            'perc_fld_area': [0.05, 0.15],
            'available_units': [10, 15],
            'N_MeanSqfeet': [1500, 1800],
            'N_MeanAge': [20, 25],
            'N_MeanNoOfStories': [2, 2],
            'N_MeanFullBathNumber': [2, 2],
            'residuals': [0, 0],
            'utility': [0.8, 0.6]  # Add utility column
        })
        
        # Mock agents with required attributes
        for agent in mock_network.unassigned_households.values():
            agent.house_budget = 300000
            agent.avoidance = False
            agent.name = 'test_agent'
        
        # Mock timestep
        engine.timestep = mock_timestep
        
        # Test run method
        engine.run()
        
        # Verify that the engine ran without errors
        assert engine is not None


class TestHousingMarketEngine:
    """Test cases for HousingMarket engine."""
    
    def test_engine_initialization(self, mock_network):
        """Test HousingMarket initialization."""
        engine = HousingMarket(mock_network)
        
        assert engine.target == mock_network
    
    def test_engine_run_method(self, mock_network, mock_timestep):
        """Test HousingMarket run method."""
        engine = HousingMarket(mock_network)
        
        # Mock network properties
        mock_network.nodes = []
        mock_network.unassigned_households = {}  # Empty dict instead of Mock
        mock_network.relocating_households = {}  # Empty dict instead of Mock
        
        # Mock timestep
        engine.timestep = mock_timestep
        
        # Test run method
        engine.run()
        
        # Verify that the engine ran without errors
        assert engine is not None


class TestBuildingDevelopmentEngine:
    """Test cases for BuildingDevelopment engine."""
    
    def test_engine_initialization(self, mock_network):
        """Test BuildingDevelopment initialization."""
        engine = BuildingDevelopment(mock_network)
        
        assert engine.target == mock_network
    
    def test_engine_run_method(self, mock_network, mock_timestep):
        """Test BuildingDevelopment run method."""
        engine = BuildingDevelopment(mock_network)
        
        # Mock network properties
        mock_network.nodes = []
        
        # Mock timestep
        engine.timestep = mock_timestep
        
        # Test run method
        engine.run()
        
        # Verify that the engine ran without errors
        assert engine is not None


class TestHousingPricingEngine:
    """Test cases for HousingPricing engine."""
    
    def test_engine_initialization(self, mock_network):
        """Test HousingPricing initialization."""
        engine = HousingPricing(mock_network)
        
        assert engine.target == mock_network
    
    def test_engine_run_method(self, mock_network, mock_timestep):
        """Test HousingPricing run method."""
        engine = HousingPricing(mock_network)
        
        # Mock network properties
        mock_network.nodes = []
        
        # Mock timestep
        engine.timestep = mock_timestep
        
        # Test run method
        engine.run()
        
        # Verify that the engine ran without errors
        assert engine is not None


class TestLandscapeStatisticsEngine:
    """Test cases for LandscapeStatistics engine."""
    
    def test_engine_initialization(self, mock_network):
        """Test LandscapeStatistics initialization."""
        engine = LandscapeStatistics(mock_network)
        
        assert engine.target == mock_network
    
    def test_engine_run_method(self, mock_network, mock_timestep):
        """Test LandscapeStatistics run method."""
        engine = LandscapeStatistics(mock_network)
        
        # Mock network properties with some data
        mock_agent1 = Mock()
        mock_agent1.household_size = 2.5
        mock_agent1.income = 50000
        mock_agent1.no_households_per_agent = 10
        
        mock_agent2 = Mock()
        mock_agent2.household_size = 3.0
        mock_agent2.income = 60000
        mock_agent2.no_households_per_agent = 10
        
        mock_agent3 = Mock()
        mock_agent3.household_size = 2.0
        mock_agent3.income = 45000
        mock_agent3.no_households_per_agent = 10
        
        mock_node1 = Mock()
        mock_node1.household_agents = {'agent1': mock_agent1, 'agent2': mock_agent2}
        mock_node1.avg_hh_income = 50000
        mock_node1.name = 'bg_001'
        mock_node1.area = 1000.0
        
        mock_node2 = Mock()
        mock_node2.household_agents = {'agent3': mock_agent3}
        mock_node2.avg_hh_income = 60000
        mock_node2.name = 'bg_002'
        mock_node2.area = 800.0
        
        mock_network.nodes = [mock_node1, mock_node2]
        mock_network.total_population = 0  # Will be calculated by engine
        mock_network.housing_block_group_df = pd.DataFrame({
            'GEOID': ['bg_001', 'bg_002'],
            'hhsize1990': [2.5, 2.0]
        })
        
        # Mock timestep
        engine.timestep = mock_timestep
        
        # Test run method
        engine.run()
        
        # Verify that the engine ran without errors
        assert engine is not None


class TestRealEstatePricesEngine:
    """Test cases for RealEstatePrices engine."""
    
    def test_engine_initialization(self, mock_network):
        """Test RealEstatePrices initialization."""
        engine = RealEstatePrices(mock_network)
        
        assert engine.target == mock_network
    
    def test_engine_run_method(self, mock_network, mock_timestep):
        """Test RealEstatePrices run method."""
        engine = RealEstatePrices(mock_network)
        
        # Mock network properties
        mock_network.nodes = []
        
        # Mock timestep
        engine.timestep = mock_timestep
        
        # Test run method
        engine.run()
        
        # Verify that the engine ran without errors
        assert engine is not None


class TestFloodHazardEngine:
    """Test cases for FloodHazard engine."""
    
    def test_engine_initialization(self, mock_network):
        """Test FloodHazard initialization."""
        engine = FloodHazard(mock_network)
        
        assert engine.target == mock_network
    
    def test_engine_run_method(self, mock_network, mock_timestep):
        """Test FloodHazard run method."""
        engine = FloodHazard(mock_network)
        
        # Mock network properties
        mock_network.nodes = []
        
        # Mock timestep
        engine.timestep = mock_timestep
        
        # Test run method
        engine.run()
        
        # Verify that the engine ran without errors
        assert engine is not None


class TestZoningEngine:
    """Test cases for Zoning engine."""
    
    def test_engine_initialization(self, mock_network):
        """Test Zoning initialization."""
        engine = Zoning(mock_network)
        
        assert engine.target == mock_network
    
    def test_engine_run_method(self, mock_network, mock_timestep):
        """Test Zoning run method."""
        engine = Zoning(mock_network)
        
        # Mock network properties
        mock_network.nodes = []
        
        # Mock timestep
        engine.timestep = mock_timestep
        
        # Test run method
        engine.run()
        
        # Verify that the engine ran without errors
        assert engine is not None


class TestFloodGenerator:
    """Test cases for FloodGenerator engine."""
    
    def test_generator_initialization(self):
        """Test FloodGenerator initialization."""
        mock_target = Mock()
        generator = FloodGenerator(target=mock_target)
        
        assert generator.target == mock_target
    
    def test_flood_generation(self):
        """Test flood generation logic."""
        mock_target = Mock()
        generator = FloodGenerator(target=mock_target)
        
        # Mock nodes with required attributes
        mock_node1 = Mock()
        mock_node1.perc_fld_area = 0.05
        
        mock_node2 = Mock()
        mock_node2.perc_fld_area = 0.15
        
        mock_target.nodes = [mock_node1, mock_node2]
        
        # Mock timestep
        generator.timestep = Mock()
        generator.timestep.year = 2020
        
        # Test run method
        generator.run()
        
        # Verify that the generator ran without errors
        assert generator is not None


class TestEngineIntegration:
    """Test cases for engine integration and interaction."""
    
    def test_engine_compatibility(self, mock_network):
        """Test that engines are compatible with each other."""
        # Test that different engines can be created with the same network
        agent_creation = NewAgentCreation(
            target=mock_network,
            growth_mode="perc",
            growth_rate=0.01,
            inc_growth_mode="random_agent_replication",
            pop_growth_inc_perc=0.90
        )
        
        agent_location = NewAgentLocation(mock_network)
        housing_market = HousingMarket(mock_network)
        building_dev = BuildingDevelopment(mock_network)
        
        # Verify all engines can be created
        assert agent_creation is not None
        assert agent_location is not None
        assert housing_market is not None
        assert building_dev is not None
    
    def test_engine_attributes(self, mock_network):
        """Test that engines have expected attributes."""
        engine = NewAgentCreation(
            target=mock_network,
            growth_mode="perc",
            growth_rate=0.01,
            inc_growth_mode="random_agent_replication",
            pop_growth_inc_perc=0.90
        )
        
        # Test that engine has required attributes
        assert hasattr(engine, 'target')
        assert hasattr(engine, 'growth_mode')
        assert hasattr(engine, 'growth_rate')
        assert hasattr(engine, 'inc_growth_mode')
        assert hasattr(engine, 'run') 