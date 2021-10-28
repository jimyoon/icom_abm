# This file contains scripts for various flood metrics in Baltimore

import geopandas as gpd
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

##### This script calculates the percentage area of each block group that is in the 100-year flood plain

flood = pd.read_csv('C:\\Users\\yoon644\\OneDrive - PNNL\\Documents\\PyProjects\\icom_abm\\data_inputs\\balt_100yr_intersect.txt')

aggregation_functions = {'Shape_Area': 'mean','fld_area': 'sum'}
flood = flood.groupby(['GISJOIN'], as_index=False).aggregate(aggregation_functions)
flood['perc_fld_area'] = flood['fld_area'] / flood['Shape_Area']

flood.to_csv('C:\\Users\\yoon644\\OneDrive - PNNL\\Documents\\PyProjects\\icom_abm\\data_inputs\\bg_perc_100yr_flood.csv')

##### This script calculates the percentage of building area that is inundated by at least 6-inches in the RIFT 100-yr flood

# Load in varoius shapefiles
flood = gpd.read_file('C:\\Users\\yoon644\\OneDrive - PNNL\\Documents\\PyProjects\\icom_abm\\data_inputs\\rift_flood_6in_epsg4326.shp')
build = gpd.read_file('C:\\Users\\yoon644\\OneDrive - PNNL\\Documents\\GIS\\ICoM\\ms_buildings_maryland\\ms_buildings_balt_sjoin.shp')
bg = gpd.read_file('C:\\Users\\yoon644\\OneDrive - PNNL\\Documents\\PyProjects\\icom_abm\\data_inputs\\blck_grp_extract_epsg4326.shp')

# Convert to a Cartesian system
flood = flood.to_crs({'init': 'epsg:6487'})
build = build.to_crs({'init': 'epsg:6487'})
bg = bg.to_crs({'init': 'epsg:6487'})

# Assign each building unique ID
build["id"] = build.index

# Determine areas of buildings
build["area"] = build['geometry'].area

# Clean up columns
build = build[['geometry','area', 'id']]

# Calculate total building footprint per block group
build_all_bg = gpd.sjoin(build, bg, how='inner',op='within')
aggregation_functions = {'area': 'sum'}
bg_build_area_all = build_all_bg.groupby(['GISJOIN'], as_index=False).aggregate(aggregation_functions)

# Calculate number of buildings per block group
build_all_bg = gpd.sjoin(build, bg, how='inner',op='within')
aggregation_functions = {'area': 'count'}
bg_build_area_count = build_all_bg.groupby(['GISJOIN'], as_index=False).aggregate(aggregation_functions)
bg_build_area_count = bg_build_area_count.rename(columns={'area': 'count'})
bg_build_area_count.to_csv('no_of_builds_count.csv')


# Subset flood inundation areas >6 inches
flood = flood[(flood.feet >= 6)]

# Identify those buildings in >6 inches flood zone flood zone
build_flood = gpd.sjoin(build, flood, how='inner',op='intersects')
build_flood = build_flood.drop_duplicates(subset='id', keep='first')  # drop duplicate buildings (i.e., building is repeated for each flood zone increment)
build_flood = build_flood[['geometry','area']]

# Calculate flooded footprint per block group
build_flood_bg = gpd.sjoin(build_flood, bg, how='inner',op='within')
aggregation_functions = {'area': 'sum'}
bg_build_area_flood = build_flood_bg.groupby(['GISJOIN'], as_index=False).aggregate(aggregation_functions)
bg_build_area_flood['area_flood'] = bg_build_area_flood['area']

# Calculate percent of building footprint flooded per block group
bg_percent_flood = pd.merge(bg_build_area_all, bg_build_area_flood[['GISJOIN','area_flood']], how='left', on='GISJOIN')
bg_percent_flood = bg_percent_flood.fillna(0)
bg_percent_flood['perc_area_flood'] = bg_percent_flood['area_flood'] / bg_percent_flood['area']
bg_percent_flood.to_csv('perc_build_area_flood_corr.csv')