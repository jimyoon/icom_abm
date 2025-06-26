# Field Mapping System for CHANCE-C

The CHANCE-C model uses a flexible field mapping system that allows you to use data files with different column names than the standard ones expected by the model. This system is now integrated directly into the configuration file, making it easier to manage and version control your field mappings.

## Overview

The field mapping system allows you to:
- Use data files with custom column names
- Map your column names to the required field names used by the model
- Maintain flexibility while ensuring data compatibility
- Keep all configuration in one place

## How It Works

Instead of using a separate field mapping file, you now define field mappings directly in your configuration YAML file. The model will automatically apply these mappings when loading your data files.

### Required Field Names

The model expects specific field names for each type of input file:

#### Geographic File (Shapefile)
- `GISJOIN`: Unique identifier for each block group
- `GEOID`: Geographic identifier
- `COUNTYFP`: County code
- `TRACTCE`: Tract code
- `BLKGRPCE`: Block group code
- `ALAND`: Land area
- `geometry`: Geometry column

#### Population File (CSV)
- `GISJOIN`: Unique identifier for each block group
- `AJWME001`: Population count

#### Flood File (CSV)
- `GISJOIN`: Unique identifier for each block group
- `Shape_Area`: Total area
- `fld_area`: Flood area
- `perc_fld_area`: Percentage of area in flood zone

#### Housing File (CSV)
- `GISJOIN`: Unique identifier for each block group
- `pop1990`: Population in 1990
- `mhi1990`: Median household income in 1990
- `hhsize1990`: Average household size in 1990
- `coastdist`: Distance to coast
- `cbddist`: Distance to CBD
- `hhtrans1993`: Number of house transactions in 1993
- `salesprice1993`: Sales price in 1993
- `salespricesf1993`: Sales price per square foot in 1993

#### Hedonic File (CSV)
- `GISJOIN`: Unique identifier for each block group
- `N_MeanSqfeet`: Normalized mean square feet
- `N_MeanAge`: Normalized mean age
- `N_MeanNoOfStories`: Normalized mean number of stories
- `N_MeanFullBathNumber`: Normalized mean number of full bathrooms
- `N_perc_area_flood`: Normalized percentage in flood zone
- `residuals`: Hedonic regression residuals

## Configuration Format

Field mappings are defined directly in your configuration YAML file using the following structure:

```yaml
# Field mapping configurations
geo_file_mapping:
  GISJOIN: "your_column_name"
  GEOID: "your_column_name"
  # ... other mappings

pop_file_mapping:
  GISJOIN: "your_column_name"
  AJWME001: "your_column_name"
  # ... other mappings

# ... other file type mappings
```

## Usage Examples

### Example 1: Standard Column Names
If your data files already use the standard column names, you can use the default mappings:

```yaml
geo_file_mapping:
  GISJOIN: "GISJOIN"
  GEOID: "GEOID"
  COUNTYFP: "COUNTYFP"
  TRACTCE: "TRACTCE"
  BLKGRPCE: "BLKGRPCE"
  ALAND: "ALAND"
  geometry: "geometry"
```

### Example 2: Custom Column Names
If your data files use different column names, map them accordingly:

```yaml
geo_file_mapping:
  GISJOIN: "BLOCK_GROUP_ID"      # Your file uses BLOCK_GROUP_ID
  GEOID: "CENSUS_ID"             # Your file uses CENSUS_ID
  COUNTYFP: "COUNTY_CODE"        # Your file uses COUNTY_CODE
  TRACTCE: "TRACT_CODE"          # Your file uses TRACT_CODE
  BLKGRPCE: "BLOCK_GROUP_CODE"   # Your file uses BLOCK_GROUP_CODE
  ALAND: "LAND_AREA"             # Your file uses LAND_AREA
  geometry: "geom"               # Your file uses geom
```

### Example 3: Mixed Standard and Custom Names
You can mix standard and custom column names:

```yaml
pop_file_mapping:
  GISJOIN: "GISJOIN"           # Standard name
  AJWME001: "POPULATION_2018"  # Custom name
```

## Complete Configuration Example

Here's a complete example showing all field mappings in a configuration file:

```yaml
# ... other configuration parameters ...

# Field mapping configurations
geo_file_mapping:
  GISJOIN: "GISJOIN"
  GEOID: "GEOID"
  COUNTYFP: "COUNTYFP"
  TRACTCE: "TRACTCE"
  BLKGRPCE: "BLKGRPCE"
  ALAND: "ALAND"
  geometry: "geometry"

pop_file_mapping:
  GISJOIN: "GISJOIN"
  AJWME001: "AJWME001"

flood_file_mapping:
  GISJOIN: "GISJOIN"
  Shape_Area: "Shape_Area"
  fld_area: "fld_area"
  perc_fld_area: "perc_fld_area"

housing_file_mapping:
  GISJOIN: "GISJOIN"
  pop1990: "pop1990"
  mhi1990: "mhi1990"
  hhsize1990: "hhsize1990"
  coastdist: "coastdist"
  cbddist: "cbddist"
  hhtrans1993: "hhtrans1993"
  salesprice1993: "salesprice1993"
  salespricesf1993: "salespricesf1993"

hedonic_file_mapping:
  GISJOIN: "GISJOIN"
  N_MeanSqfeet: "N_MeanSqfeet"
  N_MeanAge: "N_MeanAge"
  N_MeanNoOfStories: "N_MeanNoOfStories"
  N_MeanFullBathNumber: "N_MeanFullBathNumber"
  N_perc_area_flood: "N_perc_area_flood"
  residuals: "residuals"
```

## Validation

The system automatically validates your field mappings to ensure:
- All required mappings are present
- Mapping values are properly formatted
- Referenced columns exist in your data files

## Best Practices

1. **Keep mappings organized**: Group related mappings together in your configuration file
2. **Use descriptive comments**: Add comments to explain custom column names
3. **Test your mappings**: Validate your configuration before running simulations
4. **Version control**: Keep your configuration files in version control
5. **Document changes**: Document any changes to field mappings for reproducibility

## Migration from Separate Field Mapping Files

If you were previously using separate field mapping files, you can easily migrate:

1. Open your existing field mapping YAML file
2. Copy the mapping sections
3. Paste them into your configuration file
4. Remove the `field_mapping_file` parameter from your configuration
5. Test your configuration to ensure it works correctly

## Troubleshooting

### Common Issues

1. **Missing required fields**: Ensure all required field mappings are present
2. **Column not found**: Verify that the column names in your mappings match your data files exactly
3. **Case sensitivity**: Column names are case-sensitive
4. **Typos**: Double-check spelling of column names

### Error Messages

- `Missing required mapping key`: Add the missing field mapping section
- `Missing required columns`: Check that your data files contain the expected columns
- `Unknown file type`: Verify that you're using the correct file type identifier

## Getting Help

If you encounter issues with field mapping:
1. Check this documentation
2. Verify your data file column names
3. Test with the example configuration file
4. Check the model logs for detailed error messages

The field mapping system is designed to be flexible and user-friendly while maintaining data integrity and model compatibility. 