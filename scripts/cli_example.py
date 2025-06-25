#!/usr/bin/env python3
"""
Example script demonstrating how to use the CHANCE-C CLI programmatically.

This script shows how to run simulations, validate configurations, and
generate results using the command line interface.
"""

import subprocess
import sys
from pathlib import Path


def run_cli_command(command_args):
    """Run a CLI command and return the result."""
    try:
        result = subprocess.run(
            ['python', '-m', 'chance_c.cli'] + command_args,
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Command executed successfully!")
        print("Output:")
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print("Error output:")
        print(e.stderr)
        return None


def main():
    """Main function demonstrating CLI usage."""
    print("CHANCE-C CLI Example")
    print("=" * 50)
    
    # Example 1: Show help information
    print("\n1. Getting help information:")
    print("-" * 30)
    run_cli_command(['--help'])
    
    # Example 2: Show model information
    print("\n2. Model information:")
    print("-" * 30)
    run_cli_command(['info'])
    
    # Example 3: Create a configuration file
    print("\n3. Creating a configuration file:")
    print("-" * 30)
    run_cli_command(['create-config', '--template', 'basic', '--output', 'example_config.yaml'])
    
    # Example 4: Validate the configuration
    print("\n4. Validating the configuration:")
    print("-" * 30)
    config_file = Path('example_config.yaml')
    if config_file.exists():
        run_cli_command(['validate-config', str(config_file)])
    else:
        print("❌ Configuration file not found")
    
    # Example 5: Run a quick simulation (sensitivity mode)
    print("\n5. Running a quick simulation:")
    print("-" * 30)
    run_cli_command([
        'run',
        '--sensitivity-run',
        '--no-years', '1',
        '--output-dir', './example_results',
        '--progress'
    ])
    
    print("\n🎉 CLI example completed!")
    print("Check the 'example_results' directory for simulation outputs.")


if __name__ == '__main__':
    main() 