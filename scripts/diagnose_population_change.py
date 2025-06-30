#!/usr/bin/env python3
"""
Diagnostic script to identify why population isn't changing between timesteps.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from chance_c import Model

def diagnose_population_change():
    """Diagnose population change issues in the simulation."""
    
    print("=== CHANCE-C Population Change Diagnostic ===\n")
    
    # Create a model with higher population growth for testing
    model = Model(
        n_years=3,  # 3-year simulation
        agent_housing_aggregation=5,  # Smaller aggregation to see more agents
        household_size=2.7,
        initial_vacancy=0.20,
        pop_growth_mode='perc',
        pop_growth_perc=0.05,  # 5% growth - should be noticeable
        inc_growth_mode='random_agent_replication',
        pop_growth_inc_perc=0.90,
        inc_growth_perc=0.05,
        bld_growth_perc=0.01,
        perc_move=0.10,
        perc_move_mode='random',
        house_budget_mode='rhea',
        house_choice_mode='simple_avoidance_utility',
        simple_anova_coefficients=(-121428, 294707, 130553, 128990, 154887, -500000),
        simple_avoidance_perc=0.95,
        budget_reduction_perc=0.90,
        stock_increase_mode='simple_perc',
        stock_increase_perc=0.05,
        housing_pricing_mode='simple_perc',
        price_increase_perc=0.05,
        landscape_name='Test',
        geo_filename='',
        pop_filename='',
        flood_filename='',
        housing_filename='',
        hedonic_filename='',
        record_time=False,
        progress=False,
        max_iterations=1,
        name='Diagnostic_Model',
        sensitivity_run=True,  # Skip some engines for faster testing
        county_agent_id='005',
        block_group_sample_size=5,
        zoning_mode='simple_perc',
        zoning_perc=0.05,
        market_mode='top_candidate',
        log_level='INFO'  # Show more logging
    )
    
    print("1. Model Configuration:")
    print(f"   Population growth mode: {model.config.pop_growth_mode}")
    print(f"   Population growth rate: {model.config.pop_growth_perc * 100}%")
    print(f"   Agent housing aggregation: {model.config.agent_housing_aggregation}")
    print(f"   Household size: {model.config.household_size}")
    print(f"   Number of years: {model.config.n_years}")
    
    # Run simulation
    print("\n2. Running simulation...")
    model.run_simulation()
    print("✅ Simulation completed!\n")
    
    # Analyze the housing dataframe
    print("3. Analyzing population data:")
    df = model.housing_dataframe
    
    # Check population by year
    pop_by_year = df.groupby('model_year')['population'].sum()
    print("\n   Total population by year:")
    for year, pop in pop_by_year.items():
        print(f"     Year {year}: {pop:,.0f} people")
    
    # Check for population changes
    years = sorted(pop_by_year.index)
    if len(years) > 1:
        for i in range(1, len(years)):
            prev_pop = pop_by_year[years[i-1]]
            curr_pop = pop_by_year[years[i]]
            change = curr_pop - prev_pop
            change_pct = (change / prev_pop) * 100 if prev_pop > 0 else 0
            print(f"     Change from Year {years[i-1]} to {years[i]}: {change:+,.0f} ({change_pct:+.2f}%)")
    
    # Check agent counts
    print("\n4. Analyzing agent data:")
    
    # Get agent counts from the network
    if hasattr(model.simulator, 'network') and hasattr(model.simulator.network, 'get_institution'):
        try:
            all_agents = model.simulator.network.get_institution('all_household_agents')
            if hasattr(all_agents, 'components'):
                total_agents = len(all_agents.components)
                print(f"   Total agents in simulation: {total_agents}")
                
                # Count agents by type
                initial_agents = sum(1 for agent in all_agents.components if 'initial' in agent.name)
                new_agents = sum(1 for agent in all_agents.components if 'initial' not in agent.name)
                print(f"   Initial agents: {initial_agents}")
                print(f"   New agents created: {new_agents}")
                
                # Check unassigned agents
                if hasattr(model.simulator.network, 'unassigned_households'):
                    unassigned = len(model.simulator.network.unassigned_households)
                    print(f"   Unassigned agents: {unassigned}")
                else:
                    print("   Unassigned agents: Not tracked")
        except Exception as e:
            print(f"   Error accessing agent data: {e}")
    
    # Check block group data
    print("\n5. Analyzing block group data:")
    
    # Check if population is being updated in block groups
    for year in sorted(df['model_year'].unique()):
        year_data = df[df['model_year'] == year]
        print(f"\n   Year {year}:")
        print(f"     Number of block groups: {len(year_data)}")
        print(f"     Total population: {year_data['population'].sum():,.0f}")
        print(f"     Average population per block group: {year_data['population'].mean():.1f}")
        print(f"     Population range: {year_data['population'].min():.0f} - {year_data['population'].max():.0f}")
        
        # Check for occupied units
        if 'occupied_units' in year_data.columns:
            print(f"     Total occupied units: {year_data['occupied_units'].sum():,.0f}")
            print(f"     Average occupied units per block group: {year_data['occupied_units'].mean():.1f}")
    
    # Check for potential issues
    print("\n6. Potential issues identified:")
    
    issues = []
    
    # Check if population growth is too small to be visible
    if len(years) > 1:
        total_change = pop_by_year[years[-1]] - pop_by_year[years[0]]
        total_change_pct = (total_change / pop_by_year[years[0]]) * 100 if pop_by_year[years[0]] > 0 else 0
        
        if abs(total_change_pct) < 1.0:
            issues.append(f"Population change is very small ({total_change_pct:.2f}%) - may be due to agent aggregation")
        
        if total_change == 0:
            issues.append("No population change detected - check agent creation engine")
    
    # Check agent aggregation
    if model.config.agent_housing_aggregation > 10:
        issues.append(f"High agent aggregation ({model.config.agent_housing_aggregation}) may mask small population changes")
    
    # Check growth rate
    if model.config.pop_growth_perc < 0.01:
        issues.append(f"Low growth rate ({model.config.pop_growth_perc * 100}%) may not be visible with current settings")
    
    if issues:
        for issue in issues:
            print(f"   ⚠️  {issue}")
    else:
        print("   ✅ No obvious issues detected")
    
    # Recommendations
    print("\n7. Recommendations:")
    print("   - Try increasing pop_growth_perc to 0.05 or higher")
    print("   - Reduce agent_housing_aggregation to 1-5 for more granular results")
    print("   - Check if NewAgentCreation engine is running properly")
    print("   - Verify that NewAgentLocation engine is assigning new agents")
    print("   - Ensure LandscapeStatistics engine is updating population counts")
    
    return df

if __name__ == "__main__":
    df = diagnose_population_change()
    print(f"\n✅ Diagnostic complete. Housing dataframe shape: {df.shape}") 