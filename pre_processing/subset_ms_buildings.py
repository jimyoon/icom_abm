# This is a script that reads in an MS building geojson file, then subsets the buildings within the baltimore study
# region domain

import geopandas as gpd
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Load in MS buildings geojson
poly = gpd.read_file('C:\\Users\\yoon644\\OneDrive - PNNL\\Documents\\GIS\\ICoM\\ms_buildings_maryland\\Maryland.geojson\\Maryland.geojson')

# Load in shapefile (projects to EPSG:4326 - match with MS buildings projection)
balt = gpd.read_file ('C:\\Users\\yoon644\\OneDrive - PNNL\\Documents\\PyProjects\\icom_abm\\data_inputs\\blck_grp_extract_epsg4326.shp')

balt['dummy'] = 'dummy'  # add dummy column to dissolve all geometries into one
geom = balt.dissolve(by='dummy').geometry[0]  # take the single union geometry
subset = poly[poly.within(geom)]
subset.to_file('ms_buildings_balt.shp', driver='ESRI Shapefile')

# alternate method using sjoin (!! Much faster !!)

subset = gpd.sjoin(poly, balt, how="inner", op='intersects')
subset.to_file('ms_buildings_balt_sjoin.shp', driver='ESRI Shapefile')