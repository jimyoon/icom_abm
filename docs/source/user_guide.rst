User Guide
==========

This guide provides detailed information on using CHANCE-C for agent-based modeling of coastal urban development.

Core Concepts
------------

Agent-Based Modeling
^^^^^^^^^^^^^^^^^^^

CHANCE-C uses agent-based modeling to simulate individual household decision-making in coastal environments. Each agent represents multiple households and makes decisions about:

* Residential location choice
* Housing preferences
* Risk perception and avoidance
* Income and budget constraints

The simulation progresses through annual time steps, with agents interacting with:

* The housing market
* Environmental hazards (flooding)
* Policy interventions
* Other agents

Housing Market Dynamics
^^^^^^^^^^^^^^^^^^^^^^

The housing market in CHANCE-C includes:

* **Supply**: Existing housing stock and new development
* **Demand**: Household preferences and budgets
* **Pricing**: Market-driven price adjustments
* **Transactions**: Buyer-seller matching

Environmental Hazards
^^^^^^^^^^^^^^^^^^^^

Flood risk is modeled through:

* **Risk Assessment**: Geographic flood probability
* **Risk Perception**: Agent awareness and avoidance
* **Impact Modeling**: Property damage and value changes
* **Adaptation**: Policy and individual responses

Model Architecture
-----------------

Simulation Components
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from chance_c import Model

   model = Model()
   
   # Core components
   simulator = model.simulator          # Main simulation engine
   network = simulator.network         # Geographic network
   landscape = network.landscape       # Spatial data
   agents = network.get_institution('all_household_agents')  # Household agents

Data Flow
^^^^^^^^^

1. **Input Data**: Geography, population, housing, flood risk
2. **Initialization**: Create agents, set up network
3. **Simulation Loop**: Annual iterations
4. **Output**: Results and statistics

Configuration Management
-----------------------

Basic Configuration
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from chance_c import SimulationConfig

   config = SimulationConfig(
       simulation_name="baltimore_study",
       start_year=2020,
       n_years=10,
       landscape_name="Baltimore",
       pop_growth_perc=0.02,
       agent_housing_aggregation=10
   )

Advanced Configuration
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   config = SimulationConfig(
       # Growth parameters
       pop_growth_mode="perc",
       pop_growth_perc=0.015,
       inc_growth_mode="random_agent_replication",
       
       # Housing market parameters
       house_choice_mode="simple_avoidance_utility",
       house_budget_mode="rhea",
       perc_move=0.12,
       
       # Environmental parameters
       simple_avoidance_perc=0.95,
       budget_reduction_perc=0.90,
       
       # Development parameters
       stock_increase_mode="simple_perc",
       stock_increase_perc=0.03,
       
       # Data files
       geo_filename="baltimore_block_groups.shp",
       pop_filename="baltimore_population.csv",
       flood_filename="baltimore_flood_risk.csv",
       housing_filename="baltimore_housing.csv",
       hedonic_filename="baltimore_hedonic.csv"
   )

Data Requirements
----------------

Input Data Format
^^^^^^^^^^^^^^^^

**Geography (Shapefile)**
.. code-block:: python

   import geopandas as gpd
   
   # Required columns
   geo_data = gpd.read_file("geography.shp")
   print(geo_data.columns)
   # Should include: GEOID, COUNTYFP, geometry

**Population (CSV)**
.. code-block:: python

   import pandas as pd
   
   # Required columns
   pop_data = pd.read_csv("population.csv")
   print(pop_data.columns)
   # Should include: GEOID, TOTAL_POPULATION, HOUSEHOLD_COUNT

**Flood Risk (CSV)**
.. code-block:: python

   # Required columns
   flood_data = pd.read_csv("flood_risk.csv")
   print(flood_data.columns)
   # Should include: GEOID, FLOOD_RISK

Data Validation
^^^^^^^^^^^^^^

.. code-block:: python

   from chance_c import Model
   
   # Model will validate data automatically
   model = Model(
       geo_filename="data/geography.shp",
       pop_filename="data/population.csv",
       flood_filename="data/flood_risk.csv"
   )
   
   # Check for validation errors
   if model.validation_errors:
       print("Data validation errors:", model.validation_errors)

Running Simulations
------------------

Basic Simulation
^^^^^^^^^^^^^^^

.. code-block:: python

   from chance_c import Model, SimulationConfig
   
   # Create configuration
   config = SimulationConfig(
       simulation_name="test_simulation",
       start_year=2020,
       n_years=5
   )
   
   # Create and run model
   model = Model(config=config)
   model.run_simulation()
   
   # Access results
   results = model.get_results()
   print(f"Simulation completed: {results['total_population']} total population")

Parallel Simulations
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from chance_c import Model, SimulationConfig
   import multiprocessing as mp
   from functools import partial
   
   def run_simulation(config):
       model = Model(config=config)
       model.run_simulation()
       return model.get_results()
   
   # Create multiple configurations
   configs = []
   for i in range(10):
       config = SimulationConfig(
           simulation_name=f"sim_{i}",
           start_year=2020,
           n_years=5,
           pop_growth_perc=0.01 + i * 0.001
       )
       configs.append(config)
   
   # Run in parallel
   with mp.Pool(processes=4) as pool:
       results = pool.map(run_simulation, configs)
   
   # Analyze results
   for i, result in enumerate(results):
       print(f"Simulation {i}: {result['total_population']} population")

Scenario Analysis
^^^^^^^^^^^^^^^^

.. code-block:: python

   # Baseline scenario
   baseline_config = SimulationConfig(
       simulation_name="baseline",
       start_year=2020,
       n_years=10,
       pop_growth_perc=0.02
   )
   
   # High growth scenario
   high_growth_config = SimulationConfig(
       simulation_name="high_growth",
       start_year=2020,
       n_years=10,
       pop_growth_perc=0.04
   )
   
   # Run scenarios
   baseline_model = Model(baseline_config)
   baseline_model.run_simulation()
   
   high_growth_model = Model(high_growth_config)
   high_growth_model.run_simulation()
   
   # Compare results
   baseline_pop = baseline_model.get_results()['total_population']
   high_growth_pop = high_growth_model.get_results()['total_population']
   
   print(f"Baseline population: {baseline_pop}")
   print(f"High growth population: {high_growth_pop}")

Accessing Results
----------------

Network Statistics
^^^^^^^^^^^^^^^^^

.. code-block:: python

   model = Model()
   model.run_simulation()
   
   network = model.simulator.network
   
   # Basic statistics
   print(f"Total population: {network.total_population}")
   print(f"Average household income: {network.avg_hh_income}")
   print(f"Average household size: {network.avg_hh_size}")
   print(f"Total housing units: {network.total_housing_units}")

Agent Data
^^^^^^^^^^

.. code-block:: python

   # Access all household agents
   agents = network.get_institution('all_household_agents').components
   
   # Agent statistics
   agent_incomes = [agent.income for agent in agents]
   agent_locations = [agent.location for agent in agents]
   
   print(f"Number of agents: {len(agents)}")
   print(f"Average agent income: {sum(agent_incomes) / len(agent_incomes)}")

Geographic Data
^^^^^^^^^^^^^^

.. code-block:: python

   # Access block group data
   block_groups = network.nodes
   
   # Housing data by block group
   housing_df = network.housing_block_group_df
   
   # Plot population distribution
   import matplotlib.pyplot as plt
   import geopandas as gpd
   
   gdf = gpd.GeoDataFrame(housing_df, geometry='geometry')
   gdf.plot(column='population', legend=True)
   plt.title('Population Distribution')
   plt.show()

Custom Analysis
^^^^^^^^^^^^^^

.. code-block:: python

   # Custom analysis functions
   def analyze_flood_risk(model):
       network = model.simulator.network
       housing_df = network.housing_block_group_df
       
       # Calculate average flood risk by income level
       high_income_areas = housing_df[housing_df['avg_income'] > housing_df['avg_income'].median()]
       low_income_areas = housing_df[housing_df['avg_income'] <= housing_df['avg_income'].median()]
       
       high_risk = high_income_areas['flood_risk'].mean()
       low_risk = low_income_areas['flood_risk'].mean()
       
       return {
           'high_income_flood_risk': high_risk,
           'low_income_flood_risk': low_risk,
           'risk_difference': high_risk - low_risk
       }
   
   # Run analysis
   results = analyze_flood_risk(model)
   print(f"Flood risk difference: {results['risk_difference']:.3f}")

Troubleshooting
--------------

Common Issues
^^^^^^^^^^^^

**Memory Issues**
.. code-block:: python

   # For large datasets, increase agent aggregation
   config = SimulationConfig(
       agent_housing_aggregation=20,  # More households per agent
       # ... other parameters
   )

**Data Loading Errors**
.. code-block:: python

   # Check data file formats
   import pandas as pd
   import geopandas as gpd
   
   try:
       geo_data = gpd.read_file("geography.shp")
       pop_data = pd.read_csv("population.csv")
       print("Data files loaded successfully")
   except Exception as e:
       print(f"Data loading error: {e}")

**Simulation Errors**
.. code-block:: python

   # Enable debug mode
   config = SimulationConfig(
       debug=True,
       # ... other parameters
   )
   
   # Check for specific errors
   try:
       model = Model(config=config)
       model.run_simulation()
   except Exception as e:
       print(f"Simulation error: {e}")
       print(f"Error details: {model.error_log}")

Performance Optimization
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Optimize for speed
   config = SimulationConfig(
       agent_housing_aggregation=15,  # Reduce number of agents
       n_years=5,                     # Shorter simulation period
       # ... other parameters
   )
   
   # Use parallel processing for multiple runs
   from multiprocessing import Pool
   
   def run_optimized_simulation(config):
       model = Model(config=config)
       model.run_simulation()
       return model.get_results()

Best Practices
-------------

Configuration Management
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Use configuration files
   import yaml
   
   with open('simulation_config.yml', 'r') as f:
       config_dict = yaml.safe_load(f)
   
   config = SimulationConfig(**config_dict)
   
   # Save configurations
   config.save('my_config.yml')

Data Validation
^^^^^^^^^^^^^^

.. code-block:: python

   # Validate data before simulation
   def validate_data(geo_file, pop_file, flood_file):
       import geopandas as gpd
       import pandas as pd
       
       # Check file existence
       for file in [geo_file, pop_file, flood_file]:
           if not os.path.exists(file):
               raise FileNotFoundError(f"File not found: {file}")
       
       # Check required columns
       geo_data = gpd.read_file(geo_file)
       pop_data = pd.read_csv(pop_file)
       flood_data = pd.read_csv(flood_file)
       
       required_geo = ['GEOID', 'COUNTYFP', 'geometry']
       required_pop = ['GEOID', 'TOTAL_POPULATION']
       required_flood = ['GEOID', 'FLOOD_RISK']
       
       for col in required_geo:
           if col not in geo_data.columns:
               raise ValueError(f"Missing column in geography file: {col}")
       
       # ... similar checks for other files
       
       return True

Result Analysis
^^^^^^^^^^^^^^

.. code-block:: python

   # Systematic result analysis
   def analyze_simulation_results(model):
       results = {}
       
       # Basic statistics
       network = model.simulator.network
       results['total_population'] = network.total_population
       results['avg_income'] = network.avg_hh_income
       
       # Geographic analysis
       housing_df = network.housing_block_group_df
       results['population_by_income'] = housing_df.groupby('income_quartile')['population'].sum()
       
       # Agent analysis
       agents = network.get_institution('all_household_agents').components
       results['agent_income_distribution'] = [agent.income for agent in agents]
       
       return results

Next Steps
----------

* Explore the :doc:`api/index` for complete API documentation
* Check out :doc:`tutorials/index` for step-by-step tutorials
* See :doc:`examples/index` for practical examples
* Read :doc:`contributing` for development guidelines 