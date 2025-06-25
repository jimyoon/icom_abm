#!/usr/bin/env python3
"""
Command Line Interface for the ICoM ABM (Agent-Based Model)

This module provides a comprehensive CLI for running simulations, viewing results,
and managing configurations for the ICoM housing market dynamics model.
"""

import click
import os
import sys
import logging
from pathlib import Path
from typing import Optional, Tuple

from .model import Model


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="0.1.0", prog_name="ICoM ABM")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output except errors')
def cli(verbose: bool, quiet: bool):
    """
    ICoM ABM - Agent-Based Model for housing market dynamics simulation.
    
    This tool provides a comprehensive framework for simulating housing market
    dynamics, including population growth, agent relocation, housing choice,
    market pricing, and environmental factors like flood hazards.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    click.echo("ICoM ABM - Housing Market Dynamics Simulator")


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Path to YAML configuration file')
@click.option('--output-dir', '-o', type=click.Path(), default='./results',
              help='Output directory for simulation results')
@click.option('--simulation-name', default='ABM_Baltimore_example',
              help='Name identifier for the simulation')
@click.option('--scenario', default='Baseline',
              help='Scenario name for the simulation run')
@click.option('--intervention', default='Baseline',
              help='Intervention type being simulated')
@click.option('--start-year', type=int, default=2018,
              help='Starting year for the simulation')
@click.option('--no-years', type=int, default=2,
              help='Number of years to simulate')
@click.option('--agent-housing-aggregation', type=int, default=10,
              help='Number of households represented by each agent')
@click.option('--hh-size', type=float, default=2.7,
              help='Average household size')
@click.option('--initial-vacancy', type=float, default=0.20,
              help='Initial vacancy rate in the housing market')
@click.option('--pop-growth-perc', type=float, default=0.01,
              help='Percentage rate of population growth')
@click.option('--perc-move', type=float, default=0.10,
              help='Percentage of agents that move each year')
@click.option('--sensitivity-run', is_flag=True,
              help='Run in sensitivity analysis mode')
@click.option('--record-time', is_flag=True,
              help='Record timing information')
@click.option('--progress', is_flag=True,
              help='Show progress indicators')
def run(config: Optional[str], output_dir: str, **kwargs):
    """
    Run the ICoM ABM simulation.
    
    This command executes a complete agent-based model simulation for housing
    market dynamics. It creates the simulation landscape, populates it with
    household agents, and runs various engines for agent behavior, market
    dynamics, and environmental factors.
    """
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        click.echo(f"Starting ICoM ABM simulation...")
        click.echo(f"Output directory: {output_path.absolute()}")
        
        # Initialize the model
        model = Model(config_file_path=config, **kwargs)
        
        # Run the simulation
        model.run_simulation()
        
        # Save configuration
        config_path = output_path / "simulation_config.yaml"
        model.write_config(str(config_path))
        
        click.echo(f"✅ Simulation completed successfully!")
        click.echo(f"📁 Results saved to: {output_path.absolute()}")
        click.echo(f"⚙️  Configuration saved to: {config_path}")
        
    except Exception as e:
        click.echo(f"❌ Simulation failed: {str(e)}", err=True)
        logger.error(f"Simulation error: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), 
              help='Output file path (default: config_validation.txt)')
def validate_config(config_file: str, output: Optional[str]):
    """
    Validate a configuration file.
    
    This command checks if a YAML configuration file is valid and displays
    the configuration parameters that will be used for simulation.
    """
    try:
        from .data_loader import SimulationConfig
        
        click.echo(f"Validating configuration file: {config_file}")
        
        # Load and validate configuration
        config = SimulationConfig.from_yaml(config_file)
        
        # Display configuration summary
        click.echo("\n📋 Configuration Summary:")
        click.echo("=" * 50)
        click.echo(f"Simulation Name: {config.simulation_name}")
        click.echo(f"Scenario: {config.scenario}")
        click.echo(f"Intervention: {config.intervention}")
        click.echo(f"Start Year: {config.start_year}")
        click.echo(f"Number of Years: {config.no_years}")
        click.echo(f"Agent Housing Aggregation: {config.agent_housing_aggregation}")
        click.echo(f"Household Size: {config.hh_size}")
        click.echo(f"Initial Vacancy: {config.initial_vacancy}")
        click.echo(f"Population Growth: {config.pop_growth_perc}")
        click.echo(f"Move Percentage: {config.perc_move}")
        click.echo(f"Landscape: {config.landscape_name}")
        
        # Save validation report if output specified
        if output:
            with open(output, 'w') as f:
                f.write("ICoM ABM Configuration Validation Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Configuration file: {config_file}\n")
                f.write(f"Validation status: PASSED\n\n")
                f.write("Configuration Parameters:\n")
                for key, value in config.__dict__.items():
                    f.write(f"  {key}: {value}\n")
            
            click.echo(f"✅ Validation report saved to: {output}")
        else:
            click.echo("✅ Configuration is valid!")
            
    except Exception as e:
        click.echo(f"❌ Configuration validation failed: {str(e)}", err=True)
        logger.error(f"Validation error: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.argument('results_dir', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), 
              help='Output file path for the plot')
@click.option('--format', 'plot_format', default='png', 
              type=click.Choice(['png', 'pdf', 'svg', 'jpg']),
              help='Output format for the plot')
@click.option('--dpi', type=int, default=300,
              help='DPI for the output image')
def plot_results(results_dir: str, output: Optional[str], plot_format: str, dpi: int):
    """
    Generate plots from simulation results.
    
    This command creates various visualizations from the simulation results,
    including population maps, change analysis, and statistical plots.
    """
    try:
        # This would need to be implemented based on how results are stored
        # For now, we'll provide a placeholder
        click.echo(f"Generating plots from results in: {results_dir}")
        click.echo("📊 Plot generation functionality to be implemented")
        
        # Example implementation would look like:
        # model = load_model_from_results(results_dir)
        # model.plot_final_population()
        # if output:
        #     plt.savefig(output, dpi=dpi, bbox_inches='tight')
        # else:
        #     plt.show()
        
    except Exception as e:
        click.echo(f"❌ Plot generation failed: {str(e)}", err=True)
        logger.error(f"Plot error: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.option('--template', '-t', type=click.Choice(['basic', 'baltimore', 'custom']),
              default='basic', help='Configuration template to use')
@click.option('--output', '-o', type=click.Path(), 
              default='config.yaml', help='Output configuration file path')
def create_config(template: str, output: str):
    """
    Create a new configuration file from a template.
    
    This command generates a YAML configuration file with default parameters
    that can be customized for specific simulation runs.
    """
    try:
        from .data_loader import SimulationConfig
        
        click.echo(f"Creating configuration file: {output}")
        
        # Create default configuration
        config = SimulationConfig()
        
        # Apply template-specific settings
        if template == 'baltimore':
            config.landscape_name = 'Baltimore'
            config.geo_filename = 'blck_grp_extract_prj.shp'
            config.pop_filename = 'balt_bg_population_2018.csv'
            config.flood_filename = 'bg_perc_100yr_flood.csv'
            config.housing_filename = 'bg_housing_1993.csv'
            config.hedonic_filename = 'simple_anova_hedonic_without_flood_bg0418.csv'
        elif template == 'custom':
            # Interactive configuration creation
            config.simulation_name = click.prompt("Simulation name", default="ABM_Custom")
            config.scenario = click.prompt("Scenario", default="Baseline")
            config.start_year = click.prompt("Start year", type=int, default=2018)
            config.no_years = click.prompt("Number of years", type=int, default=2)
            config.landscape_name = click.prompt("Landscape name", default="Custom")
        
        # Save configuration
        config.to_yaml(output)
        
        click.echo(f"✅ Configuration file created: {output}")
        click.echo("📝 Edit the file to customize parameters for your simulation")
        
    except Exception as e:
        click.echo(f"❌ Configuration creation failed: {str(e)}", err=True)
        logger.error(f"Config creation error: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.argument('results_dir', type=click.Path(exists=True))
@click.option('--format', 'output_format', default='csv',
              type=click.Choice(['csv', 'json', 'excel']),
              help='Output format for the summary')
@click.option('--output', '-o', type=click.Path(),
              help='Output file path for the summary')
def summarize(results_dir: str, output_format: str, output: Optional[str]):
    """
    Generate a summary report from simulation results.
    
    This command creates a comprehensive summary of simulation results,
    including key statistics, changes over time, and performance metrics.
    """
    try:
        click.echo(f"Generating summary from results in: {results_dir}")
        
        # This would need to be implemented based on how results are stored
        # For now, we'll provide a placeholder
        click.echo("📈 Summary generation functionality to be implemented")
        
        # Example implementation would look like:
        # model = load_model_from_results(results_dir)
        # summary = model.combine_housing_dataframes()
        # 
        # if output_format == 'csv':
        #     summary.to_csv(output or 'summary.csv', index=False)
        # elif output_format == 'json':
        #     summary.to_json(output or 'summary.json', orient='records')
        # elif output_format == 'excel':
        #     summary.to_excel(output or 'summary.xlsx', index=False)
        
    except Exception as e:
        click.echo(f"❌ Summary generation failed: {str(e)}", err=True)
        logger.error(f"Summary error: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
def info():
    """
    Display information about the ICoM ABM model.
    
    This command shows version information, available features, and
    basic usage instructions.
    """
    click.echo("ICoM ABM - Agent-Based Model for Housing Market Dynamics")
    click.echo("=" * 60)
    click.echo("Version: 0.1.0")
    click.echo("Author: Jim Yoon (jim.yoon@pnnl.gov)")
    click.echo("Repository: https://github.com/jimyoon/icom_abm")
    click.echo()
    click.echo("Features:")
    click.echo("  • Population growth and agent relocation simulation")
    click.echo("  • Housing market dynamics and pricing")
    click.echo("  • Building development and stock management")
    click.echo("  • Environmental hazard assessment (flood risks)")
    click.echo("  • Zoning and regulatory factors")
    click.echo("  • Comprehensive statistical analysis and visualization")
    click.echo()
    click.echo("Available Commands:")
    click.echo("  run          - Execute a simulation")
    click.echo("  validate-config - Validate configuration files")
    click.echo("  create-config - Create new configuration files")
    click.echo("  plot-results - Generate visualizations")
    click.echo("  summarize    - Create summary reports")
    click.echo()
    click.echo("For detailed help on any command, use: icom-abm <command> --help")


if __name__ == '__main__':
    cli()
