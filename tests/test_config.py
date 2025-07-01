"""
Tests for configuration management in chance_c.
"""
import pytest
import tempfile
import os
import yaml
from unittest.mock import patch, mock_open

from chance_c import SimulationConfig


class TestSimulationConfig:
    """Test cases for SimulationConfig class."""
    
    def test_basic_initialization(self):
        """Test basic SimulationConfig initialization."""
        config = SimulationConfig(
            simulation_name="test_simulation",
            start_year=2020,
            n_years=3
        )
        
        assert config.simulation_name == "test_simulation"
        assert config.start_year == 2020
        assert config.n_years == 3
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = SimulationConfig()
        
        assert config.simulation_name == "ABM_Baltimore_example"
        assert config.start_year == 2018
        assert config.n_years == 2
        assert config.agent_housing_aggregation == 10
        assert config.household_size == 2.7
    
    def test_custom_values(self):
        """Test setting custom values."""
        config = SimulationConfig(
            simulation_name="custom_sim",
            scenario="test_scenario",
            start_year=2025,
            n_years=5,
            agent_housing_aggregation=20,
            household_size=3.0
        )
        
        assert config.simulation_name == "custom_sim"
        assert config.scenario == "test_scenario"
        assert config.start_year == 2025
        assert config.n_years == 5
        assert config.agent_housing_aggregation == 20
        assert config.household_size == 3.0
    
    def test_field_mappings_initialization(self):
        """Test that field mappings are initialized correctly."""
        config = SimulationConfig()
        
        assert config.geo_file_mapping is not None
        assert config.pop_file_mapping is not None
        assert config.flood_file_mapping is not None
        assert config.housing_file_mapping is not None
        assert config.hedonic_file_mapping is not None
    
    def test_file_paths_initialization(self):
        """Test that file paths are set correctly."""
        config = SimulationConfig()
        
        assert config.geo_filename != ""
        assert config.pop_filename != ""
        assert config.flood_filename != ""
        assert config.housing_filename != ""
        assert config.hedonic_filename != ""
    
    def test_get_field_mapper(self):
        """Test getting a FieldMapper instance."""
        config = SimulationConfig()
        mapper = config.get_field_mapper()
        
        assert mapper is not None
        assert hasattr(mapper, 'mappings')
    
    def test_validate_field_mapping(self):
        """Test field mapping validation."""
        config = SimulationConfig()
        is_valid = config.validate_field_mapping()
        
        assert isinstance(is_valid, bool)
    
    def test_get_required_columns(self):
        """Test getting required columns for different file types."""
        config = SimulationConfig()
        
        geo_columns = config.get_required_columns('geo')
        pop_columns = config.get_required_columns('pop')
        
        assert isinstance(geo_columns, dict)
        assert isinstance(pop_columns, dict)
        assert len(geo_columns) > 0
        assert len(pop_columns) > 0
    
    def test_get_population_field_name(self):
        """Test getting population field name."""
        config = SimulationConfig()
        field_name = config.get_population_field_name()
        
        assert field_name == "AJWME001"
    
    def test_from_yaml(self):
        """Test loading configuration from YAML file."""
        yaml_content = """
simulation_name: yaml_test
scenario: test_scenario
start_year: 2020
n_years: 3
agent_housing_aggregation: 15
household_size: 2.8
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name
        
        try:
            config = SimulationConfig.from_yaml(yaml_path)
            
            assert config.simulation_name == "yaml_test"
            assert config.scenario == "test_scenario"
            assert config.start_year == 2020
            assert config.n_years == 3
            assert config.agent_housing_aggregation == 15
            assert config.household_size == 2.8
        finally:
            os.unlink(yaml_path)
    
    def test_to_yaml(self):
        """Test saving configuration to YAML file."""
        config = SimulationConfig(
            simulation_name="save_test",
            start_year=2020,
            n_years=3
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml_path = f.name
        
        try:
            config.to_yaml(yaml_path)
            
            # Verify the file was created and contains expected content
            assert os.path.exists(yaml_path)
            
            with open(yaml_path, 'r') as f:
                saved_content = yaml.safe_load(f)
            
            assert saved_content['simulation_name'] == "save_test"
            assert saved_content['start_year'] == 2020
            assert saved_content['n_years'] == 3
        finally:
            os.unlink(yaml_path)
    
    def test_yaml_roundtrip(self):
        """Test saving and loading configuration preserves all values."""
        original_config = SimulationConfig(
            simulation_name="roundtrip_test",
            scenario="test_scenario",
            start_year=2020,
            n_years=3,
            agent_housing_aggregation=15,
            household_size=2.8
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml_path = f.name
        
        try:
            original_config.to_yaml(yaml_path)
            loaded_config = SimulationConfig.from_yaml(yaml_path)
            
            assert loaded_config.simulation_name == original_config.simulation_name
            assert loaded_config.scenario == original_config.scenario
            assert loaded_config.start_year == original_config.start_year
            assert loaded_config.n_years == original_config.n_years
            assert loaded_config.agent_housing_aggregation == original_config.agent_housing_aggregation
            assert loaded_config.household_size == original_config.household_size
        finally:
            os.unlink(yaml_path)
    
    def test_invalid_yaml_file(self):
        """Test handling of invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            yaml_path = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                SimulationConfig.from_yaml(yaml_path)
        finally:
            os.unlink(yaml_path)
    
    def test_nonexistent_yaml_file(self):
        """Test handling of nonexistent YAML file."""
        with pytest.raises(FileNotFoundError):
            SimulationConfig.from_yaml("nonexistent_file.yml")
    
    def test_complex_parameters(self):
        """Test complex parameter types."""
        config = SimulationConfig(
            simple_anova_coefficients=(-100000, 200000, 150000, 100000, 120000, -400000)
        )
        
        assert len(config.simple_anova_coefficients) == 6
        assert config.simple_anova_coefficients[0] == -100000
    
    def test_string_representation(self):
        """Test string representation of config."""
        config = SimulationConfig(simulation_name="test")
        
        str_repr = str(config)
        assert "test" in str_repr
        assert "SimulationConfig" in str_repr
    
    def test_repr_representation(self):
        """Test repr representation of config."""
        config = SimulationConfig(simulation_name="test")
        
        repr_str = repr(config)
        assert "test" in repr_str
        assert "SimulationConfig" in repr_str 