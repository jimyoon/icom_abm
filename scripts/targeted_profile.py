#!/usr/bin/env python3
"""
Targeted profiling script for specific computational bottlenecks in chance-c.
"""

import time
import cProfile
import pstats
import io
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add the chance_c module to the path
sys.path.insert(0, str(Path(__file__).parent))

def profile_utility_calculations():
    """Profile utility calculation functions which are likely bottlenecks."""
    print("Profiling utility calculations...")
    
    from chance_c.model import Model
    
    # Create a minimal model
    model = Model(
        n_years=1,
        agent_housing_aggregation=20,
        block_group_sample_size=3,
        record_time=True,
        progress=False
    )
    
    # Set up the simulation to get to the utility calculation stage
    model.simulator = model.simulator.__class__(
        network=model.network, 
        record_time=model.config.record_time, 
        progress=model.config.progress, 
        max_iterations=model.config.max_iterations,
        name=model.config.simulation_name, 
        scenario=model.config.scenario, 
        intervention=model.config.intervention, 
        start_year=model.config.start_year, 
        n_years=model.config.n_years
    )
    
    # Profile the utility calculation specifically
    pr = cProfile.Profile()
    pr.enable()
    
    try:
        # This will trigger utility calculations
        model.run_simulation()
    except Exception as e:
        print(f"Simulation failed during profiling: {e}")
    
    pr.disable()
    
    # Analyze results
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    
    print("Utility calculation profiling results:")
    print(s.getvalue())
    
    return pr

def profile_pandas_operations():
    """Profile pandas operations which are often bottlenecks."""
    print("\nProfiling pandas operations...")
    
    # Create sample data similar to what chance-c uses
    n_block_groups = 1000
    n_households = 5000
    
    # Sample housing data
    housing_data = pd.DataFrame({
        'GEOID': [f'BG{i:06d}' for i in range(n_block_groups)],
        'new_price': np.random.uniform(100000, 500000, n_block_groups),
        'available_units': np.random.randint(1, 20, n_block_groups),
        'N_MeanSqfeet': np.random.uniform(1000, 3000, n_block_groups),
        'N_MeanAge': np.random.uniform(10, 50, n_block_groups),
        'N_MeanNoOfStories': np.random.uniform(1, 3, n_block_groups),
        'N_MeanFullBathNumber': np.random.uniform(1, 3, n_block_groups),
        'perc_fld_area': np.random.uniform(0, 0.3, n_block_groups),
        'residuals': np.random.normal(0, 10000, n_block_groups)
    })
    
    # Sample household utilities
    utilities_data = pd.DataFrame({
        'GEOID': np.random.choice(housing_data['GEOID'], n_households * 10),
        'household': [f'hh_{i}' for i in range(n_households)] * 10,
        'utility': np.random.uniform(0, 1000000, n_households * 10)
    })
    
    pr = cProfile.Profile()
    pr.enable()
    
    # Simulate operations similar to those in chance-c
    for _ in range(100):
        # Simulate filtering operations
        budget_filter = housing_data[housing_data['new_price'] <= 300000]
        
        # Simulate sampling operations
        if len(budget_filter) > 0:
            sample = budget_filter.sample(n=min(10, len(budget_filter)), replace=True, weights='available_units')
        
        # Simulate utility calculations
        if len(utilities_data) > 0:
            household_utilities = utilities_data[utilities_data['household'] == 'hh_0']
            utilities_dict = dict(zip(household_utilities['GEOID'], household_utilities['utility']))
            sorted_candidates = sorted(((v, k) for k, v in utilities_dict.items()))
    
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(10)
    
    print("Pandas operations profiling results:")
    print(s.getvalue())
    
    return pr

def profile_agent_creation():
    """Profile agent creation and management operations."""
    print("\nProfiling agent creation operations...")
    
    from chance_c.model_classes.urban_agents import HouseholdAgent
    
    pr = cProfile.Profile()
    pr.enable()
    
    # Create many agents
    agents = []
    for i in range(10000):
        agent = HouseholdAgent(
            name=f'agent_{i}',
            location=f'BG{i:06d}',
            no_households_per_agent=10,
            household_size=2.7,
            year_of_residence=2018
        )
        agents.append(agent)
    
    # Simulate agent operations
    for agent in agents[:1000]:
        agent.house_budget = np.random.uniform(100000, 500000)
        agent.income = np.random.uniform(50000, 150000)
        agent.avoidance = np.random.choice([True, False])
    
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(10)
    
    print("Agent creation profiling results:")
    print(s.getvalue())
    
    return pr

def profile_market_matching():
    """Profile the housing market matching algorithm."""
    print("\nProfiling market matching algorithm...")
    
    # Create sample market data
    n_households = 1000
    n_block_groups = 500
    
    households = {
        f'hh_{i}': {
            'income': np.random.uniform(50000, 150000),
            'utility_dict': {f'BG{j:06d}': np.random.uniform(0, 1000000) for j in range(n_block_groups)}
        }
        for i in range(n_households)
    }
    
    block_groups = {
        f'BG{i:06d}': {
            'available_units': np.random.randint(0, 10),
            'demand': {}
        }
        for i in range(n_block_groups)
    }
    
    pr = cProfile.Profile()
    pr.enable()
    
    # Simulate market matching iterations
    for market_iter in range(5):
        block_group_demand = {}
        
        # Simulate household demand calculation
        for household_name, household_data in households.items():
            utilities_dict = household_data['utility_dict']
            sorted_candidates = sorted(((v, k) for k, v in utilities_dict.items()))
            
            try:
                top_candidate = sorted_candidates[-1-market_iter][1]
                if top_candidate in block_group_demand:
                    block_group_demand[top_candidate][household_name] = household_data['income']
                else:
                    block_group_demand[top_candidate] = {household_name: household_data['income']}
            except IndexError:
                continue
        
        # Simulate matching process
        for block_group_name, demand in block_group_demand.items():
            no_households = len(demand)
            available_units = block_groups[block_group_name]['available_units']
            
            if available_units >= no_households:
                # All households can be accommodated
                pass
            else:
                # Only top income households
                top_matches = dict(sorted(demand.items(), key=lambda x: x[1], reverse=True)[:available_units])
    
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(10)
    
    print("Market matching profiling results:")
    print(s.getvalue())
    
    return pr

def benchmark_numpy_operations():
    """Benchmark numpy operations that could benefit from numba."""
    print("\nBenchmarking numpy operations...")
    
    # Create sample data
    n_elements = 1000000
    data = np.random.uniform(0, 1000000, n_elements)
    coefficients = np.array([-121428, 294707, 130553, 128990, 154887, -500000])
    
    # Benchmark utility calculation
    start_time = time.time()
    
    for _ in range(100):
        # Simulate utility calculation similar to chance-c
        utility = (coefficients[0] + 
                  coefficients[1] * data + 
                  coefficients[2] * data * 0.5 + 
                  coefficients[3] * data * 0.3 + 
                  coefficients[4] * data * 0.2 + 
                  coefficients[5] * data * 0.1)
    
    numpy_time = time.time() - start_time
    print(f"Numpy utility calculation time: {numpy_time:.4f}s")
    
    return numpy_time

if __name__ == "__main__":
    print("Targeted Profiling for Chance-C Optimization")
    print("="*60)
    
    # Run targeted profiling
    profile_utility_calculations()
    profile_pandas_operations()
    profile_agent_creation()
    profile_market_matching()
    benchmark_numpy_operations()
    
    print("\nTargeted profiling complete!")
    print("Look for functions with high call counts or long execution times.") 