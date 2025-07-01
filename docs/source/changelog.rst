Changelog
=========

All notable changes to CHANCE-C will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------

Added
~~~~~
- Comprehensive documentation with pydata-sphinx-theme
- Interactive Jupyter notebook tutorials
- Detailed API reference documentation
- User guide with best practices
- Examples and use cases

Changed
~~~~~~~
- Updated documentation theme from sphinx-book-theme to pydata-sphinx-theme
- Improved README with virtual environment setup instructions
- Enhanced configuration management documentation

[0.1.0] - 2024-01-XX
--------------------

Added
~~~~~
- Initial release of CHANCE-C framework
- Agent-based modeling core functionality
- Baltimore example dataset
- Basic simulation engines:
  - NewAgentCreation
  - ExistingAgentReloSampler
  - NewAgentLocation
  - ExistingAgentLocation
  - HousingMarket
  - BuildingDevelopment
  - HousingPricing
  - FloodHazard
  - Zoning
  - LandscapeStatistics
- Model classes:
  - ICOMSimulator
  - ABMLandscape
  - HouseholdAgent
  - BlockGroup
  - CountyZoningManager
  - RealEstate
- Data management utilities:
  - DataLoader
  - FieldMapper
  - SimulationConfig
- Command-line interface
- Basic visualization capabilities
- Field mapping system for custom data
- Configuration management with YAML support
- Example scripts and notebooks
- Test suite with pytest
- Continuous integration with GitHub Actions

Changed
~~~~~~~
- N/A (initial release)

Deprecated
~~~~~~~~~~
- N/A (initial release)

Removed
~~~~~~~
- N/A (initial release)

Fixed
~~~~~
- N/A (initial release)

Security
~~~~~~~~
- N/A (initial release)

Version History
--------------

Release Timeline
~~~~~~~~~~~~~~~

- **v0.1.0** - Initial public release
- **Future releases** - See GitHub milestones for planned features

Development Process
~~~~~~~~~~~~~~~~~~

CHANCE-C follows these versioning principles:

- **Major versions** (X.0.0) - Breaking changes to public API
- **Minor versions** (0.X.0) - New features, backward compatible
- **Patch versions** (0.0.X) - Bug fixes, backward compatible

Pre-release versions may use additional identifiers:
- **Alpha** (0.1.0a1) - Early development, unstable
- **Beta** (0.1.0b1) - Feature complete, testing phase
- **Release candidate** (0.1.0rc1) - Final testing before release

Contributing to Changelog
--------------------------

When contributing to CHANCE-C, please update this changelog:

1. **Add entries** under the [Unreleased] section
2. **Use appropriate categories**:
   - Added - for new features
   - Changed - for changes in existing functionality
   - Deprecated - for soon-to-be removed features
   - Removed - for now removed features
   - Fixed - for any bug fixes
   - Security - in case of vulnerabilities

3. **Follow the format**:
   - Use bullet points for each change
   - Include brief, clear descriptions
   - Reference issues/PRs when relevant
   - Group related changes together

4. **Before release**:
   - Move [Unreleased] items to new version section
   - Add release date
   - Create new empty [Unreleased] section

Migration Guides
---------------

When upgrading between versions, consult these guides:

From 0.1.0 to Future Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Migration guides will be added as new versions are released.*

**General Upgrade Process:**

1. **Backup your work** - Save current configurations and results
2. **Check breaking changes** - Review changelog for breaking changes
3. **Update dependencies** - Install new version with ``pip install --upgrade chance_c``
4. **Test compatibility** - Run existing code with new version
5. **Update configurations** - Modify any deprecated parameters
6. **Update imports** - Change any moved or renamed modules

Breaking Changes
~~~~~~~~~~~~~~~

We strive to minimize breaking changes, but they may occur in major versions:

**Version 0.1.0**
- Initial API design (no breaking changes from previous versions)

**Future Versions**
- Breaking changes will be documented here with migration instructions

Deprecation Policy
-----------------

CHANCE-C follows these deprecation practices:

1. **Deprecation Warning** - Features marked as deprecated will issue warnings
2. **Grace Period** - Deprecated features remain functional for at least one minor version
3. **Documentation** - Deprecated features are marked in documentation
4. **Migration Path** - Alternative approaches are provided
5. **Removal** - Deprecated features are removed in the next major version

Currently Deprecated
~~~~~~~~~~~~~~~~~~~~

*No deprecated features in current version.*

Planned Deprecations
~~~~~~~~~~~~~~~~~~~~

*No planned deprecations at this time.*

Release Notes
------------

Detailed release notes for each version:

Version 0.1.0
~~~~~~~~~~~~~

**Release Date:** 2024-01-XX

**Highlights:**
- First public release of CHANCE-C
- Complete agent-based modeling framework
- Baltimore example dataset included
- Comprehensive documentation and tutorials

**New Features:**
- Full simulation pipeline from data loading to results analysis
- Modular engine architecture for extensibility
- Field mapping system for custom data integration
- Command-line interface for batch processing
- Interactive Jupyter notebooks for learning
- Built-in visualization capabilities

**Technical Details:**
- Python 3.11+ support
- Dependencies: pandas, geopandas, numpy, scipy, matplotlib
- Cross-platform compatibility (Windows, macOS, Linux)
- Comprehensive test suite
- CI/CD pipeline with GitHub Actions

**Documentation:**
- Complete API reference
- Step-by-step tutorials
- User guide with best practices
- Examples and use cases
- Installation and setup guides

**Known Issues:**
- Performance optimization ongoing for large datasets
- Memory usage can be high for detailed simulations
- Some advanced features require additional dependencies

**Acknowledgments:**
- Built on the pynsim framework
- Uses geopandas for geospatial operations
- Example data from Baltimore metropolitan area
- Community feedback and testing

Future Roadmap
-------------

Planned features for upcoming releases:

**Version 0.2.0 (Planned)**
- Performance optimizations
- Additional example datasets
- Enhanced visualization tools
- Parallel processing improvements
- Extended documentation

**Version 0.3.0 (Planned)**
- Climate change scenario support
- Advanced policy intervention tools
- Integration with external models
- Web-based interface
- Cloud deployment options

**Long-term Goals**
- Real-time data integration
- Machine learning integration
- Multi-scale modeling capabilities
- International dataset support
- Commercial licensing options

See `GitHub Issues <https://github.com/jimyoon/icom_abm/issues>`_ and 
`Milestones <https://github.com/jimyoon/icom_abm/milestones>`_ for detailed planning. 