import logging
from pynsim import Engine
import polars as pl
from chance_c.utils.polars_utils import fast_conditional_update_polars


class HousingPricing(Engine):
    """An engine class that adjusts housing prices based on demand and supply conditions.
    
    The HousingPricing class is a pynsim engine that iterates through all block group
    nodes and adjusts housing prices based on demand and supply conditions. It increases
    prices when demand exceeds supply and decreases prices when there has been sustained
    low demand over the previous 5 timesteps.
    
    Args:
        target: The simulation network target containing block group nodes.
        price_increase_perc (float, optional): Percentage increase for price adjustments.
            Defaults to 0.05.
        **kwargs: Additional keyword arguments passed to the parent class.
    
    Inter-module Outputs/Modifications:
        block_group.new_price (float): Updated housing price for each block group node.
        target.housing_block_group_df (pandas.DataFrame): Updated housing dataframe with
            new prices.
    """
    
    def __init__(self, target, price_increase_perc: float = 0.05, **kwargs) -> None:
        """Initialize the HousingPricing engine.
        
        Args:
            target: The simulation network target containing block group nodes.
            price_increase_perc: Percentage increase for price adjustments.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(HousingPricing, self).__init__(target, **kwargs)
        self.price_increase_perc = price_increase_perc

    def run(self) -> None:
        """Execute the housing pricing adjustment process.
        
        Iterates through all block group nodes and adjusts housing prices based on
        demand and supply conditions. Increases prices when demand exceeds supply
        and decreases prices when there has been sustained low demand over the
        previous 5 timesteps.
        """
        logging.info("Running the housing pricing engine, year " + str(self.target.current_timestep.year))
        
        # Handle price updates using pandas for compatibility
        for block_group in self.target.nodes:
            if block_group.demand_exceeds_supply:
                block_group.new_price = block_group.new_price * (1 + self.price_increase_perc)
                self.target.housing_block_group_df.loc[
                    self.target.housing_block_group_df['GEOID'] == block_group.name, 
                    'new_price'
                ] = block_group.new_price

            if self.target.current_timestep_idx >= 5:
                if hasattr(block_group, 'get_history') and not any(block_group.get_history('demand_exceeds_supply')[-5:]):
                    block_group.new_price = block_group.new_price * (1 - self.price_increase_perc)
                    self.target.housing_block_group_df.loc[
                        self.target.housing_block_group_df['GEOID'] == block_group.name, 
                        'new_price'
                    ] = block_group.new_price
