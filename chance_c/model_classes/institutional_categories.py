from pynsim import Institution


class AllHouseholdAgents(Institution):
    """An institution that contains all household agents in the simulation.
    
    This institution serves as a container for all household agents,
    providing a centralized way to access and manage household agents
    across the entire simulation landscape.
    
    Args:
        name (str): The name identifier for this institution.
        **kwargs: Additional keyword arguments passed to the parent class.
    """
    
    def __init__(self, name: str, **kwargs) -> None:
        """Initialize the AllHouseholdAgents institution.
        
        Args:
            name: Name identifier for the institution.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super(AllHouseholdAgents, self).__init__(name, **kwargs)

    def setup(self, timestep: int) -> None:
        """Set up the institution for a given timestep.
        
        Args:
            timestep: The current timestep for setup operations.
        """
        pass
