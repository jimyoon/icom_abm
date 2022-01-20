from pynsim import Engine
import numpy as np

class BuildingDevelopment(Engine):
    def __init__(self, target, stock_increase_mode='simple_perc', stock_increase_perc=0.05, **kwargs):
        super(BuildingDevelopment, self).__init__(target, **kwargs)

    def run(self):
        self.target.housing_bg_df['new_units_constructed'] = np.where(self.target.housing_bg_df['demand_exceeds_supply'] == False, 0,
                                                              round(self.target.housing_bg_df['occupied_units'] * .05))

        for bg in self.target.nodes:
            bg.new_units_constructed = self.target.housing_bg_df[(self.target.housing_bg_df['GEOID'] == bg.name)]['new_units_constructed'].values[0]
            bg.available_units += bg.new_units_constructed
            bg.available_units = int(bg.available_units)