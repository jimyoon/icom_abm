from pynsim import Engine


class HousingPricing(Engine):
    """An engine class that manages housing pricing based on market demand and supply conditions.
    
    The HousingPricing class is a pynsim engine that adjusts housing prices in block groups
    based on demand and supply dynamics. It increases prices when demand exceeds supply and
    decreases prices when there has been sustained low demand over multiple timesteps.
    
    Args:
        target: The simulation network target containing block group nodes.
        housing_pricing_mode (str, optional): Mode for housing pricing calculation. 
            Currently only supports 'simple_perc'. Defaults to 'simple_perc'.
        price_increase_perc (float, optional): Percentage for price adjustments. 
            Defaults to 0.05.
        **kwargs: Additional keyword arguments passed to the parent class.
    
    Inter-module Outputs/Modifications:
        block_group.new_price (float): Updated housing price for each block group node.
        target.housing_block_group_df (pandas.DataFrame): Updated housing dataframe with 
            new price data.
    """
    
    def __init__(self, target, housing_pricing_mode: str = 'simple_perc', 
                 price_increase_perc: float = 0.05, **kwargs) -> None:
        """Initialize the HousingPricing engine.
        
        Args:
            target: The simulation network target containing block group nodes.
            housing_pricing_mode: Mode for housing pricing calculation.
            price_increase_perc: Percentage for price adjustments.
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
        # Guard: Check if target is a network (has nodes and housing_block_group_df)
        if not hasattr(self.target, 'nodes') or not hasattr(self.target, 'housing_block_group_df'):
            return
        
        for block_group in self.target.nodes:
            if block_group.demand_exceeds_supply:  # Removed '== True' for PEP8 compliance
                block_group.new_price = block_group.new_price * (1 + self.price_increase_perc)
                self.target.housing_block_group_df.loc[self.target.housing_block_group_df['GEOID'] == block_group.name, 'new_price'] = block_group.new_price

            if self.target.current_timestep_idx is not None and self.target.current_timestep_idx >= 5:  # JY TEMP for testing
                if not any(block_group.get_history('demand_exceeds_supply')[-5:]):
                    block_group.new_price = block_group.new_price * (1 - self.price_increase_perc)
                    self.target.housing_block_group_df.loc[self.target.housing_block_group_df['GEOID'] == block_group.name, 'new_price'] = block_group.new_price
