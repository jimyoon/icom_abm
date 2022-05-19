from pynsim import Engine
import numpy as np
import pandas as pd
from math import nan
import statistics

class LandscapeStatistics(Engine):
    def __init__(self, target, **kwargs):
        super(LandscapeStatistics, self).__init__(target, **kwargs)

    def run(self):
        # reset population sums
        self.target.total_population = 0

        # calculate various statistics (landscape level) from hh agents
        incomes_landscape = []
        hh_size_landscape = []

        # update master block group pandas dataframe
        rows_list = []  # first load dictionary for each row into a list, then create the dataframe from the dictionary (much faster!)
        for bg in self.target.nodes:
            if bg.name == '240054924021' or bg.name== '245102603031': # JY TEMP debug
                print('HAHA')
                pass
            bg_dict = {}
            bg_dict['name'] = bg.name
            bg_dict['no_hh_agents'] = len(bg.hh_agents)

            # calculate various statistics (block level) from hh agents
            bg.population = 0
            incomes_bg = []
            hh_size_bg = []
            bg.no_of_hhs = len(bg.hh_agents)


            for name, a in bg.hh_agents.items():
                if np.isfinite(a.hh_size) or a.hh_size == 0:  # accounts for 0 or nan hh_size values
                    self.target.total_population += a.no_hhs_per_agent * a.hh_size
                else:  # use mean
                    self.target.total_population += a.no_hhs_per_agent * self.target.housing_bg_df.hhsize1990.mean()
                bg.population += a.no_hhs_per_agent * a.hh_size
                incomes_bg.append(a.income)
                incomes_landscape.append(a.income)
                hh_size_bg.append(a.hh_size)
                hh_size_landscape.append(a.hh_size)

            bg_dict['population'] = bg.population
            if not incomes_bg:  # i.e. no households reside in block group
                bg_dict['average_income'] = nan
                bg.mean_hh_income = nan  # update attribute on block group
            else:
                bg_dict['average_income'] = statistics.mean(incomes_bg)
                bg.avg_hh_income = statistics.mean(incomes_bg)  # update attribute on block group
            if not hh_size_bg:
                bg_dict['avg_hh_size'] = nan
                bg.avg_hh_size = nan  # update attribute on block group
            else:
                bg_dict['avg_hh_size'] = statistics.mean(hh_size_bg)
                bg.avg_hh_size = statistics.mean(hh_size_bg)  # update attribute on block group

            # pop density calc
            bg_dict['pop_density'] = bg.population / bg.area
            bg.pop_density = bg.population / bg.area

            #  occupied units calc
            bg_dict['occupied_units'] = bg.occupied_units

            # available units calc
            bg_dict['available_units'] = bg.available_units

            # supply exceeds demand
            bg_dict['demand_exceeds_supply'] = bg.demand_exceeds_supply

            rows_list.append(bg_dict)

        housing_current_df = pd.DataFrame(rows_list)
        self.target.avg_hh_income = statistics.mean(incomes_landscape)
        self.target.avg_hh_size = statistics.mean(hh_size_landscape)

        # calculate normalized statistics for block groups
        housing_current_df['average_income_norm'] = housing_current_df['average_income'] / housing_current_df['average_income'].max()

        # merge with housing_bg_df to retain geometry features
        previous_housing_bg = pd.DataFrame(self.target.housing_bg_df, columns=self.target.column_index)
        cols_to_use = previous_housing_bg.columns.difference(housing_current_df.columns)
        updated_housing_bg_df = pd.merge(previous_housing_bg[cols_to_use], housing_current_df, how='left',
                                         left_on='GEOID', right_on='name')
        column_index = dict(zip(updated_housing_bg_df.columns, list(range(0, len(updated_housing_bg_df.columns)))))
        updated_housing_bg_df = updated_housing_bg_df.to_numpy()
        self.target.housing_bg_df = updated_housing_bg_df
        self.targt.column_index = column_index
