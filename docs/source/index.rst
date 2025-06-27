CHANCE-C Documentation
======================

**Coastal Hazards And Neighborhood Change - Computational**

A comprehensive agent-based modeling framework designed to simulate urban development dynamics in flood-prone coastal environments.

.. image:: https://github.com/jimyoon/icom_abm/actions/workflows/build.yml/badge.svg
   :target: https://github.com/jimyoon/icom_abm/actions/workflows/build.yml
   :alt: CI Status

.. image:: https://img.shields.io/badge/python-3.11+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.11+

.. image:: https://img.shields.io/badge/license-BSD--2--Clause-green.svg
   :target: LICENSE
   :alt: BSD-2-Clause License

Overview
--------

CHANCE-C integrates household decision-making, housing market dynamics, environmental hazards, and policy interventions to provide a comprehensive framework for understanding coastal urban development patterns.

Key Features
^^^^^^^^^^^

* **Agent-Based Modeling**: Simulates individual household agents with realistic decision-making
* **Housing Market Dynamics**: Models supply, demand, pricing, and development
* **Environmental Hazards**: Integrates flood risk and climate change impacts
* **Policy Analysis**: Supports scenario testing and intervention evaluation
* **Geospatial Integration**: Built on robust geospatial data handling
* **Modular Architecture**: Extensible framework for custom simulations

Quick Start
-----------

.. code-block:: python

   from chance_c import Model, SimulationConfig

   # Create a model with default settings
   model = Model()

   # Run simulation
   model.run_simulation()

   # Access results
   print(f"Total population: {model.simulator.network.total_population}")

Installation
------------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/jimyoon/icom_abm.git
   cd icom_abm

   # Install in development mode
   pip install -e .

Requirements
^^^^^^^^^^^

* Python 3.11+
* GDAL/OGR libraries
* PROJ (Projection library)
* GEOS (Geometry library)

For detailed installation instructions, see :doc:`getting_started`.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   user_guide
   api/index
   tutorials/index
   examples/index
   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 