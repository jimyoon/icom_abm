Tutorials
=========

Welcome to the CHANCE-C tutorials! These comprehensive guides will walk you through using CHANCE-C for various urban development modeling scenarios.

.. toctree::
   :maxdepth: 2
   :caption: Tutorial Contents

   quickstarter.ipynb
   configuration.ipynb
   custom_simulations.ipynb

Tutorial Overview
-----------------

Our tutorials are designed to take you from beginner to advanced user:

**Beginner Tutorials**
  Start here if you're new to CHANCE-C or agent-based modeling.

**Intermediate Tutorials**
  Build on the basics with more complex scenarios and customization.

**Advanced Tutorials**
  Deep dive into custom development and advanced modeling techniques.

Tutorial Structure
------------------

Each tutorial follows a consistent structure:

1. **Learning Objectives**: What you'll accomplish
2. **Prerequisites**: Required knowledge and setup
3. **Step-by-Step Instructions**: Detailed walkthrough
4. **Code Examples**: Complete, runnable code
5. **Expected Output**: What results to expect
6. **Next Steps**: Where to go from here

Getting the Most from Tutorials
--------------------------------

**Prerequisites**
  - CHANCE-C installed and working (:doc:`../installation`)
  - Basic Python knowledge
  - Familiarity with Jupyter notebooks (recommended)

**Setup**
  We recommend working through tutorials in a Jupyter notebook environment:

  .. code-block:: bash

     pip install jupyter
     jupyter notebook

**Data**
  All tutorials use the example data included with CHANCE-C, so no additional data preparation is needed.

**Support**
  If you encounter issues:
  
  - Check the :doc:`../getting_started` guide
  - Review the :doc:`../api/index` for detailed function documentation
  - Ask questions in `GitHub Discussions <https://github.com/jimyoon/icom_abm/discussions>`_

Tutorial Descriptions
---------------------

Quickstarter Tutorial
~~~~~~~~~~~~~~~~~~~~~

**File**: :doc:`quickstarter`

**Duration**: 30-45 minutes

**Level**: Beginner

Learn the fundamentals of CHANCE-C by running your first simulation. This tutorial covers:

- Creating and configuring models
- Understanding input data requirements
- Running simulations with default settings
- Accessing and interpreting results
- Basic visualization techniques

**Perfect for**: First-time users who want to get up and running quickly.

Configuration Tutorial
~~~~~~~~~~~~~~~~~~~~~~

**File**: :doc:`configuration`

**Duration**: 60-90 minutes

**Level**: Intermediate

Master CHANCE-C's powerful configuration system. This tutorial covers:

- Understanding the SimulationConfig class
- Working with YAML configuration files
- Customizing simulation parameters
- Field mapping for custom data
- Best practices for configuration management

**Perfect for**: Users ready to customize simulations for their specific needs.

Custom Simulations Tutorial
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**File**: :doc:`custom_simulations`

**Duration**: 2-3 hours

**Level**: Advanced

Learn to extend CHANCE-C with custom components. This tutorial covers:

- Understanding the simulation architecture
- Creating custom agents and behaviors
- Developing custom engines
- Integrating new components
- Advanced modeling techniques

**Perfect for**: Researchers and developers who need specialized functionality.

Interactive Notebooks
---------------------

All tutorials are available as interactive Jupyter notebooks in the repository:

- ``notebooks/quickstarter.ipynb``
- ``notebooks/configuration.ipynb``
- ``notebooks/custom.ipynb``

You can run these notebooks locally or view them online:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/jimyoon/icom_abm.git
   cd icom_abm/notebooks
   
   # Start Jupyter
   jupyter notebook

**Notebook Features:**
   - **Pre-executed outputs**: All notebooks include pre-generated outputs and visualizations
   - **Interactive code**: Modify and re-run cells to experiment with different parameters
   - **Complete examples**: Each notebook contains fully working code examples
   - **Embedded plots**: Visualizations are embedded directly in the notebook output

**Using the Documentation:**
   - **HTML version**: Read the formatted documentation with embedded outputs
   - **Download links**: Each tutorial page includes a link to download the original notebook
   - **Copy-paste ready**: All code examples can be copied directly from the documentation

Additional Resources
--------------------

**Example Scripts**
  Check the ``scripts/`` directory for additional examples:
  
  - ``scripts/abm_baltimore_example.py`` - Basic simulation script
  - ``scripts/cli_example.py`` - Command-line interface usage
  - ``scripts/post_processing/`` - Analysis and visualization examples

**API Documentation**
  For detailed function and class documentation, see :doc:`../api/index`.

**User Guide**
  For conceptual information about CHANCE-C's capabilities, see :doc:`../user_guide`.

Contributing to Tutorials
-------------------------

We welcome contributions to improve our tutorials:

1. **Report Issues**: Found an error or unclear explanation? `Open an issue <https://github.com/jimyoon/icom_abm/issues>`_
2. **Suggest Improvements**: Have ideas for new tutorials or enhancements? Start a discussion
3. **Submit Changes**: Fork the repository and submit a pull request

Tutorial Guidelines for Contributors:

- Keep examples simple and focused
- Include complete, runnable code
- Test all code examples
- Use the included example data when possible
- Follow the established tutorial structure 