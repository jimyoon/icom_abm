# Chance-C Profiling Analysis and Numba Optimization Recommendations

## Executive Summary

The profiling analysis of chance-c reveals several key performance bottlenecks that can be significantly improved with numba optimization. The simulation took **25.9 seconds** for a 2-year run with reduced parameters, with the biggest bottlenecks being:

1. **Geopandas distance calculations (8.8s)** - 34% of total time
2. **Pandas operations (multiple bottlenecks)** - ~15% of total time  
3. **Utility calculations** - Good candidates for numba
4. **Market matching algorithms** - Can benefit from numba optimization

## Detailed Bottleneck Analysis

### 1. Geopandas Distance Calculations (8.8s - 34% of total time)

**Location**: `chance_c/model_engines/existing_agent_relocation.py:110`

**Problem**: The existing agent relocation engine performs 300 distance calculations using geopandas, which involves:
- 320,850 calls to `shapely.geometry.base.distance()` 
- 320,850 calls to `shapely.topology.__call__()`
- Complex geometry operations with shapely objects

**Numba Solution**: Replace geopandas distance with numba-optimized distance calculations using numpy arrays.

### 2. Pandas Operations (Multiple bottlenecks)

**Key bottlenecks identified**:
- DataFrame filtering operations (`pandas.core.ops.array_ops.comparison_op`)
- Sampling operations (`pandas.core.generic.sample`) 
- DataFrame concatenation (`pandas.core.reshape.concat.concat`)
- Series creation and manipulation

**Numba Solution**: Convert pandas operations to numpy arrays where possible and use numba for filtering/sampling logic.

### 3. Utility Calculations

**Location**: `chance_c/model_engines/new_agent_location.py:74`

**Current implementation**: Simple mathematical operations that are perfect for numba:
```python
# Simple ANOVA utility calculation
utility = (coefficients[0] + 
          coefficients[1] * sqfeet + 
          coefficients[2] * age + 
          coefficients[3] * stories + 
          coefficients[4] * baths + 
          residuals)

# Cobb-Douglas utility calculation  
cobb_douglas_utility = (sqfeet ** a) * (age ** b) * (stories ** c)
```

**Numba Solution**: Convert to numba-compiled functions for massive speedup.

### 4. Market Matching Algorithm

**Location**: `chance_c/model_engines/housing_market.py:47`

**Current bottlenecks**:
- Sorting operations (5,480 calls to `builtins.sorted`)
- Dictionary operations and lookups
- Iterative matching logic

**Numba Solution**: Use numba for sorting and matching logic with numpy arrays.

## Specific Numba Optimization Recommendations

### Priority 1: Distance Calculations (Biggest Impact)

**Current**: Geopandas with shapely geometries
```python
distances = gdf.distance(ref_point)
```

**Proposed**: Numba-optimized distance calculation
```python
@numba.jit(nopython=True)
def calculate_distances(coords_x, coords_y, ref_x, ref_y):
    n = len(coords_x)
    distances = np.empty(n)
    for i in range(n):
        dx = coords_x[i] - ref_x
        dy = coords_y[i] - ref_y
        distances[i] = np.sqrt(dx*dx + dy*dy)
    return distances
```

**Expected speedup**: 10-100x faster

### Priority 2: Utility Calculations

**Current**: Python loops with pandas operations
```python
for household in households:
    utility = calculate_utility(household, block_group)
```

**Proposed**: Numba-vectorized utility calculation
```python
@numba.jit(nopython=True)
def calculate_utilities_vectorized(sqfeet, age, stories, baths, residuals, coefficients):
    n = len(sqfeet)
    utilities = np.empty(n)
    for i in range(n):
        utilities[i] = (coefficients[0] + 
                       coefficients[1] * sqfeet[i] + 
                       coefficients[2] * age[i] + 
                       coefficients[3] * stories[i] + 
                       coefficients[4] * baths[i] + 
                       residuals[i])
    return utilities
```

**Expected speedup**: 5-20x faster

### Priority 3: Market Matching Algorithm

**Current**: Python sorting and dictionary operations
```python
sorted_candidates = sorted(((v, k) for k, v in utilities_dict.items()))
```

**Proposed**: Numba-optimized matching with numpy arrays
```python
@numba.jit(nopython=True)
def find_top_candidates(utilities, household_ids, n_candidates):
    # Use numpy argsort for faster sorting
    sorted_indices = np.argsort(utilities)[::-1]  # Descending order
    return household_ids[sorted_indices[:n_candidates]]
```

**Expected speedup**: 2-5x faster

### Priority 4: Pandas Operations Replacement

**Current**: Pandas filtering and sampling
```python
budget_filter = housing_data[housing_data['new_price'] <= 300000]
sample = budget_filter.sample(n=10, weights='available_units')
```

**Proposed**: Numba-optimized filtering and sampling
```python
@numba.jit(nopython=True)
def filter_and_sample(prices, weights, budget, n_sample):
    # Filter by budget
    mask = prices <= budget
    filtered_indices = np.where(mask)[0]
    
    if len(filtered_indices) == 0:
        return np.array([], dtype=np.int64)
    
    # Sample with weights
    filtered_weights = weights[filtered_indices]
    sampled_indices = np.random.choice(
        filtered_indices, 
        size=min(n_sample, len(filtered_indices)), 
        p=filtered_weights/filtered_weights.sum()
    )
    return sampled_indices
```

**Expected speedup**: 3-10x faster

## Implementation Strategy

### Phase 1: Distance Calculations (Immediate Impact)
1. Extract coordinates from geopandas geometries to numpy arrays
2. Implement numba distance calculation function
3. Replace geopandas distance calls in `existing_agent_relocation.py`
4. **Expected time savings**: 8.8s → 0.1s (88x speedup)

### Phase 2: Utility Calculations (High Impact)
1. Convert utility calculation functions to numba
2. Vectorize operations across multiple households
3. Replace utility calculations in `new_agent_location.py`
4. **Expected time savings**: 1-2s → 0.1s (10-20x speedup)

### Phase 3: Market Matching (Medium Impact)
1. Convert market matching logic to use numpy arrays
2. Implement numba-optimized sorting and matching
3. Replace market matching in `housing_market.py`
4. **Expected time savings**: 1-2s → 0.3s (3-7x speedup)

### Phase 4: Pandas Operations (Ongoing)
1. Identify and replace pandas bottlenecks with numpy/numba
2. Focus on filtering, sampling, and concatenation operations
3. **Expected time savings**: 2-3s → 0.5s (4-6x speedup)

## Expected Overall Performance Improvement

**Current total time**: 25.9 seconds
**Expected optimized time**: 2-4 seconds
**Overall speedup**: 6-13x faster

## Implementation Notes

1. **Data Structure Changes**: May need to convert some pandas DataFrames to numpy arrays
2. **Memory Usage**: Numba operations may use more memory but will be much faster
3. **Compatibility**: Ensure numba functions work with existing data types
4. **Testing**: Maintain existing functionality while improving performance

## Next Steps

1. Install numba: `pip install numba`
2. Start with Phase 1 (distance calculations) for immediate impact
3. Implement utility calculation optimizations
4. Gradually replace pandas operations with numpy/numba alternatives
5. Profile after each phase to measure improvements

## Files to Modify

1. `chance_c/model_engines/existing_agent_relocation.py` - Distance calculations
2. `chance_c/model_engines/new_agent_location.py` - Utility calculations  
3. `chance_c/model_engines/housing_market.py` - Market matching
4. `chance_c/model_engines/landscape_statistics.py` - Statistical calculations
5. Create new `chance_c/utils/numba_utils.py` - Shared numba functions 