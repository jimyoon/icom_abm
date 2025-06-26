from pynsim import Engine


class BuildingDevelopment(Engine):
    """An engine class that manages building development based on housing demand.
    
    The BuildingDevelopment class is a pynsim engine that increases housing stock
    in block groups where demand exceeds supply. It calculates new units to be
    constructed based on a percentage of occupied units and updates both the
    block group nodes and the housing dataframe.
    
    Args:
        target: The simulation network target containing block group nodes.
        stock_increase_mode (str, optional): Mode for stock increase calculation. 
            Currently only supports 'simple_perc'. Defaults to 'simple_perc'.
        stock_increase_perc (float, optional): Percentage of occupied units to 
            use for calculating new construction. Defaults to 0.05.
        **kwargs: Additional keyword arguments passed to the parent class.
    
    Inter-module Outputs/Modifications:
        block_group.new_units_constructed (int): Number of new units constructed in block group.
        block_group.available_units (int): Updated available units in block group.
        target.housing_block_group_df (pandas.DataFrame): Updated housing dataframe with 
            new construction and available units data.
    """
    
    def __init__(self, target, stock_increase_mode: str = 'simple_perc', 
                 stock_increase_perc: float = 0.05, **kwargs) -> None:
        """Initialize the BuildingDevelopment engine.
        
        Args:
            target: The simulation network target containing block group nodes.
            stock_increase_mode: Mode for stock increase calculation.
            stock_increase_perc: Percentage of occupied units for new construction.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(BuildingDevelopment, self).__init__(target, **kwargs)
        self.stock_increase_perc = stock_increase_perc

    def run(self) -> None:
        """Execute the building development process.
        
        Iterates through all block group nodes and constructs new housing units
        where demand exceeds supply. Updates both node attributes and the housing
        dataframe with new construction data.
        """
        for block_group in self.target.nodes:
            if block_group.demand_exceeds_supply:  # Removed '== True' for PEP8 compliance
                block_group.new_units_constructed = round(block_group.occupied_units * self.stock_increase_perc)
                block_group.available_units += block_group.new_units_constructed
                block_group.available_units = int(block_group.available_units)
                self.target.housing_block_group_df.loc[self.target.housing_block_group_df['GEOID'] == block_group.name, 'new_units_constructed'] = block_group.new_units_constructed
                self.target.housing_block_group_df.loc[self.target.housing_block_group_df['GEOID'] == block_group.name, 'available_units'] = block_group.available_units
            else:
                block_group.new_units_constructed = 0