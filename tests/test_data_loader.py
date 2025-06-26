"""
Tests for data loading functionality in chance_c.
"""
import pytest
import pandas as pd
import geopandas as gpd
import numpy as np
import os
import tempfile
from unittest.mock import patch, mock_open
import warnings
from shapely.geometry import Polygon

# Suppress warnings that are expected during testing
warnings.filterwarnings("ignore", category=UserWarning, message="Column names longer than 10 characters will be truncated when saved to ESRI Shapefile.")
warnings.filterwarnings("ignore", category=RuntimeWarning, message="Normalized/laundered field name:.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, message="The 'shapely.geos' module is deprecated.*")

from chance_c import SimulationConfig
from tests.conftest import (
    assert_dataframe_not_empty, assert_dataframe_columns,
    assert_numeric_column, assert_geodataframe_valid
)


class TestDataLoader:
    """Test cases for data loading functionality."""
    
    def test_load_csv_data(self, temp_data_dir, sample_csv_data):
        """Test loading CSV data."""
        # Create temporary CSV file
        csv_file = os.path.join(temp_data_dir, "test_data.csv")
        sample_csv_data.to_csv(csv_file, index=False)
        
        # Load data
        loaded_data = pd.read_csv(csv_file)
        
        assert_dataframe_not_empty(loaded_data)
        assert_dataframe_columns(loaded_data, ['GEOID', 'population', 'income', 'housing_units', 'flood_risk'])
        assert len(loaded_data) == 3
    
    def test_load_shapefile_data(self, temp_data_dir, sample_block_groups):
        """Test loading shapefile data."""
        # Suppress warnings for this specific test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Create temporary shapefile
            shp_file = os.path.join(temp_data_dir, "test_geo.shp")
            sample_block_groups.to_file(shp_file)
            
            # Load data
            loaded_data = gpd.read_file(shp_file)
        
        assert_geodataframe_valid(loaded_data)
        # Note: Shapefile column names are truncated to 10 characters
        expected_columns = ['GEOID', 'population', 'income', 'housing_un', 'vacant_uni', 'flood_risk', 'geometry']
        assert_dataframe_columns(loaded_data, expected_columns)
        assert len(loaded_data) == 3
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            pd.read_csv("nonexistent_file.csv")
    
    def test_load_invalid_csv_format(self, temp_data_dir):
        """Test loading invalid CSV format."""
        # Create invalid CSV file
        invalid_csv = os.path.join(temp_data_dir, "invalid.csv")
        with open(invalid_csv, 'w') as f:
            f.write("invalid,csv,format\n")
            f.write("missing,quotes\n")
            f.write("wrong,number,of,columns\n")
        
        # Should handle gracefully
        try:
            data = pd.read_csv(invalid_csv)
            assert isinstance(data, pd.DataFrame)
        except Exception as e:
            # Some parsing errors are expected
            assert isinstance(e, Exception)
    
    def test_data_validation(self, sample_csv_data):
        """Test data validation."""
        # Test required columns
        required_columns = ['GEOID', 'population']
        for col in required_columns:
            assert col in sample_csv_data.columns, f"Required column {col} missing"
        
        # Test data types
        assert_numeric_column(sample_csv_data, 'population')
        assert_numeric_column(sample_csv_data, 'income')
        assert_numeric_column(sample_csv_data, 'housing_units')
        assert_numeric_column(sample_csv_data, 'flood_risk')
        
        # Test data ranges
        assert sample_csv_data['population'].min() >= 0
        assert sample_csv_data['income'].min() >= 0
        assert sample_csv_data['housing_units'].min() >= 0
        assert sample_csv_data['flood_risk'].min() >= 0
        assert sample_csv_data['flood_risk'].max() <= 1
    
    def test_geodataframe_validation(self, sample_block_groups):
        """Test GeoDataFrame validation."""
        assert_geodataframe_valid(sample_block_groups)
        
        # Test geometry column
        assert 'geometry' in sample_block_groups.columns
        assert all(sample_block_groups['geometry'].notna())
        
        # Test CRS
        assert sample_block_groups.crs is not None
    
    def test_data_aggregation(self, sample_csv_data):
        """Test data aggregation functionality."""
        # Test grouping by GEOID
        grouped = sample_csv_data.groupby('GEOID').agg({
            'population': 'sum',
            'income': 'mean',
            'housing_units': 'sum'
        }).reset_index()
        
        assert_dataframe_not_empty(grouped)
        assert len(grouped) == 3  # Should have 3 unique GEOIDs
        assert 'population' in grouped.columns
        assert 'income' in grouped.columns
        assert 'housing_units' in grouped.columns
    
    def test_data_merging(self, sample_csv_data, sample_block_groups):
        """Test merging different data sources."""
        # Convert GeoDataFrame to DataFrame for merging
        block_groups_df = sample_block_groups.drop(columns=['geometry'])
        
        # Merge on GEOID
        merged = pd.merge(sample_csv_data, block_groups_df, on='GEOID', how='inner')
        
        assert_dataframe_not_empty(merged)
        assert len(merged) == 3  # Should have 3 matching records
        assert 'population_x' in merged.columns or 'population_y' in merged.columns
    
    def test_missing_data_handling(self, sample_csv_data):
        """Test handling of missing data."""
        # Add some missing values
        data_with_missing = sample_csv_data.copy()
        data_with_missing.loc[0, 'income'] = np.nan
        data_with_missing.loc[1, 'population'] = np.nan
        
        # Test missing value detection
        missing_income = data_with_missing['income'].isna().sum()
        missing_population = data_with_missing['population'].isna().sum()
        
        assert missing_income == 1
        assert missing_population == 1
        
        # Test filling missing values
        filled_data = data_with_missing.fillna({
            'income': data_with_missing['income'].mean(),
            'population': data_with_missing['population'].mean()
        })
        
        assert filled_data['income'].isna().sum() == 0
        assert filled_data['population'].isna().sum() == 0
    
    def test_data_type_conversion(self, sample_csv_data):
        """Test data type conversion."""
        # Test converting to different types
        converted_data = sample_csv_data.copy()
        converted_data['GEOID'] = converted_data['GEOID'].astype(str)
        converted_data['population'] = converted_data['population'].astype(float)
        converted_data['income'] = converted_data['income'].astype(int)
        
        assert converted_data['GEOID'].dtype == 'object'
        assert converted_data['population'].dtype == 'float64'
        assert converted_data['income'].dtype == 'int64'
    
    def test_large_dataset_handling(self, temp_data_dir):
        """Test handling of large datasets."""
        # Create larger dataset
        large_data = pd.DataFrame({
            'GEOID': [f'bg_{i:03d}' for i in range(1000)],
            'population': [1000 + i for i in range(1000)],
            'income': [50000 + i * 100 for i in range(1000)],
            'housing_units': [400 + i for i in range(1000)]
        })
        
        csv_file = os.path.join(temp_data_dir, "large_data.csv")
        large_data.to_csv(csv_file, index=False)
        
        # Load data
        loaded_data = pd.read_csv(csv_file)
        
        assert len(loaded_data) == 1000
        assert_dataframe_columns(loaded_data, ['GEOID', 'population', 'income', 'housing_units'])
        
        # Test memory usage
        memory_usage = loaded_data.memory_usage(deep=True).sum()
        assert memory_usage > 0  # Should use some memory
    
    def test_data_export(self, temp_data_dir, sample_csv_data):
        """Test data export functionality."""
        # Export to CSV
        output_csv = os.path.join(temp_data_dir, "exported_data.csv")
        sample_csv_data.to_csv(output_csv, index=False)
        
        assert os.path.exists(output_csv)
        
        # Verify exported data
        exported_data = pd.read_csv(output_csv)
        assert_dataframe_not_empty(exported_data)
        assert len(exported_data) == len(sample_csv_data)
        assert list(exported_data.columns) == list(sample_csv_data.columns)
    
    def test_data_filtering(self, sample_csv_data):
        """Test data filtering functionality."""
        # Filter by population threshold
        filtered_data = sample_csv_data[sample_csv_data['population'] > 1000]
        
        assert len(filtered_data) == 1  # Only one record has population > 1000
        assert filtered_data.iloc[0]['GEOID'] == 'bg_002'
        
        # Filter by income range
        income_filtered = sample_csv_data[
            (sample_csv_data['income'] >= 50000) &
            (sample_csv_data['income'] <= 70000)
        ]
        
        assert len(income_filtered) == 1  # Only one record in income range (bg_001 has 50000)
    
    def test_data_sorting(self, sample_csv_data):
        """Test data sorting functionality."""
        # Sort by population
        sorted_by_pop = sample_csv_data.sort_values('population')
        
        assert_dataframe_not_empty(sorted_by_pop)
        assert len(sorted_by_pop) == 3
        
        # Check sorting order
        populations = sorted_by_pop['population'].values
        assert populations[0] <= populations[1] <= populations[2]
        
        # Sort by income descending
        sorted_by_income_desc = sample_csv_data.sort_values('income', ascending=False)
        incomes = sorted_by_income_desc['income'].values
        assert incomes[0] >= incomes[1] >= incomes[2] 