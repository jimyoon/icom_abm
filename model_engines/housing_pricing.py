from pynsim import Engine
import numpy as np

class HousingPricing(Engine):
    def __init__(self, target, housing_pricing_mode='simple_perc', price_increase_perc=0.05, **kwargs):
        super(HousingPricing, self).__init__(target, **kwargs)
        self.price_increase_perc = price_increase_perc

    def run(self):

        for bg in self.target.nodes:
            if bg.demand_exceeds_supply == True:
                bg.new_price = bg.new_price * (1 + self.price_increase_perc)
                self.target.housing_bg_df.loc[self.target.housing_bg_df['GEOID'] == bg.name, 'new_price'] = bg.new_price

            if self.target.current_timestep_idx >= 5: # JY TEMP for testing
                if not any(bg.get_history('demand_exceeds_supply')):
                    bg.new_price = bg.new_price * (1 - self.price_increase_perc)
                    self.target.housing_bg_df.loc[self.target.housing_bg_df['GEOID'] == bg.name, 'new_price'] = bg.new_price
            #bg.new_price = bg.new_price * 2  # !JY TEMP