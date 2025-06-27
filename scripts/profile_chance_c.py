#!/usr/bin/env python3
"""
CHANCE-C Performance Profiling Script

This script provides multiple profiling approaches to identify performance bottlenecks
in CHANCE-C simulations. It includes:

1. Line-by-line profiling with line_profiler
2. Function-level profiling with cProfile
3. Memory profiling with memory_profiler
4. Custom timing for specific components
5. Performance comparison between different configurations

Usage:
    python scripts/profile_chance_c.py [--profile-type] [--iterations] [--output-dir]
"""

import time
import cProfile
import pstats
import io
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add the parent directory to the path to import chance_c
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from chance_c import Model
    from chance_c.model_classes.simulator import ICOMSimulator
    from chance_c.model_engines.housing_market import HousingMarket
    from chance_c.model_engines.new_agent_location import NewAgentLocation
    from chance_c.model_engines.existing_agent_relocation import ExistingAgentLocation
    from chance_c.model_engines.existing_agent_relocation import ExistingAgentReloSampler
    from chance_c.model_engines.agent_creation import NewAgentCreation
    from chance_c.model_engines.building_development import BuildingDevelopment
    from chance_c.model_engines.housing_pricing import HousingPricing
    from chance_c.model_engines.landscape_statistics import LandscapeStatistics
    from chance_c.model_engines.real_estate_prices import RealEstatePrices
    from chance_c.model_engines.flood_hazard import FloodHazard
    from chance_c.model_engines.zoning import Zoning
    from chance_c.model_classes.institutional_agents import CountyZoningManager, RealEstate
    from chance_c.model_classes.institutional_categories import AllHouseholdAgents
except ImportError as e:
    print(f"Error importing chance_c: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CHANCEProfiler:
    """Comprehensive profiler for CHANCE-C simulations."""
    
    def __init__(self, output_dir: str = "profiling_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {}
        
    def profile_with_cprofile(self, model: Model, iterations: int = 1) -> Dict[str, Any]:
        """Profile using cProfile for function-level performance analysis."""
        logger.info(f"Running cProfile analysis with {iterations} iterations")
        
        profiler = cProfile.Profile()
        profiler.enable()
        
        start_time = time.time()
        for i in range(iterations):
            logger.info(f"Running iteration {i+1}/{iterations}")
            model.run_simulation()
        end_time = time.time()
        
        profiler.disable()
        
        # Save detailed stats
        stats_file = self.output_dir / "cprofile_stats.prof"
        profiler.dump_stats(str(stats_file))
        
        # Generate readable report
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(50)  # Top 50 functions
        
        report_file = self.output_dir / "cprofile_report.txt"
        with open(report_file, 'w') as f:
            f.write(s.getvalue())
        
        total_time = end_time - start_time
        avg_time = total_time / iterations
        
        result = {
            'total_time': total_time,
            'avg_time': avg_time,
            'iterations': iterations,
            'stats_file': str(stats_file),
            'report_file': str(report_file)
        }
        
        self.results['cprofile'] = result
        logger.info(f"cProfile analysis complete. Average time: {avg_time:.2f}s")
        return result
    
    def profile_components(self, model: Model) -> Dict[str, Any]:
        """Profile individual components of the simulation."""
        logger.info("Profiling individual simulation components")
        
        component_times = {}
        
        # First, we need to create the simulator and run the initial setup
        # We'll do this by running the simulation up to the point where engines are added
        logger.info("Setting up simulator for component profiling")
        
        # Create simulator (this is what run_simulation does initially)
        model.simulator = ICOMSimulator(
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
        
        # Profile landscape setup
        start_time = time.time()
        model.simulator.set_timestep_information()
        model.simulator.set_landscape(
            landscape_name=model.config.landscape_name,
            geo_filename=model.config.geo_filename,
            pop_filename=model.config.pop_filename,
            pop_fieldname=model.config.get_population_field_name(),
            flood_filename=model.config.flood_filename,
            housing_filename=model.config.housing_filename,
            hedonic_filename=model.config.hedonic_filename,
            field_mappings={
                'geo_file_mapping': model.config.geo_file_mapping,
                'pop_file_mapping': model.config.pop_file_mapping,
                'flood_file_mapping': model.config.flood_file_mapping,
                'housing_file_mapping': model.config.housing_file_mapping,
                'hedonic_file_mapping': model.config.hedonic_file_mapping
            }
        )
        component_times['landscape_setup'] = time.time() - start_time
        
        # Add institutions (this is part of the setup)
        if model.config.sensitivity_run is False:
            # Add zoning manager
            model.simulator.network.add_institution(CountyZoningManager(name=f'zoning_manager_{model.config.county_agent_id}'))
            for block_group in model.simulator.network.nodes:
                if block_group.county == model.config.county_agent_id:
                    model.simulator.network.get_institution(f'zoning_manager_{model.config.county_agent_id}').add_node(block_group)
            
            # Add real estate institution
            model.simulator.network.add_institution(RealEstate(name='real_estate'))
        
        # Add household agents institution
        model.simulator.network.add_institution(AllHouseholdAgents(name='all_household_agents'))
        
        # Profile agent creation
        start_time = time.time()
        model.simulator.convert_initial_population_to_agents(
            no_households_per_agent=model.config.agent_housing_aggregation,
            simple_avoidance_perc=model.config.simple_avoidance_perc
        )
        component_times['agent_creation'] = time.time() - start_time
        
        # Profile housing unit initialization
        start_time = time.time()
        model.simulator.initialize_available_building_units(
            initial_vacancy=model.config.initial_vacancy
        )
        component_times['housing_init'] = time.time() - start_time
        
        # Add engines (this is what run_simulation does)
        if model.config.sensitivity_run is False:
            # Add real estate pricing engine
            target = model.simulator.network.get_institution('real_estate')
            estimation_mode = "OLS_hedonic"
            model.simulator.add_engine(RealEstatePrices(target, estimation_mode=estimation_mode))
        
        # Add other engines
        target = model.simulator.network
        model.simulator.add_engine(NewAgentCreation(
            target, 
            growth_mode=model.config.pop_growth_mode, 
            growth_rate=model.config.pop_growth_perc, 
            inc_growth_mode=model.config.inc_growth_mode,
            pop_growth_inc_perc=model.config.pop_growth_inc_perc, 
            inc_growth_perc=model.config.inc_growth_perc, 
            no_households_per_agent=model.config.agent_housing_aggregation, 
            household_size=model.config.household_size,
            simple_avoidance_perc=model.config.simple_avoidance_perc
        ))
        
        model.simulator.add_engine(ExistingAgentReloSampler(target, perc_move=model.config.perc_move))
        
        model.simulator.add_engine(
            NewAgentLocation(
                target, 
                model.config.block_group_sample_size, 
                house_choice_mode=model.config.house_choice_mode, 
                simple_anova_coefficients=model.config.simple_anova_coefficients, 
                budget_reduction_perc=model.config.budget_reduction_perc
            )
        )
        
        model.simulator.add_engine(
            ExistingAgentLocation(
                target, 
                block_group_sample_size=model.config.block_group_sample_size, 
                house_choice_mode=model.config.house_choice_mode, 
                simple_anova_coefficients=model.config.simple_anova_coefficients
            )
        )
        
        model.simulator.add_engine(
            HousingMarket(
                target, 
                market_mode=model.config.market_mode, 
                block_group_sample_size=model.config.block_group_sample_size
            )
        )
        
        model.simulator.add_engine(
            BuildingDevelopment(
                target, 
                stock_increase_mode=model.config.stock_increase_mode, 
                stock_increase_perc=model.config.stock_increase_perc
            )
        )
        
        model.simulator.add_engine(
            HousingPricing(
                target, 
                housing_pricing_mode=model.config.housing_pricing_mode, 
                price_increase_perc=model.config.price_increase_perc
            )
        )
        
        if model.config.sensitivity_run is False:
            model.simulator.add_engine(FloodHazard(target))
            target = model.simulator.network.get_institution(f'zoning_manager_{model.config.county_agent_id}')
            model.simulator.add_engine(
                Zoning(
                    target, 
                    zoning_mode=model.config.zoning_mode, 
                    zoning_perc=model.config.zoning_perc
                )
            )
        
        model.simulator.add_engine(LandscapeStatistics(target))
        
        # Profile engine execution (one timestep)
        model.simulator.current_timestep_idx = 0
        model.simulator.current_timestep = model.simulator.timesteps[0]
        model.simulator.network.current_timestep = model.simulator.current_timestep
        
        engine_times = {}
        for engine in model.simulator.engines:
            start_time = time.time()
            engine.run()
            engine_times[engine.__class__.__name__] = time.time() - start_time
        
        component_times['engines'] = engine_times
        
        self.results['component_times'] = component_times
        
        # Save component times to file
        report_file = self.output_dir / "component_times.txt"
        with open(report_file, 'w') as f:
            f.write("CHANCE-C Component Profiling Results\n")
            f.write("=" * 50 + "\n\n")
            
            for component, time_taken in component_times.items():
                if component == 'engines':
                    f.write(f"\n{component.upper()}:\n")
                    f.write("-" * 20 + "\n")
                    for engine, engine_time in time_taken.items():
                        f.write(f"  {engine}: {engine_time:.4f}s\n")
                else:
                    f.write(f"{component}: {time_taken:.4f}s\n")
        
        logger.info(f"Component profiling complete. Results saved to {report_file}")
        return component_times
    
    def profile_memory_usage(self, model: Model) -> Dict[str, Any]:
        """Profile memory usage during simulation."""
        try:
            from memory_profiler import profile
            import psutil
        except ImportError:
            logger.warning("memory_profiler not available. Install with: pip install memory_profiler psutil")
            return {}
        
        logger.info("Profiling memory usage")
        
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        model.run_simulation()
        end_time = time.time()
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_peak = process.memory_info().peak_wset / 1024 / 1024  # MB
        
        result = {
            'memory_before_mb': memory_before,
            'memory_after_mb': memory_after,
            'memory_peak_mb': memory_peak,
            'memory_increase_mb': memory_after - memory_before,
            'simulation_time': end_time - start_time
        }
        
        self.results['memory'] = result
        
        # Save memory report
        report_file = self.output_dir / "memory_profile.txt"
        with open(report_file, 'w') as f:
            f.write("CHANCE-C Memory Profiling Results\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Memory before simulation: {memory_before:.2f} MB\n")
            f.write(f"Memory after simulation:  {memory_after:.2f} MB\n")
            f.write(f"Memory increase:          {memory_after - memory_before:.2f} MB\n")
            f.write(f"Peak memory usage:        {memory_peak:.2f} MB\n")
            f.write(f"Simulation time:          {end_time - start_time:.2f} seconds\n")
        
        logger.info(f"Memory profiling complete. Results saved to {report_file}")
        return result
    
    def compare_configurations(self, configs: list) -> Dict[str, Any]:
        """Compare performance across different configurations."""
        logger.info(f"Comparing {len(configs)} different configurations")
        
        comparison_results = {}
        
        for i, config in enumerate(configs):
            logger.info(f"Testing configuration {i+1}/{len(configs)}")
            
            start_time = time.time()
            model = Model(**config)
            model.run_simulation()
            end_time = time.time()
            
            config_name = f"config_{i+1}"
            comparison_results[config_name] = {
                'config': config,
                'time': end_time - start_time
            }
        
        # Save comparison report
        report_file = self.output_dir / "configuration_comparison.txt"
        with open(report_file, 'w') as f:
            f.write("CHANCE-C Configuration Performance Comparison\n")
            f.write("=" * 55 + "\n\n")
            
            for config_name, result in comparison_results.items():
                f.write(f"{config_name}:\n")
                f.write(f"  Time: {result['time']:.2f} seconds\n")
                f.write(f"  Config: {result['config']}\n\n")
        
        self.results['configuration_comparison'] = comparison_results
        logger.info(f"Configuration comparison complete. Results saved to {report_file}")
        return comparison_results
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        report_file = self.output_dir / "profiling_summary.txt"
        
        with open(report_file, 'w') as f:
            f.write("CHANCE-C Performance Profiling Summary\n")
            f.write("=" * 45 + "\n\n")
            
            if 'cprofile' in self.results:
                f.write("cProfile Results:\n")
                f.write(f"  Average simulation time: {self.results['cprofile']['avg_time']:.2f} seconds\n")
                f.write(f"  Total iterations: {self.results['cprofile']['iterations']}\n")
                f.write(f"  Detailed report: {self.results['cprofile']['report_file']}\n\n")
            
            if 'component_times' in self.results:
                f.write("Component Timing:\n")
                for component, time_taken in self.results['component_times'].items():
                    if component == 'engines':
                        f.write(f"  {component}:\n")
                        for engine, engine_time in time_taken.items():
                            f.write(f"    {engine}: {engine_time:.4f}s\n")
                    else:
                        f.write(f"  {component}: {time_taken:.4f}s\n")
                f.write("\n")
            
            if 'memory' in self.results:
                f.write("Memory Usage:\n")
                f.write(f"  Memory increase: {self.results['memory']['memory_increase_mb']:.2f} MB\n")
                f.write(f"  Peak memory: {self.results['memory']['memory_peak_mb']:.2f} MB\n\n")
            
            if 'configuration_comparison' in self.results:
                f.write("Configuration Comparison:\n")
                for config_name, result in self.results['configuration_comparison'].items():
                    f.write(f"  {config_name}: {result['time']:.2f}s\n")
        
        logger.info(f"Summary report generated: {report_file}")


def main():
    """Main profiling function."""
    parser = argparse.ArgumentParser(description="Profile CHANCE-C performance")
    parser.add_argument("--profile-type", choices=["cprofile", "components", "memory", "all"], 
                       default="all", help="Type of profiling to perform")
    parser.add_argument("--iterations", type=int, default=1, 
                       help="Number of iterations for cProfile analysis")
    parser.add_argument("--output-dir", default="profiling_results", 
                       help="Output directory for profiling results")
    parser.add_argument("--sensitivity-run", action="store_true", 
                       help="Run in sensitivity mode (faster)")
    
    args = parser.parse_args()
    
    # Create profiler
    profiler = CHANCEProfiler(args.output_dir)
    
    # Create model with profiling-friendly settings
    model_config = {
        'sensitivity_run': args.sensitivity_run,
        'n_years': 2,  # Short simulation for profiling
        'record_time': False,
        'progress': False
    }
    
    logger.info("Creating CHANCE-C model for profiling")
    model = Model(**model_config)
    
    # Run selected profiling
    if args.profile_type in ["cprofile", "all"]:
        profiler.profile_with_cprofile(model, args.iterations)
    
    if args.profile_type in ["components", "all"]:
        # Recreate model for component profiling
        model = Model(**model_config)
        profiler.profile_components(model)
    
    if args.profile_type in ["memory", "all"]:
        # Recreate model for memory profiling
        model = Model(**model_config)
        profiler.profile_memory_usage(model)
    
    # Generate summary report
    profiler.generate_summary_report()
    
    logger.info(f"Profiling complete! Results saved to {args.output_dir}/")
    logger.info("Check the summary report for key findings and optimization opportunities.")


if __name__ == "__main__":
    main() 