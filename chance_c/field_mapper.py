"""
Field mapping utilities for the CHANCE ABM model.

This module provides functionality to map user-defined column names in input files
to the required field names used by the model.
"""

import yaml
from typing import Dict, Optional, Any
import pandas as pd
import logging


class FieldMapper:
    """Handles mapping between user input file column names and required model field names."""
    
    def __init__(self, mapping_file: Optional[str] = None):
        """Initialize the FieldMapper.
        
        Args:
            mapping_file: Path to YAML file containing field mappings. 
                         If None, uses default mappings.
        """
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()
        
    def _load_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load field mappings from YAML file or use defaults.
        
        Returns:
            Dictionary containing field mappings for each file type.
        """
        if self.mapping_file:
            try:
                with open(self.mapping_file, 'r') as file:
                    return yaml.safe_load(file)
            except FileNotFoundError:
                logging.warning(f"Mapping file {self.mapping_file} not found. Using default mappings.")
                return self._get_default_mappings()
            except yaml.YAMLError as e:
                logging.error(f"Error parsing mapping file: {e}. Using default mappings.")
                return self._get_default_mappings()
        else:
            return self._get_default_mappings()
    
    def _get_default_mappings(self) -> Dict[str, Dict[str, str]]:
        """Get default field mappings.
        
        Returns:
            Dictionary containing default field mappings.
        """
        return {
            'geo_file_mapping': {
                'GISJOIN': 'GISJOIN',
                'GEOID': 'GEOID',
                'COUNTYFP': 'COUNTYFP',
                'TRACTCE': 'TRACTCE',
                'BLKGRPCE': 'BLKGRPCE',
                'ALAND': 'ALAND',
                'geometry': 'geometry'
            },
            'pop_file_mapping': {
                'GISJOIN': 'GISJOIN',
                'AJWME001': 'AJWME001'
            },
            'flood_file_mapping': {
                'GISJOIN': 'GISJOIN',
                'Shape_Area': 'Shape_Area',
                'fld_area': 'fld_area',
                'perc_fld_area': 'perc_fld_area'
            },
            'housing_file_mapping': {
                'GISJOIN': 'GISJOIN',
                'pop1990': 'pop1990',
                'mhi1990': 'mhi1990',
                'hhsize1990': 'hhsize1990',
                'coastdist': 'coastdist',
                'cbddist': 'cbddist',
                'hhtrans1993': 'hhtrans1993',
                'salesprice1993': 'salesprice1993',
                'salespricesf1993': 'salespricesf1993'
            },
            'hedonic_file_mapping': {
                'GISJOIN': 'GISJOIN',
                'N_MeanSqfeet': 'N_MeanSqfeet',
                'N_MeanAge': 'N_MeanAge',
                'N_MeanNoOfStories': 'N_MeanNoOfStories',
                'N_MeanFullBathNumber': 'N_MeanFullBathNumber',
                'N_perc_area_flood': 'N_perc_area_flood',
                'residuals': 'residuals'
            }
        }
    
    def map_dataframe(self, df: pd.DataFrame, file_type: str) -> pd.DataFrame:
        """Map column names in a dataframe to required field names.
        
        Args:
            df: Input dataframe with user-defined column names
            file_type: Type of file ('geo', 'pop', 'flood', 'housing', 'hedonic')
            
        Returns:
            Dataframe with mapped column names
            
        Raises:
            ValueError: If file_type is not recognized or required columns are missing
        """
        mapping_key = f"{file_type}_file_mapping"
        
        if mapping_key not in self.mappings:
            raise ValueError(f"Unknown file type: {file_type}")
        
        mapping = self.mappings[mapping_key]
        mapped_df = df.copy()
        
        # Check for missing required columns
        missing_columns = []
        for required_field, user_field in mapping.items():
            if user_field not in df.columns:
                missing_columns.append(f"{user_field} (maps to {required_field})")
        
        if missing_columns:
            raise ValueError(f"Missing required columns in {file_type} file: {', '.join(missing_columns)}")
        
        # Rename columns to required field names
        rename_dict = {user_field: required_field for required_field, user_field in mapping.items()}
        mapped_df = mapped_df.rename(columns=rename_dict)
        
        # Select only the required columns
        required_columns = list(mapping.keys())
        mapped_df = mapped_df[required_columns]
        
        return mapped_df
    
    def get_required_columns(self, file_type: str) -> Dict[str, str]:
        """Get the required columns for a specific file type.
        
        Args:
            file_type: Type of file ('geo', 'pop', 'flood', 'housing', 'hedonic')
            
        Returns:
            Dictionary mapping required field names to their descriptions
        """
        mapping_key = f"{file_type}_file_mapping"
        
        if mapping_key not in self.mappings:
            raise ValueError(f"Unknown file type: {file_type}")
        
        # Load metadata to get descriptions
        try:
            with open('data/input_file_metadata.yml', 'r') as file:
                metadata = yaml.safe_load(file)
        except FileNotFoundError:
            # Return basic info if metadata file not found
            return {field: f"Required field: {field}" for field in self.mappings[mapping_key].keys()}
        
        # Get descriptions from metadata
        metadata_key = f"{file_type}_file_metadata"
        if metadata_key in metadata:
            return metadata[metadata_key]
        else:
            return {field: f"Required field: {field}" for field in self.mappings[mapping_key].keys()}
    
    def validate_mapping_file(self, mapping_file: str) -> bool:
        """Validate a mapping file.
        
        Args:
            mapping_file: Path to the mapping file to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            with open(mapping_file, 'r') as file:
                mappings = yaml.safe_load(file)
            
            required_keys = [
                'geo_file_mapping', 'pop_file_mapping', 'flood_file_mapping',
                'housing_file_mapping', 'hedonic_file_mapping'
            ]
            
            for key in required_keys:
                if key not in mappings:
                    logging.error(f"Missing required mapping key: {key}")
                    return False
                
                if not isinstance(mappings[key], dict):
                    logging.error(f"Mapping key {key} must be a dictionary")
                    return False
            
            return True
            
        except (FileNotFoundError, yaml.YAMLError) as e:
            logging.error(f"Error validating mapping file: {e}")
            return False
    
    def create_example_mapping_file(self, output_file: str) -> None:
        """Create an example mapping file with common alternative column names.
        
        Args:
            output_file: Path where the example mapping file should be saved
        """
        example_mappings = {
            'geo_file_mapping': {
                'GISJOIN': 'BLOCK_GROUP_ID',      # Alternative: BLOCK_GROUP_ID
                'GEOID': 'CENSUS_ID',             # Alternative: CENSUS_ID
                'COUNTYFP': 'COUNTY_CODE',        # Alternative: COUNTY_CODE
                'TRACTCE': 'TRACT_CODE',          # Alternative: TRACT_CODE
                'BLKGRPCE': 'BLOCK_GROUP_CODE',   # Alternative: BLOCK_GROUP_CODE
                'ALAND': 'LAND_AREA',             # Alternative: LAND_AREA
                'geometry': 'geom'                # Alternative: geom
            },
            'pop_file_mapping': {
                'GISJOIN': 'BLOCK_GROUP_ID',      # Alternative: BLOCK_GROUP_ID
                'AJWME001': 'POPULATION_2018'     # Alternative: POPULATION_2018
            },
            'flood_file_mapping': {
                'GISJOIN': 'BLOCK_GROUP_ID',      # Alternative: BLOCK_GROUP_ID
                'Shape_Area': 'FLOOD_AREA',       # Alternative: FLOOD_AREA
                'fld_area': 'FLOODED_AREA',       # Alternative: FLOODED_AREA
                'perc_fld_area': 'FLOOD_PERCENT'  # Alternative: FLOOD_PERCENT
            },
            'housing_file_mapping': {
                'GISJOIN': 'BLOCK_GROUP_ID',      # Alternative: BLOCK_GROUP_ID
                'pop1990': 'POP_1990',            # Alternative: POP_1990
                'mhi1990': 'MEDIAN_INCOME_1990',  # Alternative: MEDIAN_INCOME_1990
                'hhsize1990': 'HH_SIZE_1990',     # Alternative: HH_SIZE_1990
                'coastdist': 'DIST_TO_COAST',     # Alternative: DIST_TO_COAST
                'cbddist': 'DIST_TO_CBD',         # Alternative: DIST_TO_CBD
                'hhtrans1993': 'HH_COUNT_1993',   # Alternative: HH_COUNT_1993
                'salesprice1993': 'SALES_PRICE_1993',  # Alternative: SALES_PRICE_1993
                'salespricesf1993': 'SALES_PRICE_SF_1993'  # Alternative: SALES_PRICE_SF_1993
            },
            'hedonic_file_mapping': {
                'GISJOIN': 'BLOCK_GROUP_ID',      # Alternative: BLOCK_GROUP_ID
                'N_MeanSqfeet': 'NORM_SQFT',      # Alternative: NORM_SQFT
                'N_MeanAge': 'NORM_AGE',          # Alternative: NORM_AGE
                'N_MeanNoOfStories': 'NORM_STORIES',  # Alternative: NORM_STORIES
                'N_MeanFullBathNumber': 'NORM_BATHS',  # Alternative: NORM_BATHS
                'N_perc_area_flood': 'NORM_FLOOD',  # Alternative: NORM_FLOOD
                'residuals': 'HEDONIC_RESIDUALS'  # Alternative: HEDONIC_RESIDUALS
            }
        }
        
        with open(output_file, 'w') as file:
            yaml.dump(example_mappings, file, default_flow_style=False, indent=2)
        
        logging.info(f"Example mapping file created: {output_file}")


def load_and_map_data(file_path: str, file_type: str, mapping_file: Optional[str] = None) -> pd.DataFrame:
    """Load data from file and apply field mapping.
    
    Args:
        file_path: Path to the input data file
        file_type: Type of file ('geo', 'pop', 'flood', 'housing', 'hedonic')
        mapping_file: Optional path to mapping file
        
    Returns:
        Dataframe with mapped column names
    """
    # Load data
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.shp'):
        import geopandas as gpd
        df = gpd.read_file(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
    
    # Apply field mapping
    mapper = FieldMapper(mapping_file)
    return mapper.map_dataframe(df, file_type) 