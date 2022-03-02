# This file includes an assortment of example scripts for extracting and visualizing results from a completed ICoM ABM simulation object, "s"

import geopandas as pd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import contextily as ctx

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

##### See which histories are stored on the network
s.network._properties

#### Get history for total population
s.network.get_history('total_population')

### Get history for population of a particular block group
s.network.nodes[50].get_history('population')
s.network.get_node('240054015052001').get_history('population')

### Get location history for a specific household agents
s.network.get_institution('all_hh_agents').components[25000].get_history('location')

### Get list of agents that reside in a specific block group
s.network.get_node('245101204002001').hh_agents

##### Export final housing dataframe to geopackage
s.network.get_history('housing_bg_df')[-1].to_file(driver='ESRI Shapefile', filename="result_test.shp")

##### Plot initial population

##### Plot initial population (with basemap)
df = s.network.get_history('housing_bg_df')[0]
ax = df.plot(column = 'population', cmap='OrRd', alpha=0.8, legend=True)
ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite)

##### Plot final population
s.network.get_history('housing_bg_df')[-1].plot(column = 'population', cmap='OrRd', legend=True)

##### Plot population change
gdf = s.network.get_history('housing_bg_df')[-1]  # copy of final bg df
gdf['population_change'] = s.network.get_history('housing_bg_df')[-1]['population'] - s.network.get_history('housing_bg_df')[0]['population']
# normalize color
ax = gdf.plot(column = 'population', cmap='OrRd', alpha=0.8, legend=True)
ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite)

##### Plot population change with divergent chloropleth map centered on 0
gdf = s.network.get_history('housing_bg_df')[-1]  # copy of final bg df
gdf['population_change'] = s.network.get_history('housing_bg_df')[-1]['population'] - s.network.get_history('housing_bg_df')[0]['population']
# normalize color
vmin, vmax, vcenter = gdf.population_change.min(), gdf.population_change.max(), 0
norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
# create a normalized colorbar
cmap = 'RdBu'
cbar = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
# with normalization
ax = gdf.plot(column='population_change', cmap=cmap, alpha=0.8, norm=norm, legend=True)
ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite)

#### Plot initial and final population side-by-side / multi-panel plot example (consistent scale)
# Get min, max, average for color scale
vmin = min(s.network.get_history('housing_bg_df')[0].population.min(), s.network.get_history('housing_bg_df')[-1].population.min())
vmax = min(s.network.get_history('housing_bg_df')[0].population.max(), s.network.get_history('housing_bg_df')[-1].population.max())
vcenter = np.mean([vmin, vmax])
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
s.network.get_history('housing_bg_df')[0].plot(column='population', vmin=vmin, vmax=vmax, cmap='OrRd', ax=ax1, legend=True)
s.network.get_history('housing_bg_df')[-1].plot(column='population', vmin=vmin, vmax=vmax, cmap='OrRd', ax=ax2, legend=True)

#### Scatterplot two columns of housing dataframe
df = pd.DataFrame(s.network.housing_bg_df)
df['population_change'] = df['population'] - df['pop1990']
df.plot(x='salesprice1993', y='population_change', style='o')

#### Scatterplot two columns of housing dataframe (with another column providing hues)
import seaborn
df = pd.DataFrame(s.network.housing_bg_df)
df['population_change'] = df['population'] - df['pop1990']
seaborn.relplot(data=df, x='salesprice1993', y='population_change', hue='average_income', aspect=1.61)

#### Scatterplot two columns of housing dataframe (with another column providing hues)
import seaborn
df = pd.DataFrame(s.network.housing_bg_df)
df['population_change_perc'] = (df['population'] - df['pop1990']) / df['pop1990']
seaborn.relplot(data=df, x='perc_fld_area', y='population_change_perc', hue='average_income', aspect=1.61)

#### Scatterplot two columns of housing dataframe (with another column providing hues)
import seaborn
df = pd.DataFrame(s.network.housing_bg_df)
df['price_change'] = df['new_price'] - df['salesprice1993']
seaborn.relplot(data=df, x='perc_fld_area', y='price_change', hue='average_income', aspect=1.61)

#### Plot metric in flood zone threshold over time
import seaborn as sns
column_names = ["Model Year", "Population Percentage Change in Flood Zone", "Flood Coefficient"]
years = []
pop_perc_change = []
fld_coeff = -1000000
fld_coeff_list = []
for t in range(s.network.current_timestep_idx):
    df = s.network.get_history('housing_bg_df')[t]
    df_fld = df[(df.perc_fld_area >= df.perc_fld_area.quantile(.9))]
    pop_perc_change_fld = (df_fld.new_price.sum() - df_fld.salesprice1993.sum()) / df_fld.salesprice1993.sum()
    years.append(t+1)
    pop_perc_change.append(pop_perc_change_fld)
    fld_coeff_list.append(fld_coeff)
dict = {'Model Year': years,
        'Pop Perc Change Flood Zone': pop_perc_change,
        'Flood Coefficient': fld_coeff_list
        }
df = pd.DataFrame(dict)
df_append = pd.read_csv('temp_flood.csv', index_col=False)  # saved from a separate simulation and loaded in as csv
df = pd.concat([df,df_append],join='inner')
sns.lineplot(x='Model Year',
             y='Pop Perc Change Flood Zone',
             hue='Flood Coefficient',
             data=df)

