# CHANCE-C: Agent-Based Modeling Framework for Coastal Urban Development

[![test](https://github.com/jimyoon/icom_abm/actions/workflows/build.yml/badge.svg)](https://github.com/jimyoon/icom_abm/actions/workflows/build.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-BSD--2--Clause-green.svg)](LICENSE)

CHANCE-C (Coastal Hazards And Neighborhood Change - Computational) is a comprehensive agent-based modeling framework designed to simulate urban development dynamics in flood-prone coastal environments. The framework integrates household decision-making, housing market dynamics, environmental hazards, and policy interventions.

## Features

- **Agent-Based Modeling**: Simulates individual household agents with realistic decision-making
- **Housing Market Dynamics**: Models supply, demand, pricing, and development
- **Environmental Hazards**: Integrates flood risk and climate change impacts
- **Policy Analysis**: Supports scenario testing and intervention evaluation
- **Geospatial Integration**: Built on robust geospatial data handling
- **Modular Architecture**: Extensible framework for custom simulations
- **Comprehensive Testing**: Full test suite with 94+ tests and CI/CD pipeline

## Requirements

- Python 3.11+
- GDAL/OGR libraries
- PROJ (Projection library)
- GEOS (Geometry library)

## Installation

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
  libgdal-dev \
  gdal-bin \
  libproj-dev \
  proj-data \
  proj-bin \
  libgeos-dev \
  libspatialindex-dev
```

**macOS:**
```bash
brew install gdal proj geos
```

**Windows:**
Install GDAL, PROJ, and GEOS through OSGeo4W or conda-forge.

### Python Package

```bash
# Clone the repository
git clone https://github.com/your-org/icom_abm.git
cd icom_abm

# Install in development mode
pip install -e .

# Or install from PyPI (when available)
pip install chance-c
```

## Quick Start

### Basic Usage

```python
from chance_c import Model, SimulationConfig

# Create a model with default settings
model = Model()

# Run simulation
model.run_simulation()

# Access results
print(f"Total population: {model.simulator.network.total_population}")
```

### Custom Configuration

```python
from chance_c import Model, SimulationConfig

# Create custom configuration
config = SimulationConfig(
    simulation_name="my_simulation",
    start_year=2020,
    n_years=5,
    pop_growth_perc=0.02,
    landscape_name="Baltimore"
)

# Create model with custom config
model = Model(config=config)
model.run_simulation()
```

### Using Your Own Data

```python
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
```

## Core Components

### Model Classes

- **`ICOMSimulator`**: Main simulation engine
- **`ABMLandscape`**: Geographic and demographic landscape
- **`HouseholdAgent`**: Individual household agents
- **`BlockGroup`**: Census block group nodes
- **`CountyZoningManager`**: Policy and regulatory agents
- **`RealEstate`**: Market and development agents

### Model Engines

- **`NewAgentCreation`**: Population growth and new household formation
- **`ExistingAgentReloSampler`**: Household relocation decisions
- **`NewAgentLocation`**: Residential choice for new households
- **`ExistingAgentLocation`**: Relocation for existing households
- **`HousingMarket`**: Buyer-seller matching and transactions
- **`BuildingDevelopment`**: New construction and development
- **`HousingPricing`**: Price dynamics and market updates
- **`FloodHazard`**: Environmental risk assessment
- **`Zoning`**: Regulatory and policy interventions
- **`LandscapeStatistics`**: Data collection and analysis

### Data Management

- **`SimulationConfig`**: Configuration management
- **`FieldMapper`**: Data field mapping and transformation
- **Data Loading**: Support for CSV, Shapefile, and other formats

## Configuration

### Simulation Parameters

```python
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
    inc_growth_mode="random_agent_replication",
    
    # Market settings
    house_choice_mode="simple_avoidance_utility",
    house_budget_mode="rhea",
    perc_move=0.10,
    
    # Environmental settings
    simple_avoidance_perc=0.95,
    budget_reduction_perc=0.90,
    
    # Development settings
    stock_increase_mode="simple_perc",
    stock_increase_perc=0.05,
    
    # Data files
    geo_filename="geography.shp",
    pop_filename="population.csv",
    flood_filename="flood_data.csv",
    housing_filename="housing_data.csv",
    hedonic_filename="hedonic_data.csv"
)
```

### Field Mapping

For data with different column names, use the field mapping system:

```python
from chance_c import FieldMapper

# Create field mappings
mappings = {
    'geo_file_mapping': {
        'GEOID': 'CENSUS_ID',
        'COUNTYFP': 'COUNTY_CODE'
    },
    'pop_file_mapping': {
        'AJWME001': 'TOTAL_POPULATION'
    }
}

# Use in configuration
config = SimulationConfig(
    field_mappings=mappings,
    # ... other parameters
)
```

## Testing

The package includes a comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_config.py
pytest tests/test_model_classes.py
pytest tests/test_model_engines.py

# Run with coverage
pytest tests/ --cov=chance_c --cov-report=html

# Run linting
flake8 chance_c/ tests/
black --check chance_c/ tests/
```

## Output and Analysis

### Accessing Results

```python
# After running simulation
model = Model()
model.run_simulation()

# Access network and components
network = model.simulator.network
households = network.get_institution('all_household_agents').components
block_groups = network.nodes

# Get statistics
total_population = network.total_population
avg_income = network.avg_hh_income
avg_household_size = network.avg_hh_size

# Access housing data
housing_df = network.housing_block_group_df
```

### Visualization

```python
import matplotlib.pyplot as plt
import geopandas as gpd

# Plot population distribution
housing_df = model.simulator.network.housing_block_group_df
gdf = gpd.GeoDataFrame(housing_df, geometry='geometry')

fig, ax = plt.subplots(1, 1, figsize=(12, 8))
gdf.plot(column='population', ax=ax, legend=True)
plt.title('Population Distribution')
plt.show()
```

## Custom Simulations

### Creating Custom Agents

```python
from chance_c.model_classes.urban_agents import HouseholdAgent

class CustomHouseholdAgent(HouseholdAgent):
    def __init__(self, name, location, income, **kwargs):
        super().__init__(name, location, income, **kwargs)
        self.custom_attribute = "custom_value"
    
    def custom_decision_method(self):
        # Implement custom decision logic
        pass
```

### Creating Custom Engines

```python
from chance_c.model_engines.base import BaseEngine

class CustomEngine(BaseEngine):
    def __init__(self, target):
        super().__init__(target)
    
    def run(self):
        # Implement custom simulation logic
        pass
```

### Using Custom Components

```python
from chance_c import Model

# Create model with custom components
model = Model()

# Add custom engine
custom_engine = CustomEngine(model.simulator.network)
model.simulator.add_engine(custom_engine)

# Run simulation
model.run_simulation()
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/your-org/icom_abm.git
cd icom_abm
pip install -e .

# Install development dependencies
pip install pytest pytest-cov flake8 black isort mypy

# Run tests
pytest tests/

# Format code
black chance_c/ tests/
isort chance_c/ tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Documentation

- [API Documentation](docs/api.md)
- [Tutorial: Custom Simulations](notebooks/tutorial_custom_simulations.ipynb)
- [Field Mapping Guide](docs/field_mapping.md)
- [Configuration Reference](docs/configuration.md)

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/icom_abm/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/icom_abm/discussions)
- **Email**: support@chance-c.org

## Acknowledgments

- Built on the [pynsim](https://github.com/pynsim/pynsim) framework
- Uses [geopandas](https://geopandas.org/) for geospatial data handling
- Integrates with [FEMA flood data](https://www.fema.gov/flood-maps)
- Developed with support from [funding organization]

---

**CHANCE-C** - Coastal Hazards And Neighborhood Change - Computational

*Empowering coastal communities through computational modeling*
