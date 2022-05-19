from pynsim import Engine
import numpy as np

class BuildingDevelopment(Engine):
    def __init__(self, target, stock_increase_mode='simple_perc', stock_increase_perc=0.05, **kwargs):
        super(BuildingDevelopment, self).__init__(target, **kwargs)
        self.stock_increase_perc = stock_increase_perc

    def run(self):
        for bg in self.target.nodes:
            if bg.name == '240054924021' or bg.name== '245102603031': # JY TEMP debug
                print('HAHA')
                pass
            if bg.demand_exceeds_supply == True:
                bg.new_units_constructed = round(bg.occupied_units * self.stock_increase_perc)
                bg.available_units += bg.new_units_constructed
                bg.available_units = int(bg.available_units)
                # self.target.housing_bg_df.loc[self.target.housing_bg_df['GEOID'] == bg.name,
                #                               'new_units_constructed'] = bg.new_units_constructed (Seems 'new_units_
                # _constructed' is not used elsewhere. Remove it because adding it to an array for only specific
                # rows is not possible.
                column_index = self.target.column_index
                self.target.housing_bg_df[self.target.housing_bg_df[:, column_index['GEOID']] == bg.name, column_index['available_units']] = bg.available_units
            else:
                bg.new_units_constructed = 0