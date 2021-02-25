# This file includes an assortment of example scripts for extracting results from a completed ICoM ABM simulation object, "s"

import geopandas as pd
import pandas as pd

# Export final housing dataframe to geopackage
s.network.housing_bg_df.to_file(driver='ESRI Shapefile', filename="result_test.shp")