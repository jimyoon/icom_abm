"""
Tests for field mapping functionality in chance_c.
"""
import pytest
import tempfile
import os
import yaml
import pandas as pd
from unittest.mock import patch, mock_open

from chance_c import FieldMapper


class TestFieldMapper:
    """Test cases for FieldMapper class."""
    
    def test_default_initialization(self):
        """Test FieldMapper initialization with default values."""
        mapper = FieldMapper()
        
        # Check that mapper is initialized
        assert mapper is not None
        assert hasattr(mapper, 'mappings')
        assert isinstance(mapper.mappings, dict)
    
    def test_custom_initialization(self, sample_field_mapping):
        """Test FieldMapper initialization with custom mapping."""
        # Create mappings dict with the expected structure
        mappings = {
            'geo_file_mapping': sample_field_mapping,
            'pop_file_mapping': {'population': 'pop'},
            'flood_file_mapping': {'flood_risk': 'flood'},
            'housing_file_mapping': {'housing_units': 'housing'},
            'hedonic_file_mapping': {'income': 'inc'}
        }
        
        mapper = FieldMapper(mappings=mappings)
        
        assert mapper.mappings == mappings
        assert 'geo_file_mapping' in mapper.mappings
        assert 'pop_file_mapping' in mapper.mappings
    
    def test_from_yaml_file(self, temp_data_dir, sample_field_mapping):
        """Test loading field mapping from YAML file."""
        # Create mappings dict with the expected structure
        mappings = {
            'geo_file_mapping': sample_field_mapping,
            'pop_file_mapping': {'population': 'pop'},
            'flood_file_mapping': {'flood_risk': 'flood'},
            'housing_file_mapping': {'housing_units': 'housing'},
            'hedonic_file_mapping': {'income': 'inc'}
        }
        
        # Create temporary YAML file
        yaml_file = os.path.join(temp_data_dir, "field_mapping.yml")
        with open(yaml_file, 'w') as f:
            yaml.dump(mappings, f)
        
        mapper = FieldMapper(mapping_file=yaml_file)
        
        assert mapper.mappings == mappings
        assert 'geo_file_mapping' in mapper.mappings
    
    def test_from_yaml_file_not_found(self):
        """Test loading field mapping from non-existent YAML file."""
        mapper = FieldMapper(mapping_file="nonexistent_file.yml")
        
        # Should use default mappings when file not found
        assert mapper.mappings is not None
        assert 'geo_file_mapping' in mapper.mappings
    
    def test_map_columns_with_missing(self, sample_field_mapping):
        """Test mapping columns with missing source columns."""
        # Create mappings dict with the expected structure
        mappings = {
            'geo_file_mapping': sample_field_mapping,
            'pop_file_mapping': {'population': 'pop'},
            'flood_file_mapping': {'flood_risk': 'flood'},
            'housing_file_mapping': {'housing_units': 'housing'},
            'hedonic_file_mapping': {'income': 'inc'}
        }
        
        mapper = FieldMapper(mappings=mappings)
        
        # Create test DataFrame with missing columns
        df = pd.DataFrame({
            'population': [1000, 1500, 800],
            'income': [50000, 75000, 45000]
            # Missing housing_units, flood_risk, geometry
        })
        
        # Should raise ValueError for missing columns
        with pytest.raises(ValueError):
            mapper.map_dataframe(df, 'geo')
    
    def test_validate_mapping(self, sample_field_mapping):
        """Test mapping validation."""
        # Create mappings dict with the expected structure
        mappings = {
            'geo_file_mapping': sample_field_mapping,
            'pop_file_mapping': {'population': 'pop'},
            'flood_file_mapping': {'flood_risk': 'flood'},
            'housing_file_mapping': {'housing_units': 'housing'},
            'hedonic_file_mapping': {'income': 'inc'}
        }
        
        mapper = FieldMapper(mappings=mappings)
        
        # Validate mapping
        is_valid = mapper.validate_mappings()
        
        assert isinstance(is_valid, bool)
    
    def test_mapping_equality(self, sample_field_mapping):
        """Test mapping equality comparison."""
        # Create mappings dict with the expected structure
        mappings1 = {
            'geo_file_mapping': sample_field_mapping,
            'pop_file_mapping': {'population': 'pop'},
            'flood_file_mapping': {'flood_risk': 'flood'},
            'housing_file_mapping': {'housing_units': 'housing'},
            'hedonic_file_mapping': {'income': 'inc'}
        }
        
        mappings2 = {
            'geo_file_mapping': sample_field_mapping,
            'pop_file_mapping': {'population': 'pop'},
            'flood_file_mapping': {'flood_risk': 'flood'},
            'housing_file_mapping': {'housing_units': 'housing'},
            'hedonic_file_mapping': {'income': 'inc'}
        }
        
        mapper1 = FieldMapper(mappings=mappings1)
        mapper2 = FieldMapper(mappings=mappings2)
        
        # Should be equal if mappings are the same
        assert mapper1.mappings == mapper2.mappings
    
    def test_mapping_copy(self, sample_field_mapping):
        """Test creating a copy of mapping."""
        # Create mappings dict with the expected structure
        mappings = {
            'geo_file_mapping': sample_field_mapping,
            'pop_file_mapping': {'population': 'pop'},
            'flood_file_mapping': {'flood_risk': 'flood'},
            'housing_file_mapping': {'housing_units': 'housing'},
            'hedonic_file_mapping': {'income': 'inc'}
        }
        
        original = FieldMapper(mappings=mappings)
        
        # Create copy
        copy = FieldMapper(mappings=original.mappings.copy())
        
        assert copy.mappings == original.mappings
        assert copy.mappings is not original.mappings  # Should be different objects
    
    def test_mapping_merge(self, sample_field_mapping):
        """Test merging field mappings."""
        # Create mappings dict with the expected structure
        mappings1 = {
            'geo_file_mapping': sample_field_mapping,
            'pop_file_mapping': {'population': 'pop'}
        }
        
        mappings2 = {
            'flood_file_mapping': {'flood_risk': 'flood'},
            'housing_file_mapping': {'housing_units': 'housing'}
        }
        
        mapper1 = FieldMapper(mappings=mappings1)
        mapper2 = FieldMapper(mappings=mappings2)
        
        # Merge mappings
        merged_mappings = {**mapper1.mappings, **mapper2.mappings}
        merged_mapper = FieldMapper(mappings=merged_mappings)
        
        assert 'geo_file_mapping' in merged_mapper.mappings
        assert 'flood_file_mapping' in merged_mapper.mappings
        assert len(merged_mapper.mappings) == 4
    
    def test_mapping_filter(self, sample_field_mapping):
        """Test filtering field mappings."""
        # Create mappings dict with the expected structure
        mappings = {
            'geo_file_mapping': sample_field_mapping,
            'pop_file_mapping': {'population': 'pop'},
            'flood_file_mapping': {'flood_risk': 'flood'},
            'housing_file_mapping': {'housing_units': 'housing'},
            'hedonic_file_mapping': {'income': 'inc'}
        }
        
        mapper = FieldMapper(mappings=mappings)
        
        # Filter mappings to only include geo and pop
        filtered_mappings = {
            k: v for k, v in mapper.mappings.items() 
            if k in ['geo_file_mapping', 'pop_file_mapping']
        }
        
        filtered_mapper = FieldMapper(mappings=filtered_mappings)
        
        assert 'geo_file_mapping' in filtered_mapper.mappings
        assert 'pop_file_mapping' in filtered_mapper.mappings
        assert 'flood_file_mapping' not in filtered_mapper.mappings
        assert len(filtered_mapper.mappings) == 2
    
    def test_mapping_keys_values(self, sample_field_mapping):
        """Test accessing mapping keys and values."""
        # Create mappings dict with the expected structure
        mappings = {
            'geo_file_mapping': sample_field_mapping,
            'pop_file_mapping': {'population': 'pop'},
            'flood_file_mapping': {'flood_risk': 'flood'},
            'housing_file_mapping': {'housing_units': 'housing'},
            'hedonic_file_mapping': {'income': 'inc'}
        }
        
        mapper = FieldMapper(mappings=mappings)
        
        # Test accessing keys and values
        keys = list(mapper.mappings.keys())
        assert 'geo_file_mapping' in keys
        assert 'pop_file_mapping' in keys
        assert len(keys) == 5
        
        geo_values = mapper.mappings['geo_file_mapping']
        assert 'population' in geo_values
        assert 'income' in geo_values
        assert len(geo_values) == 5
    
    def test_get_required_columns(self, sample_field_mapping):
        """Test getting required columns for different file types."""
        # Create mappings dict with the expected structure
        mappings = {
            'geo_file_mapping': sample_field_mapping,
            'pop_file_mapping': {'population': 'pop'},
            'flood_file_mapping': {'flood_risk': 'flood'},
            'housing_file_mapping': {'housing_units': 'housing'},
            'hedonic_file_mapping': {'income': 'inc'}
        }
        
        mapper = FieldMapper(mappings=mappings)
        
        # Test getting required columns
        geo_columns = mapper.get_required_columns('geo')
        pop_columns = mapper.get_required_columns('pop')
        
        assert isinstance(geo_columns, dict)
        assert isinstance(pop_columns, dict)
        assert len(geo_columns) > 0
        assert len(pop_columns) > 0
    
    def test_validate_mapping_file(self, temp_data_dir, sample_field_mapping):
        """Test mapping file validation."""
        # Create mappings dict with the expected structure
        mappings = {
            'geo_file_mapping': sample_field_mapping,
            'pop_file_mapping': {'population': 'pop'},
            'flood_file_mapping': {'flood_risk': 'flood'},
            'housing_file_mapping': {'housing_units': 'housing'},
            'hedonic_file_mapping': {'income': 'inc'}
        }
        
        # Create temporary YAML file
        yaml_file = os.path.join(temp_data_dir, "field_mapping.yml")
        with open(yaml_file, 'w') as f:
            yaml.dump(mappings, f)
        
        mapper = FieldMapper(mappings=mappings)
        
        # Test validation
        is_valid = mapper.validate_mapping_file(yaml_file)
        assert isinstance(is_valid, bool)
    
    def test_create_example_mapping_file(self, temp_data_dir):
        """Test creating example mapping file."""
        mapper = FieldMapper()
        
        # Create example file
        example_file = os.path.join(temp_data_dir, "example_mapping.yml")
        mapper.create_example_mapping_file(example_file)
        
        # Verify file was created
        assert os.path.exists(example_file)
        
        # Verify file contains valid YAML
        with open(example_file, 'r') as f:
            content = yaml.safe_load(f)
        
        assert isinstance(content, dict)
        assert 'geo_file_mapping' in content 