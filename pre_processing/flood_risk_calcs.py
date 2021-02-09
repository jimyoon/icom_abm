# This script calculates the percentage area of each block group that is in the 100-year flood plain

import geopandas as gpd
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

flood = pd.read_csv('C:\\Users\\yoon644\\OneDrive - PNNL\\Documents\\PyProjects\\icom_abm\\data_inputs\\balt_100yr_intersect.txt')

aggregation_functions = {'Shape_Area': 'mean','fld_area': 'sum'}
flood = flood.groupby(['GISJOIN'], as_index=False).aggregate(aggregation_functions)
flood['perc_fld_area'] = flood['fld_area'] / flood['Shape_Area']

flood.to_csv('C:\\Users\\yoon644\\OneDrive - PNNL\\Documents\\PyProjects\\icom_abm\\data_inputs\\bg_perc_100yr_flood.csv')