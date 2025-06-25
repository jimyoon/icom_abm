import logging

from pynsim import Engine


class HousingInventoryOld(Engine):  # JY: deprecated; housing inventory tracked via dataframe
    """An engine class that identifies housing inventory for the current timestep.
    
    The HousingInventoryOld class is a pynsim engine that scans through the model 
    landscape and identifies available housing inventory for each of the block groups.
    This class is deprecated as housing inventory is now tracked via dataframe.
    
    Args:
        target: The simulation network target containing block group nodes.
        residences_per_unit (int, optional): Number of residences per unit. 
            Defaults to 10.
        **kwargs: Additional keyword arguments passed to the parent class.
    
    Inter-module Outputs/Modifications:
        target.available_units_list (list): List of block group names with 
            available units.
    """

    def __init__(self, target, residences_per_unit: int = 10, **kwargs) -> None:
        """Initialize the HousingInventoryOld engine.
        
        Args:
            target: The simulation network target containing block group nodes.
            residences_per_unit: Number of residences per unit.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(HousingInventoryOld, self).__init__(target, **kwargs)
        self.residences_per_unit = residences_per_unit

    def run(self) -> None:
        """Execute the housing inventory identification process.
        
        Scans through all block group nodes and adds block group names to the
        available units list based on the number of available units in each
        block group.
        """
        for bg in self.target.nodes:
            if bg.available_units == 0:
                logging.info('no more units available for block group: ' + bg.name)
            for unit in range(bg.available_units):
                self.target.available_units_list.append(bg.name)

    def run_old(self) -> None:
        """Execute the legacy housing inventory identification process.
        
        Scans through all block group nodes and calculates available units based
        on a fixed number of residences per block group, then adds block group
        names to the available units list.
        """
        for bg in self.target.nodes:
            bg.available_residences = 10000  # temporarily assume 10,000 residences always available
            bg.available_units = (bg.available_residences + self.residences_per_unit // 2) // self.residences_per_unit  # division with rounding to nearest integer
            for unit in range(bg.available_units):
                self.target.available_units_list.append(bg.name)