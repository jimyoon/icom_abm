#!/usr/bin/env python3
"""
CHANCE-C Performance Benchmarking Script

This script provides simple benchmarking of CHANCE-C performance with different
configurations and parameters. It's useful for comparing performance across
different settings and identifying optimization opportunities.

Usage:
    python scripts/benchmark_chance_c.py [--config] [--iterations] [--output-file]
"""

import time
import sys
import os
from pathlib import Path
import argparse
import json
from typing import Dict, Any, List
import statistics

# Add the parent directory to the path to import chance_c
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from chance_c import Model
except ImportError as e:
    print(f"Error importing chance_c: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


class CHANCEBenchmark:
    """Benchmarking class for CHANCE-C simulations."""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_configuration(self, config: Dict[str, Any], iterations: int = 3) -> Dict[str, Any]:
        """Benchmark a specific configuration."""
        print(f"Benchmarking configuration: {config.get('name', 'unnamed')}")
        print(f"Running {iterations} iterations...")
        
        times = []
        memory_usage = []
        
        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}")
            
            # Create model
            model = Model(**config)
            
            # Measure time
            start_time = time.time()
            model.run_simulation()
            end_time = time.time()
            
            times.append(end_time - start_time)
            
            # Measure memory (if psutil is available)
            try:
                import psutil
                process = psutil.Process()
                memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
            except ImportError:
                pass
        
        # Calculate statistics
        result = {
            'config': config,
            'iterations': iterations,
            'times': times,
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_time': statistics.stdev(times) if len(times) > 1 else 0,
        }
        
        if memory_usage:
            result.update({
                'memory_usage': memory_usage,
                'avg_memory': statistics.mean(memory_usage),
                'max_memory': max(memory_usage),
            })
        
        return result
    
    def run_standard_benchmarks(self) -> Dict[str, Any]:
        """Run a set of standard benchmarks."""
        print("Running standard CHANCE-C benchmarks...")
        
        # Define benchmark configurations
        benchmarks = [
            {
                'name': 'sensitivity_2yr',
                'sensitivity_run': True,
                'n_years': 2,
                'record_time': False,
                'progress': False
            },
            {
                'name': 'sensitivity_5yr',
                'sensitivity_run': True,
                'n_years': 5,
                'record_time': False,
                'progress': False
            },
            {
                'name': 'full_2yr',
                'sensitivity_run': False,
                'n_years': 2,
                'record_time': False,
                'progress': False
            },
            {
                'name': 'full_5yr',
                'sensitivity_run': False,
                'n_years': 5,
                'record_time': False,
                'progress': False
            }
        ]
        
        results = {}
        for config in benchmarks:
            result = self.benchmark_configuration(config, iterations=3)
            results[config['name']] = result
        
        self.results = results
        return results
    
    def compare_agent_aggregation(self, aggregations: List[int] = [1, 5, 10, 20]) -> Dict[str, Any]:
        """Compare performance with different agent aggregation levels."""
        print("Comparing agent aggregation levels...")
        
        results = {}
        for agg in aggregations:
            config = {
                'name': f'agg_{agg}',
                'sensitivity_run': True,
                'n_years': 2,
                'agent_housing_aggregation': agg,
                'record_time': False,
                'progress': False
            }
            
            result = self.benchmark_configuration(config, iterations=3)
            results[f'agg_{agg}'] = result
        
        return results
    
    def compare_sample_sizes(self, sample_sizes: List[int] = [5, 10, 20, 50]) -> Dict[str, Any]:
        """Compare performance with different block group sample sizes."""
        print("Comparing block group sample sizes...")
        
        results = {}
        for size in sample_sizes:
            config = {
                'name': f'sample_{size}',
                'sensitivity_run': True,
                'n_years': 2,
                'block_group_sample_size': size,
                'record_time': False,
                'progress': False
            }
            
            result = self.benchmark_configuration(config, iterations=3)
            results[f'sample_{size}'] = result
        
        return results
    
    def save_results(self, filename: str = "benchmark_results.json"):
        """Save benchmark results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"Results saved to {filename}")
    
    def print_summary(self):
        """Print a summary of benchmark results."""
        print("\n" + "="*60)
        print("CHANCE-C BENCHMARK SUMMARY")
        print("="*60)
        
        for name, result in self.results.items():
            print(f"\n{name.upper()}:")
            print(f"  Average time: {result['avg_time']:.2f}s ± {result['std_time']:.2f}s")
            print(f"  Range: {result['min_time']:.2f}s - {result['max_time']:.2f}s")
            if 'avg_memory' in result:
                print(f"  Average memory: {result['avg_memory']:.1f} MB")
                print(f"  Peak memory: {result['max_memory']:.1f} MB")
        
        # Find fastest and slowest
        if self.results:
            fastest = min(self.results.items(), key=lambda x: x[1]['avg_time'])
            slowest = max(self.results.items(), key=lambda x: x[1]['avg_time'])
            
            print(f"\nPERFORMANCE COMPARISON:")
            print(f"  Fastest: {fastest[0]} ({fastest[1]['avg_time']:.2f}s)")
            print(f"  Slowest: {slowest[0]} ({slowest[1]['avg_time']:.2f}s)")
            print(f"  Speedup: {slowest[1]['avg_time'] / fastest[1]['avg_time']:.1f}x")


def main():
    """Main benchmarking function."""
    parser = argparse.ArgumentParser(description="Benchmark CHANCE-C performance")
    parser.add_argument("--config", choices=["standard", "aggregation", "sample_size", "all"], 
                       default="standard", help="Type of benchmark to run")
    parser.add_argument("--iterations", type=int, default=3, 
                       help="Number of iterations per configuration")
    parser.add_argument("--output-file", default="benchmark_results.json", 
                       help="Output file for results")
    
    args = parser.parse_args()
    
    # Create benchmarker
    benchmarker = CHANCEBenchmark()
    
    # Run selected benchmarks
    if args.config in ["standard", "all"]:
        benchmarker.run_standard_benchmarks()
    
    if args.config in ["aggregation", "all"]:
        agg_results = benchmarker.compare_agent_aggregation()
        benchmarker.results.update(agg_results)
    
    if args.config in ["sample_size", "all"]:
        sample_results = benchmarker.compare_sample_sizes()
        benchmarker.results.update(sample_results)
    
    # Save and print results
    benchmarker.save_results(args.output_file)
    benchmarker.print_summary()
    
    print(f"\nDetailed results saved to: {args.output_file}")
    print("\nOptimization recommendations:")
    print("- Use sensitivity_run=True for faster testing")
    print("- Increase agent_housing_aggregation for larger simulations")
    print("- Adjust block_group_sample_size based on accuracy vs speed trade-offs")
    print("- Consider parallel processing for multiple runs")


if __name__ == "__main__":
    main() 