#!/usr/bin/env python3
"""
Test script to verify LandscapeStatistics engine functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from chance_c import Model
from chance_c.model_engines.landscape_statistics import LandscapeStatistics

def test_landscape_statistics():
    """Test if LandscapeStatistics engine is working correctly."""
    
    print("=== Testing LandscapeStatistics Engine ===\n")
    
    # Create a simple model
    model = Model(
        n_years=2,
        agent_housing_aggregation=5,
        pop_growth_perc=0.10,  # 10% growth to make it obvious
        sensitivity_run=True,
        log_level='DEBUG'
    )
    
    # Run simulation
    print("1. Running simulation...")
    model.run_simulation()
    print("✅ Simulation completed!\n")
    
    # Check if LandscapeStatistics engine was added
    print("2. Checking engine configuration:")
    engines = model.simulator.engines
    landscape_stats_engine = None
    
    for engine in engines:
        if isinstance(engine, LandscapeStatistics):
            landscape_stats_engine = engine
            break
    
    if landscape_stats_engine:
        print("   ✅ LandscapeStatistics engine found in simulation")
    else:
        print("   ❌ LandscapeStatistics engine NOT found in simulation")
        return
    
    # Check population before and after running the engine manually
    print("\n3. Testing manual engine execution:")
    
    # Get initial population
    initial_pop = model.simulator.network.total_population
    print(f"   Initial total population: {initial_pop:,.0f}")
    
    # Run the engine manually
    landscape_stats_engine.run()
    
    # Check population after running
    final_pop = model.simulator.network.total_population
    print(f"   Final total population: {final_pop:,.0f}")
    
    if final_pop != initial_pop:
        print(f"   ✅ Population updated: {final_pop - initial_pop:+,.0f} change")
    else:
        print("   ❌ Population not updated")
    
    # Check block group populations
    print("\n4. Checking block group populations:")
    
    # Count agents in each block group
    agent_counts = {}
    for block_group in model.simulator.network.nodes:
        agent_counts[block_group.name] = len(block_group.household_agents)
    
    # Calculate expected population
    expected_pop = sum(agent_counts.values()) * model.config.agent_housing_aggregation * model.config.household_size
    print(f"   Expected population from agents: {expected_pop:,.0f}")
    print(f"   Actual total population: {final_pop:,.0f}")
    
    if abs(expected_pop - final_pop) < 1000:  # Allow some tolerance
        print("   ✅ Population calculation is correct")
    else:
        print(f"   ❌ Population mismatch: {abs(expected_pop - final_pop):,.0f}")
    
    # Check if the engine is being called during simulation
    print("\n5. Checking engine execution during simulation:")
    
    # Look for LandscapeStatistics in the logs or check if it's being called
    # This is tricky since we can't easily intercept the pynsim execution
    print("   Note: LandscapeStatistics engine should run after agent location engines")
    print("   to update population counts in the housing dataframe")
    
    # Check the housing dataframe
    print("\n6. Checking housing dataframe:")
    df = model.housing_dataframe
    
    # Check population by year
    pop_by_year = df.groupby('model_year')['population'].sum()
    print("   Population by year in housing dataframe:")
    for year, pop in pop_by_year.items():
        print(f"     Year {year}: {pop:,.0f}")
    
    # Check if population is being updated in the dataframe
    if len(pop_by_year) > 1:
        first_pop = pop_by_year.iloc[0]
        last_pop = pop_by_year.iloc[-1]
        change = last_pop - first_pop
        change_pct = (change / first_pop) * 100 if first_pop > 0 else 0
        
        print(f"   Population change in dataframe: {change:+,.0f} ({change_pct:+.2f}%)")
        
        if change > 0:
            print("   ✅ Population is changing in the dataframe")
        else:
            print("   ❌ Population is not changing in the dataframe")
    else:
        print("   ⚠️  Only one year of data available")
    
    return model

if __name__ == "__main__":
    model = test_landscape_statistics()
    print(f"\n✅ Test complete.") 