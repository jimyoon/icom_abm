# Random Seed Control in ICoM ABM

This document explains how to use the random seed functionality in the ICoM Agent-Based Model to ensure reproducible simulation results.

## Overview

The ICoM ABM includes various randomized processes such as:
- Agent creation and relocation
- Housing choice decisions
- Market dynamics
- Environmental hazard assessments

By setting a random seed, you can ensure that these processes produce identical results across multiple simulation runs, which is essential for:
- Debugging and testing
- Sensitivity analysis
- Reproducible research
- Model validation

## How to Set Random Seeds

### Method 1: Direct Parameter in Model Constructor

```python
from chance_c import Model

# Create model with random seed
model = Model(
    simulation_name="my_simulation",
    start_year=2018,
    n_years=5,
    random_seed=42  # Set seed directly
)
model.run_simulation()
```

### Method 2: Using SimulationConfig Object

```python
from chance_c import Model, SimulationConfig

# Create config with random seed
config = SimulationConfig(
    simulation_name="my_simulation",
    start_year=2018,
    n_years=5,
    random_seed=123  # Set seed in config
)

# Create model with config
model = Model(config=config)
model.run_simulation()
```

### Method 3: YAML Configuration File

```yaml
# config.yml
simulation_name: "my_simulation"
start_year: 2018
n_years: 5
random_seed: 456
```

```python
from chance_c import Model

# Load model from YAML file
model = Model(config_file_path="config.yml")
model.run_simulation()
```

### Method 4: Override Config Seed

```python
from chance_c import Model, SimulationConfig

# Create config with one seed
config = SimulationConfig(
    simulation_name="my_simulation",
    start_year=2018,
    n_years=5,
    random_seed=789
)

# Override the seed when creating model
model = Model(config=config, random_seed=999)
model.run_simulation()
```

## Verification

To verify that the random seed is working correctly, run the same simulation multiple times with the same seed:

```python
from chance_c import Model

# Run simulation twice with same seed
model1 = Model(simulation_name="test1", random_seed=42)
model1.run_simulation()
result1 = model1.get_history('total_population')[-1]

model2 = Model(simulation_name="test2", random_seed=42)
model2.run_simulation()
result2 = model2.get_history('total_population')[-1]

print(f"Result 1: {result1}")
print(f"Result 2: {result2}")
print(f"Results identical: {result1 == result2}")  # Should be True
```

## Technical Details

### What Gets Seeded

The random seed controls:
- Python's `random` module
- NumPy's random number generator (`np.random`)

This ensures that all randomized processes in the simulation use the same sequence of random numbers.

### When the Seed is Set

The random seed is set:
1. During Model initialization (if provided)
2. At the start of `run_simulation()` (if configured)

This ensures that the seed is active before any random operations occur.

### Seed Values

- **Integer values**: Any integer can be used as a seed
- **None**: No seed is set, resulting in random behavior
- **Reproducibility**: Same seed always produces same results on the same system

## Best Practices

1. **Document your seeds**: Always record which seed values you use in your research
2. **Use different seeds**: For sensitivity analysis, use different seeds to explore parameter space
3. **Test reproducibility**: Verify that your results are reproducible with the same seed
4. **Version control**: Include seed values in your configuration files for version control

## Example Scripts

See the following example scripts in the `scripts/` directory:
- `random_seed_example.py`: Basic usage examples
- `test_random_seed.py`: Verification and testing

## Troubleshooting

### Results Still Vary

If you're still getting different results with the same seed:
1. Check that the seed is being set correctly: `print(model.config.random_seed)`
2. Ensure no other code is setting random seeds elsewhere
3. Verify that you're using the same version of Python and dependencies

### Performance Impact

Setting a random seed has negligible performance impact and is recommended for all production simulations.

## API Reference

### Model Class

```python
Model(
    # ... other parameters ...
    random_seed: Union[int, None] = None
)
```

### SimulationConfig Class

```python
SimulationConfig(
    # ... other parameters ...
    random_seed: Union[int, None] = None
)
```

### Utility Function

```python
from chance_c.utils import set_random_seed

set_random_seed(seed: Union[int, None]) -> None
``` 