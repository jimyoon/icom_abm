from pynsim import Engine


class Zoning(Engine):
    """An engine class that manages zoning regulations and land use policies.
    
    The Zoning engine handles zoning-related operations including determining
    zoning classifications for block groups. It currently executes zoning
    determination for the year 2020, with framework in place for additional
    zoning operations.
    
    Args:
        target: The simulation network target containing block group nodes.
        **kwargs: Additional keyword arguments passed to the parent class.
    
    Inter-module Outputs/Modifications:
        target: Updated with zoning classifications through
            target.determine_zoning() method.
    """
    
    def __init__(self, target, zoning_mode: str = 'simple_perc', zoning_perc: float = 0.05, **kwargs) -> None:
        """Initialize the Zoning engine.
        
        Args:
            target: The simulation network target containing block group nodes.
            zoning_mode: Mode for zoning calculations (default: 'simple_perc').
            zoning_perc: Percentage for zoning calculations (default: 0.05).
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(Zoning, self).__init__(target, **kwargs)
        self.zoning_mode = zoning_mode
        self.zoning_perc = zoning_perc

    def run(self) -> None:
        """Execute the zoning determination process.
        
        Determines zoning classifications for block groups. Currently executes
        zoning determination specifically for the year 2020, with potential
        for expansion to handle multiple years or dynamic zoning changes.
        """
        # Try to get the current timestep from the simulator's network, fallback to target
        current_year = None
        if hasattr(self, 'simulator') and hasattr(self.simulator, 'network') and hasattr(self.simulator.network, 'current_timestep'):
            current_year = self.simulator.network.current_timestep.year
        elif hasattr(self.target, 'current_timestep'):
            current_year = self.target.current_timestep.year
        if current_year == 2020:
            self.target.determine_zoning()
