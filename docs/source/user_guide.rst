User Guide
==========

Welcome to the CHANCE-C User Guide! This guide provides comprehensive information about CHANCE-C's capabilities, concepts, and best practices for urban development modeling.

What is CHANCE-C?
-----------------

CHANCE-C (Coastal Hazards And Neighborhood Change - Computational) is an agent-based modeling framework specifically designed for simulating urban development dynamics in coastal environments subject to flood hazards. It integrates multiple complex systems:

- **Individual Decision-Making**: Household agents making housing choices
- **Housing Market Dynamics**: Supply, demand, pricing, and development
- **Environmental Hazards**: Flood risk and extreme weather impacts
- **Policy Interventions**: Zoning, regulations, and adaptation strategies
- **Spatial Interactions**: Geographic relationships and neighborhood effects

Core Concepts
-------------

Agent-Based Modeling
~~~~~~~~~~~~~~~~~~~~

CHANCE-C uses agent-based modeling (ABM) to simulate complex urban systems. In ABM:

- **Agents** are individual entities (households, developers, institutions) that make decisions
- **Environment** is the spatial and social context in which agents operate
- **Interactions** between agents and environment create emergent system-level behaviors
- **Time** progresses in discrete steps, allowing dynamic evolution

**Why Agent-Based Modeling?**

Traditional urban models often use aggregate approaches that may miss important individual behaviors and interactions. ABM allows us to:

- Model heterogeneous agents with different preferences and constraints
- Capture spatial relationships and neighborhood effects
- Study emergent phenomena that arise from individual decisions
- Test policy interventions at the agent level

Spatial Structure
~~~~~~~~~~~~~~~~

CHANCE-C organizes space using census block groups as the fundamental spatial unit:

- **Block Groups**: Geographic areas containing housing units and population
- **Networks**: Connections between block groups for agent movement
- **Attributes**: Each block group has characteristics like flood risk, amenities, and housing stock

Agents and Institutions
~~~~~~~~~~~~~~~~~~~~~~

**Household Agents**
  Individual households that make housing decisions based on:
  
  - Income and budget constraints
  - Preferences for location attributes
  - Risk tolerance for flood hazards
  - Household size and composition

**Institutional Agents**
  Organizations that make collective decisions:
  
  - **Real Estate**: Manages housing development and sales
  - **Zoning Managers**: Implement land use regulations
  - **Government Agencies**: Coordinate policy interventions

Simulation Engines
~~~~~~~~~~~~~~~~~

CHANCE-C uses modular engines that execute specific behaviors each time step:

**Population Dynamics**
  - New agent creation (population growth)
  - Agent lifecycle and demographic changes

**Housing Decisions**
  - Existing agent relocation decisions
  - New agent location choices
  - Housing market transactions

**Market Dynamics**
  - Housing supply and demand
  - Price adjustments
  - New construction and development

**Environmental Impacts**
  - Flood hazard assessment
  - Risk perception and adaptation
  - Climate change effects

**Policy Implementation**
  - Zoning and land use regulations
  - Intervention scenarios
  - Regulatory compliance

Key Features
-----------

Flexible Data Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

CHANCE-C supports various data formats and sources:

**Geographic Data**
  - Shapefiles for spatial boundaries
  - Census data for demographics
  - FEMA flood maps for hazard assessment

**Demographic Data**
  - Population counts and characteristics
  - Income distributions
  - Household composition

**Housing Data**
  - Housing stock characteristics
  - Price and value information
  - Vacancy rates and turnover

**Economic Data**
  - Hedonic pricing models
  - Market transaction data
  - Development costs

Field Mapping System
~~~~~~~~~~~~~~~~~~~

CHANCE-C includes a powerful field mapping system that allows you to use data with different column names without modifying your source files:

.. code-block:: yaml

   geo_file_mapping:
     GEOID: 'CENSUS_BLOCK_GROUP_ID'
     COUNTYFP: 'COUNTY_CODE'
   
   pop_file_mapping:
     AJWME001: 'TOTAL_POPULATION'
     AJWNE001: 'TOTAL_HOUSEHOLDS'

This flexibility enables integration with diverse data sources and formats.

Scenario Analysis
~~~~~~~~~~~~~~~~

CHANCE-C supports comprehensive scenario analysis:

**Baseline Scenarios**
  - Current conditions and trends
  - Historical validation
  - Reference case for comparisons

**Policy Scenarios**
  - Zoning changes and regulations
  - Infrastructure investments
  - Incentive programs

**Climate Scenarios**
  - Sea level rise projections
  - Increased flood frequency
  - Extreme weather events

**Development Scenarios**
  - Population growth variations
  - Economic development patterns
  - Land use changes

Modeling Workflow
----------------

A typical CHANCE-C modeling workflow follows these steps:

1. **Data Preparation**
   - Gather required input data
   - Create field mappings if needed
   - Validate data quality and completeness

2. **Model Configuration**
   - Set simulation parameters
   - Define scenario conditions
   - Configure agent behaviors

3. **Model Calibration**
   - Adjust parameters to match historical data
   - Validate model outputs
   - Conduct sensitivity analysis

4. **Scenario Simulation**
   - Run baseline and alternative scenarios
   - Compare outcomes across scenarios
   - Analyze policy impacts

5. **Results Analysis**
   - Visualize spatial and temporal patterns
   - Quantify scenario differences
   - Interpret policy implications

Best Practices
--------------

Model Design
~~~~~~~~~~~~

**Start Simple**
  Begin with basic scenarios and gradually add complexity. This helps identify key relationships and validate model behavior.

**Use Default Data First**
  Familiarize yourself with CHANCE-C using the included example data before working with your own datasets.

**Document Everything**
  Keep detailed records of:
  - Configuration parameters
  - Data sources and processing steps
  - Modeling assumptions and decisions
  - Results and interpretations

Data Management
~~~~~~~~~~~~~~

**Data Quality**
  - Verify data accuracy and completeness
  - Check for missing values and outliers
  - Ensure spatial and temporal consistency
  - Validate against independent sources

**Field Mapping**
  - Use descriptive field names in mappings
  - Document the meaning of each field
  - Test mappings with small datasets first
  - Keep mapping files under version control

**Backup and Version Control**
  - Maintain backups of all data files
  - Use version control for configuration files
  - Document changes and their rationale
  - Archive results for reproducibility

Simulation Configuration
~~~~~~~~~~~~~~~~~~~~~~~

**Parameter Selection**
  - Base parameters on empirical evidence when possible
  - Document sources and assumptions
  - Conduct sensitivity analysis for key parameters
  - Consider parameter uncertainty

**Agent Aggregation**
  - Balance computational efficiency with model detail
  - Start with higher aggregation for testing
  - Reduce aggregation for final analysis
  - Document aggregation effects

**Temporal Resolution**
  - Choose appropriate time steps for your research question
  - Consider seasonal and cyclical patterns
  - Balance detail with computational requirements
  - Validate temporal dynamics

Results Analysis
~~~~~~~~~~~~~~~

**Validation**
  - Compare model outputs to observed data
  - Test model behavior under extreme conditions
  - Verify that results make intuitive sense
  - Conduct cross-validation with independent datasets

**Uncertainty Analysis**
  - Run multiple model realizations
  - Vary key parameters within reasonable ranges
  - Report confidence intervals where appropriate
  - Discuss limitations and uncertainties

**Visualization**
  - Use appropriate visualization techniques
  - Show spatial and temporal patterns
  - Highlight key findings and insights
  - Make visualizations accessible to stakeholders

Common Use Cases
---------------

Urban Planning
~~~~~~~~~~~~~~

**Land Use Planning**
  - Evaluate zoning alternatives
  - Assess development capacity
  - Analyze transportation impacts
  - Study neighborhood change patterns

**Infrastructure Planning**
  - Assess service demand
  - Evaluate infrastructure investments
  - Study accessibility improvements
  - Plan for population growth

Climate Adaptation
~~~~~~~~~~~~~~~~~

**Flood Risk Assessment**
  - Model flood impacts on housing markets
  - Evaluate adaptation strategies
  - Study risk perception and behavior
  - Assess equity implications

**Sea Level Rise Planning**
  - Project long-term impacts
  - Evaluate retreat strategies
  - Study adaptation pathways
  - Plan for managed relocation

Policy Analysis
~~~~~~~~~~~~~~

**Housing Policy**
  - Evaluate affordable housing programs
  - Study gentrification and displacement
  - Assess housing market interventions
  - Analyze equity outcomes

**Environmental Policy**
  - Study environmental justice impacts
  - Evaluate green infrastructure
  - Assess pollution reduction strategies
  - Analyze ecosystem service values

Research Applications
~~~~~~~~~~~~~~~~~~~~

**Academic Research**
  - Test theoretical hypotheses
  - Conduct comparative studies
  - Develop new modeling approaches
  - Publish peer-reviewed research

**Applied Research**
  - Support decision-making processes
  - Evaluate program effectiveness
  - Conduct impact assessments
  - Inform policy development

Performance Considerations
---------------------------

Computational Efficiency
~~~~~~~~~~~~~~~~~~~~~~~~~

**Agent Aggregation**
  Higher aggregation (fewer agents) reduces computation time but may lose detail.

**Spatial Resolution**
  Larger spatial units reduce complexity but may miss important local effects.

**Temporal Resolution**
  Longer time steps reduce computation but may miss important dynamics.

**Model Complexity**
  Simpler models run faster but may not capture all relevant processes.

Memory Management
~~~~~~~~~~~~~~~~

**Large Datasets**
  - Process data in chunks when possible
  - Use efficient data structures
  - Monitor memory usage
  - Consider distributed computing for very large models

**Result Storage**
  - Save only necessary outputs
  - Use compressed file formats
  - Implement incremental saving
  - Clean up temporary files

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

**Slow Performance**
  - Reduce agent aggregation
  - Simplify model configuration
  - Check for infinite loops
  - Monitor system resources

**Memory Errors**
  - Reduce dataset size
  - Increase system memory
  - Use data chunking
  - Optimize data structures

**Convergence Issues**
  - Check parameter values
  - Verify model logic
  - Reduce time step size
  - Add stability constraints

**Unexpected Results**
  - Verify input data
  - Check configuration parameters
  - Review model assumptions
  - Conduct sensitivity analysis

Getting Help
~~~~~~~~~~~

**Documentation**
  - Review tutorials and examples
  - Check API documentation
  - Read user guide sections
  - Consult troubleshooting guides

**Community Support**
  - Post questions in GitHub Discussions
  - Report bugs in GitHub Issues
  - Join user community forums
  - Attend workshops and conferences

**Professional Support**
  - Consult with model developers
  - Hire experienced practitioners
  - Collaborate with research institutions
  - Engage professional services

Advanced Topics
--------------

Model Extension
~~~~~~~~~~~~~~

CHANCE-C is designed to be extensible. Advanced users can:

- Create custom agent types
- Develop new simulation engines
- Implement specialized behaviors
- Integrate external models

For detailed information on extending CHANCE-C, see :doc:`tutorials/custom_simulations`.

Integration with Other Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~

CHANCE-C can be integrated with:

- **GIS Software**: For spatial analysis and visualization
- **Statistical Software**: For advanced analytics
- **Optimization Tools**: For parameter calibration
- **Visualization Tools**: For interactive dashboards

High-Performance Computing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For large-scale simulations, CHANCE-C can be deployed on:

- **Cluster Computing**: Distributed simulation runs
- **Cloud Computing**: Scalable computing resources
- **GPU Computing**: Accelerated computation
- **Parallel Processing**: Multi-core execution

Next Steps
----------

After reading this user guide:

1. **Try the Tutorials**: Work through :doc:`tutorials/index` for hands-on experience
2. **Explore Examples**: Check :doc:`examples/index` for specific use cases
3. **Review API Documentation**: See :doc:`api/index` for detailed technical information
4. **Join the Community**: Participate in discussions and contribute to development

For specific questions about your use case, consider:

- Reviewing similar published studies
- Consulting with domain experts
- Engaging with the CHANCE-C community
- Seeking professional collaboration 