Getting Started
===============

Welcome to CHANCE-C! This guide will help you get up and running with the CHANCE-C agent-based modeling framework for coastal urban development simulations.

What is CHANCE-C?
-----------------

CHANCE-C (Coastal Hazards And Neighborhood Change - Computational) is a comprehensive agent-based modeling framework designed to simulate urban development dynamics in flood-prone coastal environments. The framework integrates:

- **Household Decision-Making**: Individual agents making housing choices
- **Housing Market Dynamics**: Supply, demand, pricing, and development
- **Environmental Hazards**: Flood risk and extreme weather impacts
- **Policy Interventions**: Zoning, regulations, and adaptation strategies

System Requirements
------------------

Before installing CHANCE-C, ensure your system meets these requirements:

- **Python**: 3.11 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 4GB RAM (8GB+ recommended for larger simulations)
- **Storage**: 1GB+ available disk space

**System Dependencies**:

- GDAL/OGR libraries
- PROJ (Projection library)
- GEOS (Geometry library)

Setting Up a Virtual Environment
---------------------------------

We strongly recommend using a virtual environment to isolate CHANCE-C dependencies:

Using venv
~~~~~~~~~~

.. code-block:: bash

   # Create a virtual environment
   python -m venv chance_c_env

   # Activate the virtual environment
   # On macOS/Linux:
   source chance_c_env/bin/activate

   # On Windows:
   chance_c_env\Scripts\activate

   # Verify activation (you should see chance_c_env in your prompt)
   which python

Using conda
~~~~~~~~~~~~

.. code-block:: bash

   # Create a conda environment
   conda create -n chance_c_env python=3.11

   # Activate the environment
   conda activate chance_c_env

   # Verify activation
   conda info --envs

Installation
------------

Once your virtual environment is activated, install CHANCE-C:

.. code-block:: bash

   pip install chance_c

For development installation:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/jimyoon/icom_abm.git
   cd icom_abm

   # Install in development mode
   pip install -e .

   # Install development dependencies
   pip install -e .[dev,docs]

Verify Installation
------------------

Test your installation by running:

.. code-block:: python

   import chance_c
   print(f"CHANCE-C version: {chance_c.__version__}")

   # Create a simple model to verify everything works
   from chance_c import Model
   model = Model()
   print("✓ CHANCE-C installed successfully!")

Your First Simulation
---------------------

Let's run your first CHANCE-C simulation using the included example data:

.. code-block:: python

   from chance_c import Model

   # Create a model with default settings
   model = Model()

   # Run a short simulation
   model.run_simulation()

   # Check results
   network = model.simulator.network
   print(f"Total population: {network.total_population}")
   print(f"Average household income: ${network.avg_hh_income:,.2f}")
   print(f"Average household size: {network.avg_hh_size:.2f}")

This simulation uses Baltimore-area example data included with CHANCE-C and runs for 2 years starting from 2018.

Understanding the Output
-------------------------

After running a simulation, you can access various results:

**Network-Level Statistics**:

.. code-block:: python

   network = model.simulator.network
   
   # Population metrics
   print(f"Total population: {network.total_population}")
   print(f"Total households: {len(network.get_institution('all_household_agents').components)}")
   
   # Housing metrics
   housing_df = network.housing_block_group_df
   print(f"Total housing units: {housing_df['housing_units'].sum()}")
   print(f"Average vacancy rate: {housing_df['vacancy_rate'].mean():.2%}")

**Agent-Level Data**:

.. code-block:: python

   # Get all household agents
   households = network.get_institution('all_household_agents').components
   
   # Analyze agent characteristics
   incomes = [agent.income for agent in households]
   locations = [agent.location for agent in households]
   
   print(f"Number of agents: {len(households)}")
   print(f"Income range: ${min(incomes):,.0f} - ${max(incomes):,.0f}")

**Spatial Data**:

.. code-block:: python

   # Access geographic data
   import geopandas as gpd
   
   gdf = gpd.GeoDataFrame(housing_df, geometry='geometry')
   
   # Plot population distribution
   ax = gdf.plot(column='population', legend=True, figsize=(10, 8))
   ax.set_title('Population Distribution by Block Group')

Next Steps
----------

Now that you have CHANCE-C installed and running, explore these resources:

1. **Quick Start Tutorial**: :doc:`quickstart` - Learn basic usage patterns
2. **Configuration Guide**: :doc:`configuration` - Understand simulation parameters
3. **Data Requirements**: :doc:`data_requirements` - Learn about input data formats
4. **Field Mapping**: :doc:`field_mapping` - Use your own data with custom column names
5. **Tutorials**: :doc:`tutorials/index` - In-depth guides and examples

Common Issues
-------------

**Import Errors**
  If you encounter import errors, ensure all dependencies are installed:
  
  .. code-block:: bash
  
     pip install --upgrade chance_c

**GDAL/Geospatial Issues**
  On some systems, you may need to install geospatial libraries separately:
  
  .. code-block:: bash
  
     # On Ubuntu/Debian
     sudo apt-get install gdal-bin libgdal-dev
     
     # On macOS with Homebrew
     brew install gdal
     
     # On Windows, consider using conda
     conda install gdal

**Memory Issues**
  For large simulations, consider:
  
  - Increasing agent aggregation (fewer, larger agents)
  - Reducing simulation years or study area
  - Using a machine with more RAM

Getting Help
------------

If you encounter issues or have questions:

- **Documentation**: Browse the full documentation for detailed guides
- **GitHub Issues**: `Report bugs or request features <https://github.com/jimyoon/icom_abm/issues>`_
- **Discussions**: `Join community discussions <https://github.com/jimyoon/icom_abm/discussions>`_
- **Examples**: Check the ``examples/`` directory in the repository

Deactivating Your Environment
------------------------------

When you're done working with CHANCE-C:

.. code-block:: bash

   # For venv:
   deactivate

   # For conda:
   conda deactivate 