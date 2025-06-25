# ICoM ABM Command Line Interface

The ICoM ABM (Agent-Based Model) provides a comprehensive command-line interface for simulating housing market dynamics, including population growth, agent relocation, housing choice, market pricing, and environmental factors like flood hazards.

## Installation

After installing the package, the CLI will be available as `icom-abm`:

```bash
# Install the package
pip install -e .

# Verify installation
icom-abm --help
```

## Quick Start

### 1. Get Information About the Model

```bash
icom-abm info
```

### 2. Create a Configuration File

```bash
# Create a basic configuration
icom-abm create-config --template basic --output my_config.yaml

# Create a Baltimore-specific configuration
icom-abm create-config --template baltimore --output baltimore_config.yaml

# Create a custom configuration interactively
icom-abm create-config --template custom --output custom_config.yaml
```

### 3. Validate Your Configuration

```bash
icom-abm validate-config my_config.yaml
```

### 4. Run a Simulation

```bash
# Run with default parameters
icom-abm run

# Run with a configuration file
icom-abm run --config my_config.yaml

# Run a sensitivity analysis
icom-abm run --sensitivity-run --no-years 1 --output-dir ./sensitivity_results

# Run with custom parameters
icom-abm run \
    --start-year 2020 \
    --no-years 5 \
    --pop-growth-perc 0.02 \
    --perc-move 0.15 \
    --output-dir ./my_simulation
```

## Available Commands

### `run` - Execute Simulation

Runs the ICoM ABM simulation with specified parameters.

**Options:**
- `--config, -c`: Path to YAML configuration file
- `--output-dir, -o`: Output directory for results (default: `./results`)
- `--simulation-name`: Name identifier for the simulation
- `--scenario`: Scenario name (default: `Baseline`)
- `--intervention`: Intervention type (default: `Baseline`)
- `--start-year`: Starting year (default: `2018`)
- `--no-years`: Number of years to simulate (default: `2`)
- `--agent-housing-aggregation`: Households per agent (default: `10`)
- `--hh-size`: Average household size (default: `2.7`)
- `--initial-vacancy`: Initial vacancy rate (default: `0.20`)
- `--pop-growth-perc`: Population growth percentage (default: `0.01`)
- `--perc-move`: Percentage of agents that move (default: `0.10`)
- `--sensitivity-run`: Run in sensitivity analysis mode
- `--record-time`: Record timing information
- `--progress`: Show progress indicators

**Example:**
```bash
icom-abm run \
    --config my_config.yaml \
    --output-dir ./simulation_results \
    --start-year 2020 \
    --no-years 10 \
    --pop-growth-perc 0.015 \
    --progress
```

### `validate-config` - Validate Configuration

Validates a YAML configuration file and displays the parameters.

**Arguments:**
- `config_file`: Path to the configuration file to validate

**Options:**
- `--output, -o`: Output file for validation report

**Example:**
```bash
icom-abm validate-config my_config.yaml --output validation_report.txt
```

### `create-config` - Create Configuration File

Creates a new configuration file from a template.

**Options:**
- `--template, -t`: Template to use (`basic`, `baltimore`, `custom`)
- `--output, -o`: Output file path (default: `config.yaml`)

**Example:**
```bash
icom-abm create-config --template baltimore --output baltimore_simulation.yaml
```

### `plot-results` - Generate Visualizations

Generates plots from simulation results.

**Arguments:**
- `results_dir`: Directory containing simulation results

**Options:**
- `--output, -o`: Output file path for the plot
- `--format`: Output format (`png`, `pdf`, `svg`, `jpg`)
- `--dpi`: DPI for the output image (default: `300`)

**Example:**
```bash
icom-abm plot-results ./simulation_results --output population_map.png --format png
```

### `summarize` - Generate Summary Report

Creates a comprehensive summary of simulation results.

**Arguments:**
- `results_dir`: Directory containing simulation results

**Options:**
- `--format`: Output format (`csv`, `json`, `excel`)
- `--output, -o`: Output file path for the summary

**Example:**
```bash
icom-abm summarize ./simulation_results --format csv --output summary.csv
```

### `info` - Display Model Information

Shows version information, features, and usage instructions.

**Example:**
```bash
icom-abm info
```

## Global Options

All commands support these global options:

- `--verbose, -v`: Enable verbose logging
- `--quiet, -q`: Suppress output except errors
- `--version`: Show version information
- `--help`: Show help message

## Configuration Files

Configuration files are in YAML format and contain all simulation parameters. You can create them using the `create-config` command or manually.

**Example configuration structure:**
```yaml
simulation_name: "ABM_Baltimore_example"
scenario: "Baseline"
intervention: "Baseline"
start_year: 2018
no_years: 2
agent_housing_aggregation: 10
hh_size: 2.7
initial_vacancy: 0.20
pop_growth_mode: "perc"
pop_growth_perc: 0.01
# ... additional parameters
```

## Output Structure

When you run a simulation, the following structure is created:

```
output_directory/
├── simulation_config.yaml    # Configuration used for the simulation
├── logs/                     # Simulation logs (if enabled)
└── results/                  # Simulation results
    ├── housing_data.csv      # Housing market data
    ├── population_data.csv   # Population statistics
    ├── agent_data.csv        # Agent behavior data
    └── plots/                # Generated visualizations
```

## Examples

### Basic Simulation
```bash
# Run a simple 2-year simulation
icom-abm run --output-dir ./basic_simulation
```

### Sensitivity Analysis
```bash
# Run multiple sensitivity scenarios
for growth_rate in 0.005 0.01 0.015 0.02; do
    icom-abm run \
        --sensitivity-run \
        --pop-growth-perc $growth_rate \
        --output-dir "./sensitivity_${growth_rate}" \
        --no-years 1
done
```

### Custom Configuration
```bash
# Create and use a custom configuration
icom-abm create-config --template custom --output my_simulation.yaml
# Edit the configuration file as needed
icom-abm run --config my_simulation.yaml --output-dir ./custom_simulation
```

### Batch Processing
```bash
# Run multiple scenarios
scenarios=("baseline" "high_growth" "low_growth")
for scenario in "${scenarios[@]}"; do
    icom-abm run \
        --scenario "$scenario" \
        --output-dir "./results_${scenario}" \
        --pop-growth-perc 0.01
done
```

## Troubleshooting

### Common Issues

1. **Configuration file not found**
   ```bash
   # Make sure the file exists and path is correct
   ls -la my_config.yaml
   icom-abm validate-config my_config.yaml
   ```

2. **Permission errors**
   ```bash
   # Check write permissions for output directory
   mkdir -p ./results
   chmod 755 ./results
   ```

3. **Memory issues with large simulations**
   ```bash
   # Reduce agent aggregation or simulation years
   icom-abm run --agent-housing-aggregation 20 --no-years 1
   ```

### Getting Help

```bash
# General help
icom-abm --help

# Command-specific help
icom-abm run --help
icom-abm validate-config --help

# Verbose output for debugging
icom-abm run --verbose --config my_config.yaml
```

## Advanced Usage

### Programmatic CLI Usage

You can also use the CLI programmatically:

```python
import subprocess

# Run a simulation
result = subprocess.run([
    'icom-abm', 'run',
    '--config', 'my_config.yaml',
    '--output-dir', './results'
], capture_output=True, text=True)

print(result.stdout)
```

### Custom Scripts

Create custom scripts that use the CLI:

```bash
#!/bin/bash
# run_multiple_scenarios.sh

for year in 2018 2019 2020; do
    for growth in 0.01 0.02 0.03; do
        icom-abm run \
            --start-year $year \
            --pop-growth-perc $growth \
            --output-dir "./results_${year}_${growth}"
    done
done
```

## Contributing

To extend the CLI with new commands or options:

1. Edit `chance_c/cli.py`
2. Add new Click commands as needed
3. Update this documentation
4. Test your changes thoroughly

For more information about the ICoM ABM model, see the main README.md file. 