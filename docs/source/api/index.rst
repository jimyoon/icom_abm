API Reference
=============

This section provides detailed documentation for all CHANCE-C classes, functions, and modules.

.. toctree::
   :maxdepth: 2
   :caption: API Documentation

   ../modules

Package Overview
------------------------------

The CHANCE-C package is organized into several key modules:

Core Modules
~~~~~~~~~~~~

- :doc:`../chance_c` - Main package with core functionality
- :doc:`../chance_c.model_classes` - Agent and landscape classes
- :doc:`../chance_c.model_engines` - Simulation engines and behaviors
- :doc:`../chance_c.data` - Data loading and management utilities

Main Classes
------------

Model and Configuration
~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: chance_c

.. autosummary::
   :toctree: generated/

   Model
   SimulationConfig

Model Classes
~~~~~~~~~~~~~

.. currentmodule:: chance_c.model_classes

.. autosummary::
   :toctree: generated/

   ICOMSimulator
   ABMLandscape
   HouseholdAgent
   BlockGroup
   CountyZoningManager
   RealEstate

Model Engines
~~~~~~~~~~~~~

.. currentmodule:: chance_c.model_engines

.. autosummary::
   :toctree: generated/

   NewAgentCreation
   ExistingAgentReloSampler
   NewAgentLocation
   ExistingAgentLocation
   HousingMarket
   BuildingDevelopment
   HousingPricing
   FloodHazard
   Zoning
   LandscapeStatistics

Data Management
~~~~~~~~~~~~~~~

.. currentmodule:: chance_c

.. autosummary::
   :toctree: generated/

   FieldMapper

Quick Reference
---------------

Common Usage Patterns
~~~~~~~~~~~~~~~~~~~~~

**Creating a Model**

.. code-block:: python

   from chance_c import Model
   
   # Default model
   model = Model()
   
   # Custom model
   model = Model(
       simulation_name="My_Simulation",
       start_year=2020,
       n_years=5
   )

**Running Simulations**

.. code-block:: python

   # Run simulation
   model.run_simulation()
   
   # Access results
   network = model.simulator.network
   results = network.housing_block_group_df

**Configuration Management**

.. code-block:: python

   from chance_c import SimulationConfig
   
   # Create configuration
   config = SimulationConfig(
       agent_housing_aggregation=20,
       pop_growth_perc=0.02
   )
   
   # Use with model
   model = Model(config=config)

**Field Mapping**

.. code-block:: python

   from chance_c import FieldMapper
   
   # Create field mappings
   mappings = {
       'geo_file_mapping': {
           'GEOID': 'CENSUS_ID'
       }
   }
   
   # Use in model
   model = Model(field_mappings=mappings)

Class Hierarchies
-----------------

Agent Classes
~~~~~~~~~~~~~

.. code-block:: text

   pynsim.Component
   └── HouseholdAgent

Institution Classes
~~~~~~~~~~~~~~~~~~

.. code-block:: text

   pynsim.Institution
   ├── AllHouseholdAgents
   ├── CountyZoningManager
   └── RealEstate

Engine Classes
~~~~~~~~~~~~~~

.. code-block:: text

   pynsim.Engine
   ├── NewAgentCreation
   ├── ExistingAgentReloSampler
   ├── NewAgentLocation
   ├── ExistingAgentLocation
   ├── HousingMarket
   ├── BuildingDevelopment
   ├── HousingPricing
   ├── FloodHazard
   ├── Zoning
   └── LandscapeStatistics

Network Classes
~~~~~~~~~~~~~~~

.. code-block:: text

   pynsim.Network
   └── ABMLandscape
       └── BlockGroup (nodes)

Key Interfaces
--------------

Model Interface
~~~~~~~~~~~~~~~

The main entry point for most users:

.. code-block:: python

   class Model:
       def __init__(self, **kwargs):
           """Initialize model with configuration parameters."""
           
       def run_simulation(self):
           """Execute the full simulation."""
           
       @property
       def config(self) -> SimulationConfig:
           """Access the simulation configuration."""
           
       @property
       def simulator(self) -> ICOMSimulator:
           """Access the underlying simulator."""

Configuration Interface
~~~~~~~~~~~~~~~~~~~~~~~~

Manages all simulation parameters:

.. code-block:: python

   class SimulationConfig:
       """Configuration dataclass with all simulation parameters."""
       
       # Basic settings
       simulation_name: str
       scenario: str
       start_year: int
       n_years: int
       
       # Agent settings
       agent_housing_aggregation: int
       household_size: float
       
       # Growth settings
       pop_growth_perc: float
       # ... many more parameters

Agent Interface
~~~~~~~~~~~~~~~

Individual decision-making entities:

.. code-block:: python

   class HouseholdAgent:
       def __init__(self, name, location, income, **kwargs):
           """Initialize household agent."""
           
       def make_housing_decision(self):
           """Make housing choice decisions."""
           
       def calculate_utility(self, location):
           """Calculate utility for a potential location."""

Engine Interface
~~~~~~~~~~~~~~~~

Behavioral modules that execute each timestep:

.. code-block:: python

   class BaseEngine:
       def __init__(self, target):
           """Initialize engine with target network."""
           
       def run(self):
           """Execute engine logic for current timestep."""

Data Loading Interface
~~~~~~~~~~~~~~~~~~~~~~

Handles input data processing:

.. code-block:: python

   class DataLoader:
       def load_geographic_data(self, filename):
           """Load shapefile data."""
           
       def load_population_data(self, filename):
           """Load population CSV data."""
           
       def apply_field_mappings(self, data, mappings):
           """Apply field name mappings."""

Error Handling
---------------

CHANCE-C defines several custom exceptions for better error handling:

.. code-block:: python

   # Configuration errors
   class ConfigurationError(Exception):
       """Raised when configuration is invalid."""
   
   # Data loading errors  
   class DataLoadingError(Exception):
       """Raised when data cannot be loaded."""
   
   # Simulation errors
   class SimulationError(Exception):
       """Raised during simulation execution."""

Type Hints
----------

CHANCE-C uses type hints throughout the codebase. Key type definitions:

.. code-block:: python

   from typing import Dict, List, Optional, Union, Tuple
   import pandas as pd
   import geopandas as gpd
   
   # Common type aliases
   AgentID = str
   LocationID = str
   ConfigDict = Dict[str, Union[str, int, float, bool]]
   GeoDataFrame = gpd.GeoDataFrame
   DataFrame = pd.DataFrame

Version Information
-------------------

To check the version of CHANCE-C you're using:

.. code-block:: python

   import chance_c
   print(chance_c.__version__)

For detailed information about changes between versions, see the :doc:`../changelog`.

Contributing to API Documentation
---------------------------------

The API documentation is automatically generated from docstrings in the source code. To improve the documentation:

1. **Enhance Docstrings**: Add or improve docstrings in the source code
2. **Add Examples**: Include usage examples in docstrings
3. **Type Annotations**: Ensure all functions have proper type hints
4. **Test Documentation**: Verify examples work correctly

For more information on contributing, see the project's contributing guidelines. 