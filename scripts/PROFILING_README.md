# CHANCE-C Performance Profiling Guide

This guide explains how to profile CHANCE-C simulations to identify performance bottlenecks and optimization opportunities.

## Overview

CHANCE-C is a complex agent-based model with multiple components that can impact performance:

- **Data Loading**: Geographic and demographic data processing
- **Agent Creation**: Converting population data to household agents
- **Engine Execution**: Housing market, agent relocation, pricing, etc.
- **Geospatial Operations**: Distance calculations, nearest neighbor searches
- **Memory Management**: Large data structures and history tracking

## Profiling Tools

### 1. Comprehensive Profiler (`profile_chance_c.py`)

The main profiling script that provides multiple analysis approaches:

```bash
# Install required dependencies
pip install memory_profiler psutil

# Run all profiling types
python scripts/profile_chance_c.py --profile-type all --iterations 3

# Run specific profiling
python scripts/profile_chance_c.py --profile-type cprofile --iterations 5
python scripts/profile_chance_c.py --profile-type components
python scripts/profile_chance_c.py --profile-type memory

# Use sensitivity mode for faster profiling
python scripts/profile_chance_c.py --sensitivity-run
```

**Outputs:**
- `cprofile_stats.prof`: Detailed profiling data (view with `snakeviz`)
- `cprofile_report.txt`: Human-readable function-level analysis
- `component_times.txt`: Timing breakdown by simulation component
- `memory_profile.txt`: Memory usage analysis
- `profiling_summary.txt`: Overall summary and recommendations

### 2. Line-by-Line Profiler (`line_profile_chance_c.py`)

For detailed analysis of specific functions:

```bash
# Install line_profiler
pip install line_profiler

# Profile entire simulation
python scripts/line_profile_chance_c.py

# Profile specific function
python scripts/line_profile_chance_c.py --function HousingMarket

# Save results to file
python scripts/line_profile_chance_c.py --output-file detailed_profile.txt
```

**Available functions:**
- `run_simulation`: Main simulation loop
- `set_landscape`: Data loading and processing
- `convert_agents`: Agent creation
- `init_housing`: Housing initialization
- `HousingMarket`: Housing market engine
- `NewAgentLocation`: New agent placement
- `ExistingAgentLocation`: Agent relocation

### 3. Performance Benchmarking (`benchmark_chance_c.py`)

Compare performance across different configurations:

```bash
# Run standard benchmarks
python scripts/benchmark_chance_c.py --config standard

# Compare agent aggregation levels
python scripts/benchmark_chance_c.py --config aggregation

# Compare sample sizes
python scripts/benchmark_chance_c.py --config sample_size

# Run all benchmarks
python scripts/benchmark_chance_c.py --config all --iterations 5
```

## Common Performance Bottlenecks

### 1. **Data Loading and Processing**
- **Issue**: Large geographic files and data type conversions
- **Location**: `ICOMSimulator.set_landscape()`
- **Optimization**: Pre-process data files, use appropriate data types

### 2. **Nearest Neighbor Calculations**
- **Issue**: O(n²) distance calculations for missing data
- **Location**: `set_landscape()` method, lines with `distance(location)`
- **Optimization**: Spatial indexing, pre-compute distances

### 3. **Housing Market Engine**
- **Issue**: Iterative matching between households and block groups
- **Location**: `HousingMarket.run()`
- **Optimization**: Vectorize operations, use NumPy arrays

### 4. **Agent Location Engines**
- **Issue**: Repeated utility calculations and sampling
- **Location**: `NewAgentLocation.run()`, `ExistingAgentLocation.run()`
- **Optimization**: Cache utility values, optimize sampling algorithms

### 5. **Memory Usage**
- **Issue**: Large data structures and history tracking
- **Location**: Throughout simulation
- **Optimization**: Use generators, clear unused data, optimize data structures

## Optimization Strategies

### 1. **Configuration Optimizations**

```python
# Faster simulation for testing
model = Model(
    sensitivity_run=True,  # Skip some engines
    n_years=2,            # Shorter simulation
    record_time=False,    # Disable timing
    progress=False        # Disable progress bars
)

# Optimize for speed vs accuracy
model = Model(
    agent_housing_aggregation=20,    # Higher aggregation = faster
    block_group_sample_size=5,       # Smaller samples = faster
    perc_move=0.05                   # Fewer moving agents = faster
)
```

### 2. **Data Structure Optimizations**

```python
# Use NumPy arrays instead of lists where possible
import numpy as np

# Vectorize operations
prices = np.array([bg.new_price for bg in block_groups])
utilities = np.vectorize(calculate_utility)(prices, incomes, flood_risks)

# Use spatial indexing for distance calculations
from scipy.spatial import cKDTree
tree = cKDTree(centroids)
distances, indices = tree.query(target_point)
```

### 3. **Algorithm Optimizations**

```python
# Cache expensive calculations
@lru_cache(maxsize=1000)
def calculate_utility(price, income, flood_risk):
    return price * income * (1 - flood_risk)

# Use efficient data structures
from collections import defaultdict
block_group_demand = defaultdict(list)

# Batch operations
def process_agents_batch(agents, batch_size=100):
    for i in range(0, len(agents), batch_size):
        batch = agents[i:i+batch_size]
        # Process batch
```

### 4. **Parallel Processing**

```python
# Parallel agent processing
from multiprocessing import Pool

def process_agent(agent):
    # Agent processing logic
    return result

with Pool() as pool:
    results = pool.map(process_agent, agents)
```

## Interpreting Results

### cProfile Output
- **ncalls**: Number of function calls
- **tottime**: Total time in function (excluding subfunctions)
- **cumtime**: Cumulative time (including subfunctions)
- **percall**: Time per call

### Line Profiler Output
- **Hits**: Number of times line was executed
- **Time**: Total time spent on line
- **Per Hit**: Average time per execution

### Memory Profiler Output
- **Line**: Line number
- **Mem Usage**: Memory usage at line
- **Increment**: Memory increase from previous line

## Example Workflow

1. **Baseline Measurement**
   ```bash
   python scripts/benchmark_chance_c.py --config standard
   ```

2. **Identify Bottlenecks**
   ```bash
   python scripts/profile_chance_c.py --profile-type all
   ```

3. **Detailed Analysis**
   ```bash
   python scripts/line_profile_chance_c.py --function HousingMarket
   ```

4. **Test Optimizations**
   ```bash
   python scripts/benchmark_chance_c.py --config all
   ```

5. **Compare Results**
   - Check `benchmark_results.json` for performance improvements
   - Review `profiling_summary.txt` for recommendations

## Advanced Profiling

### Using snakeviz for Visualization
```bash
pip install snakeviz
snakeviz profiling_results/cprofile_stats.prof
```

### Using py-spy for Real-time Profiling
```bash
pip install py-spy
py-spy top -- python scripts/abm_baltimore_example.py
```

### Using memory_profiler for Memory Analysis
```bash
python -m memory_profiler scripts/abm_baltimore_example.py
```

## Performance Targets

Based on typical CHANCE-C simulations:

- **Sensitivity Mode (2 years)**: < 30 seconds
- **Full Mode (2 years)**: < 60 seconds  
- **Memory Usage**: < 2 GB
- **Scalability**: Linear with number of agents

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from project root
2. **Memory Issues**: Use smaller datasets or increase system memory
3. **Slow Profiling**: Use `--sensitivity-run` for faster analysis
4. **Missing Dependencies**: Install required packages with pip

### Getting Help

- Check the profiling output files for detailed error messages
- Review the `profiling_summary.txt` for optimization recommendations
- Compare results across different configurations to identify patterns

## Next Steps

After profiling:

1. **Implement Optimizations**: Focus on the highest-impact bottlenecks
2. **Test Thoroughly**: Ensure optimizations don't affect model accuracy
3. **Document Changes**: Update code comments and documentation
4. **Monitor Performance**: Re-run profiling after changes
5. **Consider Parallelization**: For large-scale simulations

Remember: Profile first, optimize second, and always validate that optimizations don't change model behavior! 