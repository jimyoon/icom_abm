#!/usr/bin/env python3
"""
Example script demonstrating geo_file datatype enforcement in CHANCE-C.

This script shows how the CHANCE-C model now automatically enforces the correct
datatypes for geo_file columns when loading data into geopandas DataFrames.

Expected geo_file datatypes:
- GISJOIN: object (string)
- GEOID: object (string)  
- COUNTYFP: object (string)
- TRACTCE: object (string)
- BLKGRPCE: object (string)
- ALAND: float64
- geometry: geometry (handled by geopandas)

Expected population_file datatypes:
- GISJOIN: object (string)
- AJWME001: int64 (or custom population field name)

Expected flood_file datatypes:
- GISJOIN: object (string)
- Shape_Area: float64
- fld_area: float64
- perc_fld_area: float64

Expected housing_file datatypes:
- GISJOIN: object (string)
- pop1990: int64
- mhi1990: int64
- hhsize1990: float64
- coastdist: float64
- cbddist: float64
- hhtrans1993: float64
- salesprice1993: float64
- salespricesf1993: float64

Expected hedonic_file datatypes:
- GISJOIN: object (string)
- N_MeanSqfeet: float64
- N_MeanAge: float64
- N_MeanNoOfStories: float64
- N_MeanFullBathNumber: float64
- residuals: float64
- N_perc_area_flood: float64
"""

import os
import sys
import pandas as pd
import geopandas as gpd
import logging

# Example of how to use the new functionality
def demonstrate_geo_datatypes():
    """Demonstrate the geo_file datatype enforcement functionality."""
    
    print("CHANCE-C Geo File Datatype Enforcement")
    print("=" * 50)
    
    print("When you load data files through CHANCE-C, the following datatypes are now automatically enforced:")
    print()
    
    print("GEO FILE DATATYPES:")
    geo_types = {
        'GISJOIN': 'object (string)',
        'GEOID': 'object (string)',
        'COUNTYFP': 'object (string)', 
        'TRACTCE': 'object (string)',
        'BLKGRPCE': 'object (string)',
        'ALAND': 'float64',
        'geometry': 'geometry (handled by geopandas)'
    }
    
    for field, dtype in geo_types.items():
        print(f"  {field:12}: {dtype}")
    
    print("\nPOPULATION FILE DATATYPES:")
    pop_types = {
        'GISJOIN': 'object (string)',
        'AJWME001': 'int64 (or custom population field)'
    }
    
    for field, dtype in pop_types.items():
        print(f"  {field:12}: {dtype}")
    
    print("\nFLOOD FILE DATATYPES:")
    flood_types = {
        'GISJOIN': 'object (string)',
        'Shape_Area': 'float64',
        'fld_area': 'float64',
        'perc_fld_area': 'float64'
    }
    
    for field, dtype in flood_types.items():
        print(f"  {field:12}: {dtype}")
    
    print("\nHOUSING FILE DATATYPES:")
    housing_types = {
        'GISJOIN': 'object (string)',
        'pop1990': 'int64',
        'mhi1990': 'int64',
        'hhsize1990': 'float64',
        'coastdist': 'float64',
        'cbddist': 'float64',
        'hhtrans1993': 'float64',
        'salesprice1993': 'float64',
        'salespricesf1993': 'float64'
    }
    
    for field, dtype in housing_types.items():
        print(f"  {field:16}: {dtype}")
    
    print("\nHEDONIC FILE DATATYPES:")
    hedonic_types = {
        'GISJOIN': 'object (string)',
        'N_MeanSqfeet': 'float64',
        'N_MeanAge': 'float64',
        'N_MeanNoOfStories': 'float64',
        'N_MeanFullBathNumber': 'float64',
        'residuals': 'float64',
        'N_perc_area_flood': 'float64'
    }
    
    for field, dtype in hedonic_types.items():
        print(f"  {field:20}: {dtype}")
    
    print()
    print("Benefits of this enforcement:")
    print("  ✓ Consistent data types across all CHANCE-C runs")
    print("  ✓ Prevents type-related errors during simulation")
    print("  ✓ Ensures proper string handling for ID fields")
    print("  ✓ Maintains numeric precision for area, population, flood, housing, and hedonic calculations")
    print("  ✓ Handles both default and custom population field names")
    print("  ✓ Ensures proper float precision for flood area, housing prices, and hedonic regression values")
    print("  ✓ Proper integer types for population and income data")
    print("  ✓ Accurate hedonic model calculations with consistent float64 precision")
    print("  ✓ Compatible with field mapping system")
    
    print()
    print("Usage in your code:")
    print("  # The datatype enforcement happens automatically when you create a Model")
    print("  from chance_c import Model")
    print("  from chance_c.data_loader import SimulationConfig")
    print()
    print("  # Option 1: Using configuration file")
    print("  config = SimulationConfig.from_yaml('your_config.yml')")
    print("  model = Model(config=config)")
    print()
    print("  # Option 2: Direct file paths")
    print("  model = Model(")
    print("      geo_filename='your_geo_file.shp',")
    print("      pop_filename='your_pop_file.csv',")
    print("      # ... other parameters")
    print("  )")
    print()
    print("  # All data files will be loaded with enforced datatypes")
    print("  model.run_simulation()")
    
    print()
    print("With field mapping:")
    print("  # If you have custom column names, use field mapping")
    print("  config = SimulationConfig(")
    print("      # Field mappings are now defined directly in the configuration file")
    print("      geo_filename='your_geo_file.shp',")
    print("      # ... other parameters")
    print("  )")
    print("  model = Model(config=config)")
    print("  # Your custom columns will be mapped AND datatypes enforced for all files")
    
    print()
    print("=" * 50)
    print("For more information, see the field mapping documentation:")
    print("  chance_c/data/FIELD_MAPPING_README.md")
    print("  chance_c/data/example_field_mapping.yml")

if __name__ == "__main__":
    demonstrate_geo_datatypes() 