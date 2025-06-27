Getting Started
==============

This guide will help you get up and running with CHANCE-C quickly.

Installation
-----------

System Dependencies
^^^^^^^^^^^^^^^^^^

Before installing CHANCE-C, you need to install system-level geospatial libraries.

**Ubuntu/Debian:**
.. code-block:: bash

   sudo apt-get update
   sudo apt-get install -y \
     libgdal-dev \
     gdal-bin \
     libproj-dev \
     proj-data \
     proj-bin \
     libgeos-dev \
     libspatialindex-dev

**macOS:**
.. code-block:: bash

   brew install gdal proj geos

**Windows:**
Install GDAL, PROJ, and GEOS through OSGeo4W or conda-forge.

Python Package Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/jimyoon/icom_abm.git
   cd icom_abm

   # Install in development mode
   pip install -e .

   # Or install from PyPI (when available)
   pip install chance-c

Verifying Installation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import chance_c
   print(f"CHANCE-C version: {chance_c.__version__}")

   # Test basic functionality
   from chance_c import Model
   model = Model()
   print("Installation successful!")

Basic Usage
----------

Creating Your First Simulation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from chance_c import Model, SimulationConfig

   # Create a basic configuration
   config = SimulationConfig(
       simulation_name="my_first_simulation",
       start_year=2020,
       n_years=5,
       landscape_name="Baltimore"
   )

   # Create and run the model
   model = Model(config=config)
   model.run_simulation()

   # Access results
   network = model.simulator.network
   print(f"Total population: {network.total_population}")
   print(f"Average household income: {network.avg_hh_income}")

Using Your Own Data
^^^^^^^^^^^^^^^^^

.. code-block:: python

   from chance_c import Model

   # Specify your data files
   model = Model(
       geo_filename="path/to/geography.shp",
       pop_filename="path/to/population.csv",
       flood_filename="path/to/flood_data.csv",
       housing_filename="path/to/housing_data.csv",
       hedonic_filename="path/to/hedonic_data.csv"
   )

   model.run_simulation()

Data Requirements
----------------

CHANCE-C requires several data files to run simulations:

Geography Data (Shapefile)
^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Format**: ESRI Shapefile (.shp)
* **Required Fields**:
  * `GEOID`: Unique geographic identifier
  * `COUNTYFP`: County FIPS code
  * `geometry`: Polygon geometries for block groups

Population Data (CSV)
^^^^^^^^^^^^^^^^^^^^

* **Format**: Comma-separated values (.csv)
* **Required Fields**:
  * `GEOID`: Geographic identifier (matches shapefile)
  * `TOTAL_POPULATION`: Total population count
  * `HOUSEHOLD_COUNT`: Number of households

Flood Data (CSV)
^^^^^^^^^^^^^^^

* **Format**: Comma-separated values (.csv)
* **Required Fields**:
  * `GEOID`: Geographic identifier
  * `FLOOD_RISK`: Flood risk percentage (0-100)

Housing Data (CSV)
^^^^^^^^^^^^^^^^^

* **Format**: Comma-separated values (.csv)
* **Required Fields**:
  * `GEOID`: Geographic identifier
  * `HOUSING_UNITS`: Number of housing units
  * `MEDIAN_HOME_VALUE`: Median home value

Hedonic Data (CSV)
^^^^^^^^^^^^^^^^^

* **Format**: Comma-separated values (.csv)
* **Required Fields**:
  * `GEOID`: Geographic identifier
  * Various housing characteristics for pricing models

Configuration
-------------

Basic Configuration
^^^^^^^^^^^^^^^^^

.. code-block:: python

   config = SimulationConfig(
       # Basic settings
       simulation_name="example_simulation",
       scenario="baseline",
       intervention="none",
       start_year=2020,
       n_years=5,
       
       # Agent settings
       agent_housing_aggregation=10,  # Households per agent
       household_size=2.7,
       
       # Growth settings
       pop_growth_mode="perc",
       pop_growth_perc=0.01,
       
       # Market settings
       house_choice_mode="simple_avoidance_utility",
       house_budget_mode="rhea",
       perc_move=0.10,
   )

Advanced Configuration
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   config = SimulationConfig(
       # Environmental settings
       simple_avoidance_perc=0.95,
       budget_reduction_perc=0.90,
       
       # Development settings
       stock_increase_mode="simple_perc",
       stock_increase_perc=0.05,
       
       # Income growth
       inc_growth_mode="random_agent_replication",
       
       # Field mappings for custom data
       field_mappings={
           'geo_file_mapping': {
               'GEOID': 'CENSUS_ID',
               'COUNTYFP': 'COUNTY_CODE'
           },
           'pop_file_mapping': {
               'AJWME001': 'TOTAL_POPULATION'
           }
       }
   )

Field Mapping
-------------

If your data uses different column names, you can map them using the field mapping system:

.. code-block:: python

   field_mappings = {
       'geo_file_mapping': {
           'GEOID': 'CENSUS_ID',
           'COUNTYFP': 'COUNTY_CODE'
       },
       'pop_file_mapping': {
           'AJWME001': 'TOTAL_POPULATION',
           'AJWNE002': 'HOUSEHOLD_COUNT'
       },
       'flood_file_mapping': {
           'FLOOD_PCT': 'FLOOD_RISK'
       },
       'housing_file_mapping': {
           'UNITS': 'HOUSING_UNITS',
           'MEDIAN_VALUE': 'MEDIAN_HOME_VALUE'
       }
   }

   config = SimulationConfig(
       field_mappings=field_mappings,
       # ... other parameters
   )

Running Simulations
------------------

Basic Simulation
^^^^^^^^^^^^^^^

.. code-block:: python

   from chance_c import Model

   # Create model
   model = Model()
   
   # Run simulation
   model.run_simulation()
   
   # Access results
   results = model.get_results()

Parallel Simulations
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from chance_c import Model
   import multiprocessing as mp

   def run_simulation(config):
       model = Model(config=config)
       model.run_simulation()
       return model.get_results()

   # Create multiple configurations
   configs = [
       SimulationConfig(simulation_name=f"sim_{i}", start_year=2020, n_years=5)
       for i in range(10)
   ]

   # Run in parallel
   with mp.Pool() as pool:
       results = pool.map(run_simulation, configs)

Troubleshooting
--------------

Common Issues
^^^^^^^^^^^^

**Import Errors**
.. code-block:: python

   # If you get import errors for geospatial libraries
   # Make sure system dependencies are installed
   # On Ubuntu/Debian:
   sudo apt-get install libgdal-dev gdal-bin

**Data Loading Errors**
.. code-block:: python

   # Check your data files exist and have correct formats
   import pandas as pd
   import geopandas as gpd
   
   # Test loading your data
   geo_data = gpd.read_file("path/to/geography.shp")
   pop_data = pd.read_csv("path/to/population.csv")
   
   print("Data files loaded successfully")

**Memory Issues**
.. code-block:: python

   # For large datasets, consider reducing agent aggregation
   config = SimulationConfig(
       agent_housing_aggregation=20,  # Increase this number
       # ... other parameters
   )

Getting Help
-----------

* **Documentation**: This documentation site
* **Issues**: `GitHub Issues <https://github.com/jimyoon/icom_abm/issues>`_
* **Discussions**: `GitHub Discussions <https://github.com/jimyoon/icom_abm/discussions>`_

Next Steps
----------

* Read the :doc:`user_guide` for detailed usage instructions
* Explore the :doc:`api/index` for complete API documentation
* Check out :doc:`tutorials/index` for step-by-step tutorials
* See :doc:`examples/index` for practical examples 