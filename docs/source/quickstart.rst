Quick Start
===========

Get up and running with CHANCE-C in 5 minutes! This guide shows you how to install CHANCE-C and run your first simulation.

Installation
------------

Install CHANCE-C using pip:

.. code-block:: bash

   # Create virtual environment (recommended)
   python -m venv chance_c_env
   source chance_c_env/bin/activate  # On Windows: chance_c_env\Scripts\activate
   
   # Install CHANCE-C
   pip install chance_c

Your First Simulation
---------------------

Run a complete simulation with just a few lines of code:

.. code-block:: python

   from chance_c import Model
   
   # Create model with default settings
   model = Model()
   
   # Run simulation (uses Baltimore example data)
   model.run_simulation()
   
   # View results
   network = model.simulator.network
   print(f"Total population: {network.total_population:,}")
   print(f"Average income: ${network.avg_hh_income:,.2f}")

That's it! You've just run a 2-year urban development simulation for Baltimore.

What Just Happened?
--------------------

Your simulation:

1. **Loaded example data** - Baltimore area demographics, housing, and flood risk
2. **Created household agents** - Individual households with income, preferences, and behaviors
3. **Simulated 2 years** - Agents made housing decisions, moved locations, and participated in markets
4. **Collected results** - Population, housing, and economic outcomes

Next Steps
----------

**Customize Your Simulation**

.. code-block:: python

   # Run longer simulation with more agents
   model = Model(
       simulation_name="My_Custom_Simulation",
       n_years=5,
       agent_housing_aggregation=5,  # More detailed agents
       pop_growth_perc=0.02          # 2% annual growth
   )
   model.run_simulation()

**Explore Results**

.. code-block:: python

   # Get detailed results
   housing_df = network.housing_block_group_df
   households = network.get_institution('all_household_agents').components
   
   # Basic analysis
   print(f"Housing units: {housing_df['housing_units'].sum():,}")
   print(f"Vacancy rate: {housing_df['vacancy_rate'].mean():.1%}")
   print(f"Number of agents: {len(households)}")

**Visualize Results**

.. code-block:: python

   import matplotlib.pyplot as plt
   import geopandas as gpd
   
   # Create map of population distribution
   gdf = gpd.GeoDataFrame(housing_df, geometry='geometry')
   gdf.plot(column='population', legend=True, figsize=(10, 8))
   plt.title('Population by Block Group')
   plt.show()

**Use Your Own Data**

.. code-block:: python

   # Use your own data files
   model = Model(
       geo_filename="path/to/your/geography.shp",
       pop_filename="path/to/your/population.csv",
       flood_filename="path/to/your/flood_data.csv",
       housing_filename="path/to/your/housing_data.csv",
       hedonic_filename="path/to/your/hedonic_data.csv"
   )

Learn More
----------

- **Detailed Tutorial**: :doc:`tutorials/quickstarter` - Complete step-by-step guide
- **Configuration**: :doc:`configuration` - Customize simulation parameters  
- **User Guide**: :doc:`user_guide` - Understand CHANCE-C concepts
- **API Reference**: :doc:`api/index` - Detailed technical documentation
- **Examples**: :doc:`examples/index` - Real-world use cases

Need Help?
----------

- **GitHub Issues**: `Report problems <https://github.com/jimyoon/icom_abm/issues>`_
- **Discussions**: `Ask questions <https://github.com/jimyoon/icom_abm/discussions>`_
- **Documentation**: Browse the full documentation for detailed guides 