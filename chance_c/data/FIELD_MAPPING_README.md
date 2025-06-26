# Field Mapping Configuration

This document explains how to use the field mapping functionality in the CHANCE ABM model to handle input files with different column names.

## Overview

The CHANCE ABM model requires specific column names in its input files. However, your data files may use different column names. The field mapping functionality allows you to map your custom column names to the required field names used by the model.

## Required Field Names

The model requires the following field names for each input file type:

### Geographic File (geo_file_mapping)
- `GISJOIN` - Unique identifier for each block group
- `GEOID` - Unique identifier for each block group  
- `COUNTYFP` - County code
- `TRACTCE` - Tract code
- `BLKGRPCE` - Block group code
- `ALAND` - Land area
- `geometry` - Geometry of the block group

### Population File (pop_file_mapping)
- `GISJOIN` - Unique identifier for each block group
- `AJWME001` - Population count (mapped from your custom column name)

### Flood File (flood_file_mapping)
- `GISJOIN` - Unique identifier for each flood zone
- `Shape_Area` - Area of the flood zone
- `fld_area` - Area of the flood zone
- `perc_fld_area` - Percentage of the flood zone

### Housing File (housing_file_mapping)
- `GISJOIN` - Unique identifier for each block group
- `pop1990` - Population in 1990
- `mhi1990` - Median household income in 1990
- `hhsize1990` - Average household size in 1990
- `coastdist` - Distance to the coast
- `cbddist` - Distance to the CBD
- `hhtrans1993` - Number of households in 1993
- `salesprice1993` - Sales price in 1993
- `salespricesf1993` - Sales price per square foot in 1993

### Hedonic File (hedonic_file_mapping)
- `GISJOIN` - Unique identifier for each block group
- `N_MeanSqfeet` - Normalized mean square feet
- `N_MeanAge` - Normalized mean age
- `N_MeanNoOfStories` - Normalized mean number of stories
- `N_MeanFullBathNumber` - Normalized mean number of full bathrooms
- `N_perc_area_flood` - Normalized percentage of the block group in the flood zone
- `residuals` - Residuals from hedonic regression

## How to Use Field Mapping

### Step 1: Create a Field Mapping File

Create a YAML file that maps your column names to the required field names. You can use the example file `data/example_field_mapping.yml` as a starting point.

Example mapping file (`my_mapping.yml`):
```yaml
# Geographic file field mappings
geo_file_mapping:
  GISJOIN: "BLOCK_GROUP_ID"      # Your column name for unique block group identifier
  GEOID: "CENSUS_ID"             # Your column name for census identifier
  COUNTYFP: "COUNTY_CODE"        # Your column name for county code
  TRACTCE: "TRACT_CODE"          # Your column name for tract code
  BLKGRPCE: "BLOCK_GROUP_CODE"   # Your column name for block group code
  ALAND: "LAND_AREA"             # Your column name for land area
  geometry: "geom"               # Your column name for geometry

# Population file field mappings
pop_file_mapping:
  GISJOIN: "BLOCK_GROUP_ID"      # Your column name for unique block group identifier
  AJWME001: "POPULATION_2018"    # Your column name for population count

# Flood file field mappings
flood_file_mapping:
  GISJOIN: "BLOCK_GROUP_ID"      # Your column name for unique block group identifier
  Shape_Area: "FLOOD_AREA"       # Your column name for flood area
  fld_area: "FLOODED_AREA"       # Your column name for flooded area
  perc_fld_area: "FLOOD_PERCENT" # Your column name for flood percentage

# Housing file field mappings
housing_file_mapping:
  GISJOIN: "BLOCK_GROUP_ID"      # Your column name for unique block group identifier
  pop1990: "POP_1990"            # Your column name for 1990 population
  mhi1990: "MEDIAN_INCOME_1990"  # Your column name for 1990 median household income
  hhsize1990: "HH_SIZE_1990"     # Your column name for 1990 household size
  coastdist: "DIST_TO_COAST"     # Your column name for distance to coast
  cbddist: "DIST_TO_CBD"         # Your column name for distance to CBD
  hhtrans1993: "HH_COUNT_1993"   # Your column name for 1993 household count
  salesprice1993: "SALES_PRICE_1993"  # Your column name for 1993 sales price
  salespricesf1993: "SALES_PRICE_SF_1993"  # Your column name for 1993 sales price per sq ft

# Hedonic file field mappings
hedonic_file_mapping:
  GISJOIN: "BLOCK_GROUP_ID"      # Your column name for unique block group identifier
  N_MeanSqfeet: "NORM_SQFT"      # Your column name for normalized square feet
  N_MeanAge: "NORM_AGE"          # Your column name for normalized age
  N_MeanNoOfStories: "NORM_STORIES"  # Your column name for normalized stories
  N_MeanFullBathNumber: "NORM_BATHS"  # Your column name for normalized bathrooms
  N_perc_area_flood: "NORM_FLOOD"  # Your column name for normalized flood percentage
  residuals: "HEDONIC_RESIDUALS"  # Your column name for hedonic residuals
```

### Step 2: Update Your Configuration

Add the field mapping file path to your simulation configuration:

```yaml
# In your config.yml file
field_mapping_file: "my_mapping.yml"
```

### Step 3: Use the Configuration

When you create your simulation configuration, the field mapping will be automatically applied:

```python
from chance_c.data_loader import SimulationConfig

# Load configuration with field mapping
config = SimulationConfig.from_yaml('config.yml')

# Validate field mapping
if config.validate_field_mapping():
    print("Field mapping is valid!")
else:
    print("Field mapping validation failed!")

# Get required columns for a specific file type
required_columns = config.get_required_columns('geo')
print("Required columns for geo file:", required_columns)
```

## Validation

The field mapping system includes validation to ensure:

1. All required mapping keys are present
2. All required columns are mapped
3. The mapping file is valid YAML

## Error Handling

If your input files are missing required columns, the system will provide clear error messages indicating which columns are missing and what they should map to.

## Examples

### Example 1: Using Default Field Names
If your data files already use the required field names, you don't need a mapping file. The system will use default mappings.

### Example 2: Custom Column Names
If your data files use different column names, create a mapping file and specify it in your configuration.

### Example 3: Partial Mapping
You only need to map the columns that have different names. Columns that already match the required names can be omitted from the mapping file.

## Troubleshooting

### Common Issues

1. **Missing Required Columns**: Ensure all required columns are present in your mapping file
2. **Invalid YAML**: Check that your mapping file is valid YAML syntax
3. **File Not Found**: Verify the path to your mapping file is correct
4. **Column Name Mismatch**: Ensure the column names in your mapping file exactly match those in your data files

### Getting Help

If you encounter issues with field mapping:

1. Check the example files provided (`data/example_field_mapping.yml`, `data/example_config.yml`)
2. Validate your mapping file using the validation function
3. Review the error messages for specific missing columns
4. Ensure your data files contain all required columns

## Advanced Usage

### Programmatic Field Mapping

You can also use the field mapping functionality programmatically:

```python
from chance_c.field_mapper import FieldMapper, load_and_map_data

# Create a field mapper
mapper = FieldMapper('my_mapping.yml')

# Load and map data
df = load_and_map_data('my_data.csv', 'geo', 'my_mapping.yml')

# Or map an existing dataframe
mapped_df = mapper.map_dataframe(df, 'geo')
```

### Creating Example Mapping Files

You can programmatically create example mapping files:

```python
from chance_c.field_mapper import FieldMapper

mapper = FieldMapper()
mapper.create_example_mapping_file('example_mapping.yml')
``` 