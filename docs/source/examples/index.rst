Examples
========

This section provides practical examples of using CHANCE-C for different applications and use cases.

.. toctree::
   :maxdepth: 2
   :caption: Example Applications

   basic_usage
   custom_data
   scenario_analysis

Example Categories
------------------

Getting Started Examples
~~~~~~~~~~~~~~~~~~~~~~~~~

Perfect for new users learning CHANCE-C basics:

- :doc:`basic_usage` - Simple simulations with default settings
- Running your first model
- Understanding basic outputs
- Simple parameter modifications

Data Integration Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~

Learn to work with your own data:

- :doc:`custom_data` - Using custom datasets
- Field mapping for different data formats
- Data preparation and validation
- Handling missing or incomplete data

Advanced Analysis Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sophisticated modeling applications:

- :doc:`scenario_analysis` - Comparing multiple scenarios
- Policy intervention analysis
- Climate change impact assessment
- Sensitivity analysis and uncertainty quantification

Interactive Examples
--------------------

All examples are available as interactive Jupyter notebooks in the repository:

.. code-block:: bash

   # Clone repository to access notebooks
   git clone https://github.com/jimyoon/icom_abm.git
   cd icom_abm
   
   # Install with examples
   pip install -e .[dev]
   
   # Start Jupyter
   jupyter notebook

Example Scripts
---------------

The ``scripts/`` directory contains additional examples:

**Basic Examples**
  - ``abm_baltimore_example.py`` - Complete simulation script
  - ``cli_example.py`` - Command-line interface usage

**Advanced Examples**
  - ``abm_baltimore_example_parallel.py`` - Parallel processing
  - ``abm_baltimore_example_PIC_slurm.py`` - HPC cluster deployment

**Pre-processing**
  - ``pre_processing/flood_risk_calcs.py`` - Flood risk calculations
  - ``pre_processing/subset_ms_buildings.py`` - Data subsetting

**Post-processing**
  - ``post_processing/post_processing_examples.py`` - Results analysis

Example Data
------------

CHANCE-C includes Baltimore-area example data:

**Geographic Data**
  - Census block group boundaries
  - Coordinate reference system: EPSG:4326 (WGS84)
  - Coverage: Baltimore metropolitan area

**Demographic Data**
  - 2018 population by block group
  - Household characteristics
  - Income distributions

**Housing Data**
  - 1993 housing stock characteristics
  - Median home values
  - Housing unit counts

**Environmental Data**
  - FEMA 100-year flood zone coverage
  - Flood risk percentages by block group

**Economic Data**
  - Hedonic regression coefficients
  - Price adjustment factors

Running Examples
----------------

Each example includes:

1. **Problem Description** - What the example demonstrates
2. **Learning Objectives** - What you'll learn
3. **Code Walkthrough** - Step-by-step explanation
4. **Expected Results** - What outputs to expect
5. **Variations** - How to modify for your needs

Example Template
----------------

Use this template structure for your own examples:

.. code-block:: python

   """
   CHANCE-C Example: [Title]
   
   Description: [What this example demonstrates]
   
   Learning Objectives:
   - [Objective 1]
   - [Objective 2]
   - [Objective 3]
   
   Prerequisites:
   - CHANCE-C installed
   - [Other requirements]
   """
   
   # Import required modules
   from chance_c import Model, SimulationConfig
   import pandas as pd
   import matplotlib.pyplot as plt
   
   # Example code here
   def main():
       # Create and configure model
       model = Model(
           simulation_name="Example_Simulation",
           # ... other parameters
       )
       
       # Run simulation
       model.run_simulation()
       
       # Analyze results
       network = model.simulator.network
       # ... analysis code
       
       # Visualize results
       # ... plotting code
       
   if __name__ == "__main__":
       main()

Contributing Examples
---------------------

We welcome contributions of new examples! To contribute:

1. **Choose a Topic** - Select an application area or use case
2. **Follow the Template** - Use the structure above
3. **Test Thoroughly** - Ensure code runs correctly
4. **Document Well** - Include clear explanations
5. **Submit PR** - Create a pull request with your example

**Example Ideas**
  - Specific geographic regions
  - Different policy scenarios
  - Novel analysis techniques
  - Integration with other tools
  - Specialized visualizations

**Guidelines**
  - Keep examples focused and concise
  - Use the included example data when possible
  - Include both code and explanatory text
  - Test on different systems
  - Follow Python best practices

Community Examples
------------------

Examples contributed by the community:

- **Academic Research**: Examples from published studies
- **Policy Analysis**: Real-world planning applications  
- **Method Development**: Novel modeling approaches
- **Tool Integration**: Connections with other software

*Note: Community examples are maintained by their authors and may use different versions of CHANCE-C.*

Getting Help with Examples
--------------------------

If you have questions about examples:

1. **Check Documentation** - Review the full documentation
2. **Search Issues** - Look for similar questions on GitHub
3. **Ask Questions** - Post in GitHub Discussions
4. **Report Problems** - Create issues for bugs or errors

**When Asking for Help**
  - Specify which example you're working with
  - Include error messages and system information
  - Describe what you're trying to achieve
  - Share your modified code if relevant 