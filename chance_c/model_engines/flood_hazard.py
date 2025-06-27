import logging

from pynsim import Engine


class FloodHazard(Engine):
    """An engine class that manages flood hazard risk assessment and updates.
    
    The FloodHazard class is a pynsim engine that updates flood hazard risk
    values for block group nodes based on temporal conditions. Currently
    implements a simple risk assignment for a specific year.
    
    Args:
        target: The simulation network target containing block group nodes.
        **kwargs: Additional keyword arguments passed to the parent class.
    
    Inter-module Outputs/Modifications:
        block_group.flood_hazard_risk (int): Updated flood hazard risk value for each 
            block group node.
    """
    
    def __init__(self, target, **kwargs) -> None:
        """Initialize the FloodHazard engine.
        
        Args:
            target: The simulation network target containing block group nodes.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(FloodHazard, self).__init__(target, **kwargs)

    def run(self) -> None:
        """Execute the flood hazard risk assessment process.
        
        Updates flood hazard risk values for all block group nodes based on
        temporal conditions. Currently assigns a risk value of 100 for the
        year 2020.
        """
        logging.info("Running the flood hazard engine, year " + str(self.target.current_timestep.year))
        if self.target.current_timestep.year == 2020:
            for block_group in self.target.nodes:
                block_group.flood_hazard_risk = 100

        pass  # to accommodate debugger


class FloodGenerator(Engine):
    """An engine class that generates flood hazard events and updates risk values.
    
    The FloodGenerator class is a pynsim engine that simulates flood hazard
    events and updates flood hazard risk values for block group nodes based
    on temporal conditions. Currently implements a simple risk assignment
    for a specific year.
    
    Args:
        target: The simulation network target containing block group nodes.
        **kwargs: Additional keyword arguments passed to the parent class.
    
    Inter-module Outputs/Modifications:
        block_group.flood_hazard_risk (int): Updated flood hazard risk value for each 
            block group node.
    """
    
    def __init__(self, target, **kwargs) -> None:
        """Initialize the FloodGenerator engine.
        
        Args:
            target: The simulation network target containing block group nodes.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(FloodGenerator, self).__init__(target, **kwargs)

    def run(self) -> None:
        """Execute the flood hazard generation process.
        
        Updates flood hazard risk values for all block group nodes based on
        temporal conditions. Currently assigns a risk value of 100 for the
        year 2020.
        """
        if self.target.current_timestep.year == 2020:
            for block_group in self.target.nodes:
                block_group.flood_hazard_risk = 100

        pass  # to accommodate debugger
