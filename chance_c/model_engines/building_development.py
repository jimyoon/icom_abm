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
        bg.new_units_constructed (int): Number of new units constructed in block group.
        bg.available_units (int): Updated available units in block group.
        target.housing_bg_df (pandas.DataFrame): Updated housing dataframe with 
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
        for bg in self.target.nodes:
            if bg.demand_exceeds_supply:  # Removed '== True' for PEP8 compliance
                bg.new_units_constructed = round(bg.occupied_units * self.stock_increase_perc)
                bg.available_units += bg.new_units_constructed
                bg.available_units = int(bg.available_units)
                self.target.housing_bg_df.loc[self.target.housing_bg_df['GEOID'] == bg.name, 'new_units_constructed'] = bg.new_units_constructed
                self.target.housing_bg_df.loc[self.target.housing_bg_df['GEOID'] == bg.name, 'available_units'] = bg.available_units
            else:
                bg.new_units_constructed = 0