Changelog
=========

All notable changes to CHANCE-C will be documented in this file.

[Unreleased]
------------

Added
^^^^^
* Initial release of CHANCE-C framework
* Agent-based modeling capabilities
* Housing market simulation
* Environmental hazard integration
* Geospatial data handling
* Comprehensive test suite
* Documentation website

Changed
^^^^^^^
* None

Deprecated
^^^^^^^^^
* None

Removed
^^^^^^^
* None

Fixed
^^^^^
* None

[1.0.0] - 2024-01-01
--------------------

Added
^^^^^
* Core Model class for simulation management
* ICOMSimulator for main simulation engine
* ABMLandscape for geographic and demographic data
* HouseholdAgent for individual household modeling
* BlockGroup for census block group representation
* CountyZoningManager for policy interventions
* RealEstate for market and development agents
* Model engines for various simulation components:
  * NewAgentCreation
  * ExistingAgentReloSampler
  * NewAgentLocation
  * ExistingAgentLocation
  * HousingMarket
  * BuildingDevelopment
  * HousingPricing
  * FloodHazard
  * Zoning
  * LandscapeStatistics
* Configuration management with SimulationConfig
* Field mapping system for data flexibility
* Data loading utilities for multiple formats
* CLI interface for command-line usage
* Comprehensive test suite with 94+ tests
* Documentation website with Sphinx
* GitHub Actions CI/CD pipeline

Changed
^^^^^^^
* None

Deprecated
^^^^^^^^^
* None

Removed
^^^^^^^
* None

Fixed
^^^^^
* None 