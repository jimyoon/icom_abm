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
@click.version_option(version="0.1.0", prog_name="CHANCE-C")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output except errors')
def cli(verbose: bool, quiet: bool):
    """
    CHANCE-C - Agent-Based Model for housing market dynamics simulation.
    
    This tool provides a comprehensive framework for simulating housing market
    dynamics, including population growth, agent relocation, housing choice,
    market pricing, and environmental factors like flood hazards.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    click.echo("CHANCE-C - Housing Market Dynamics Simulator")


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
@click.option('--household-size', type=float, default=2.7,
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
@click.option('--block-group-sample-size', default=10, help='Number of block groups to sample for residential choice')
@click.option('--zoning-mode', default='simple_perc', help='Mode for zoning decisions')
@click.option('--zoning-perc', default=0.05, help='Percentage for zoning calculations')
@click.option('--market-mode', default='top_candidate', help='Mode for housing market operations')
@click.option('--landscape-name', default='Baltimore', help='Name of the geographic landscape')
@click.option('--geo-filename', help='Filename for geographic boundary data (uses default if not specified)')
@click.option('--pop-filename', help='Filename for population data (uses default if not specified)')

@click.option('--flood-filename', help='Filename for flood hazard data (uses default if not specified)')
@click.option('--housing-filename', help='Filename for housing data (uses default if not specified)')
@click.option('--hedonic-filename', help='Filename for hedonic pricing data (uses default if not specified)')
@click.option('--field-mapping-file', help='Path to field mapping configuration file')
def run(config: Optional[str], output_dir: str, **kwargs):
    """
    Run the ICoM ABM simulation with the specified configuration.
    
    Args:
        config: Path to configuration YAML file (optional)
        output_dir: Directory to save simulation outputs
        **kwargs: Additional configuration parameters
    """
    # Extract parameters from kwargs
    simulation_name = kwargs.get('simulation_name', 'ABM_Baltimore_example')
    scenario = kwargs.get('scenario', 'Baseline')
    intervention = kwargs.get('intervention', 'Baseline')
    start_year = kwargs.get('start_year', 2018)
    n_years = kwargs.get('n_years', 2)
    agent_housing_aggregation = kwargs.get('agent_housing_aggregation', 10)
    household_size = kwargs.get('household_size', 2.7)
    initial_vacancy = kwargs.get('initial_vacancy', 0.20)
    pop_growth_mode = kwargs.get('pop_growth_mode', 'perc')
    pop_growth_perc = kwargs.get('pop_growth_perc', 0.01)
    inc_growth_mode = kwargs.get('inc_growth_mode', 'random_agent_replication')
    pop_growth_inc_perc = kwargs.get('pop_growth_inc_perc', 0.90)
    inc_growth_perc = kwargs.get('inc_growth_perc', 0.05)
    bld_growth_perc = kwargs.get('bld_growth_perc', 0.01)
    perc_move = kwargs.get('perc_move', 0.10)
    perc_move_mode = kwargs.get('perc_move_mode', 'random')
    house_budget_mode = kwargs.get('house_budget_mode', 'rhea')
    house_choice_mode = kwargs.get('house_choice_mode', 'simple_avoidance_utility')
    simple_anova_coefficients = kwargs.get('simple_anova_coefficients', (-121428, 294707, 130553, 128990, 154887, -500000))
    simple_avoidance_perc = kwargs.get('simple_avoidance_perc', 0.95)
    budget_reduction_perc = kwargs.get('budget_reduction_perc', 0.90)
    stock_increase_mode = kwargs.get('stock_increase_mode', 'simple_perc')
    stock_increase_perc = kwargs.get('stock_increase_perc', 0.05)
    housing_pricing_mode = kwargs.get('housing_pricing_mode', 'simple_perc')
    price_increase_perc = kwargs.get('price_increase_perc', 0.05)
    landscape_name = kwargs.get('landscape_name', 'Baltimore')
    geo_filename = kwargs.get('geo_filename', 'blck_grp_extract_prj.shp')
    pop_filename = kwargs.get('pop_filename', 'balt_block_group_population_2018.csv')
    flood_filename = kwargs.get('flood_filename', 'block_group_perc_100yr_flood.csv')
    housing_filename = kwargs.get('housing_filename', 'block_group_housing_1993.csv')
    hedonic_filename = kwargs.get('hedonic_filename', 'simple_anova_hedonic_without_flood_block_group0418.csv')
    record_time = kwargs.get('record_time', False)
    progress = kwargs.get('progress', False)
    max_iterations = kwargs.get('max_iterations', 1)
    name = kwargs.get('name', 'ABM_Baltimore_example')
    sensitivity_run = kwargs.get('sensitivity_run', False)
    county_agent_id = kwargs.get('county_agent_id', '005')
    block_group_sample_size = kwargs.get('block_group_sample_size', 10)
    zoning_mode = kwargs.get('zoning_mode', 'simple_perc')
    zoning_perc = kwargs.get('zoning_perc', 0.05)
    market_mode = kwargs.get('market_mode', 'top_candidate')
    
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        click.echo(f"Starting CHANCE-C simulation...")
        click.echo(f"Output directory: {output_path.absolute()}")
        
        # Create and run the model
        model = Model(
            config_file_path=config,
            simulation_name=simulation_name,
            scenario=scenario,
            intervention=intervention,
            start_year=start_year,
            n_years=n_years,
            agent_housing_aggregation=agent_housing_aggregation,
            household_size=household_size,
            initial_vacancy=initial_vacancy,
            pop_growth_mode=pop_growth_mode,
            pop_growth_perc=pop_growth_perc,
            inc_growth_mode=inc_growth_mode,
            pop_growth_inc_perc=pop_growth_inc_perc,
            inc_growth_perc=inc_growth_perc,
            bld_growth_perc=bld_growth_perc,
            perc_move=perc_move,
            perc_move_mode=perc_move_mode,
            house_budget_mode=house_budget_mode,
            house_choice_mode=house_choice_mode,
            simple_anova_coefficients=simple_anova_coefficients,
            simple_avoidance_perc=simple_avoidance_perc,
            budget_reduction_perc=budget_reduction_perc,
            stock_increase_mode=stock_increase_mode,
            stock_increase_perc=stock_increase_perc,
            housing_pricing_mode=housing_pricing_mode,
            price_increase_perc=price_increase_perc,
            landscape_name=landscape_name,
            geo_filename=geo_filename,
            pop_filename=pop_filename,
            flood_filename=flood_filename,
            housing_filename=housing_filename,
            hedonic_filename=hedonic_filename,
            record_time=record_time,
            progress=progress,
            max_iterations=max_iterations,
            name=name,
            sensitivity_run=sensitivity_run,
            county_agent_id=county_agent_id,
            block_group_sample_size=block_group_sample_size,
            zoning_mode=zoning_mode,
            zoning_perc=zoning_perc,
            market_mode=market_mode,
        )
        
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
        click.echo(f"Number of Years: {config.n_years}")
        click.echo(f"Agent Housing Aggregation: {config.agent_housing_aggregation}")
        click.echo(f"Household Size: {config.hh_size}")
        click.echo(f"Initial Vacancy: {config.initial_vacancy}")
        click.echo(f"Population Growth: {config.pop_growth_perc}")
        click.echo(f"Move Percentage: {config.perc_move}")
        click.echo(f"Landscape: {config.landscape_name}")
        
        # Save validation report if output specified
        if output:
            with open(output, 'w') as f:
                f.write("CHANCE-C Configuration Validation Report\n")
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
            # Note: File paths will use defaults automatically
        elif template == 'custom':
            # Interactive configuration creation
            config.simulation_name = click.prompt("Simulation name", default="ABM_Custom")
            config.scenario = click.prompt("Scenario", default="Baseline")
            config.start_year = click.prompt("Start year", type=int, default=2018)
            config.n_years = click.prompt("Number of years", type=int, default=2)
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
    Display information about the CHANCE-C model.
    
    This command shows version information, available features, and
    basic usage instructions.
    """
    click.echo("CHANCE-C - Agent-Based Model for Housing Market Dynamics")
    click.echo("=" * 60)
    click.echo("")
    click.echo("📊 Features:")
    click.echo("  • Agent-based modeling of housing market dynamics")
    click.echo("  • Flood risk and extreme weather integration")
    click.echo("  • Spatial analysis with geographic data")
    click.echo("  • Policy simulation and intervention testing")
    click.echo("  • Built-in visualization and analysis tools")
    click.echo("")
    click.echo("🚀 Quick Start:")
    click.echo("  # Run with default example data (no setup needed!)")
    click.echo("  chance-c run")
    click.echo("")
    click.echo("  # Run with custom configuration")
    click.echo("  chance-c create-config --template baltimore -o my_config.yaml")
    click.echo("  chance-c run --config my_config.yaml")
    click.echo("")
    click.echo("📁 Default Data:")
    click.echo("  CHANCE-C includes Baltimore-area example data files:")
    click.echo("  • Census block group boundaries")
    click.echo("  • 2018 population data")
    click.echo("  • FEMA 100-year flood zones")
    click.echo("  • 1993 housing characteristics")
    click.echo("  • Hedonic regression results")
    click.echo("")
    click.echo("  You can override any data file by specifying custom paths.")
    click.echo("")
    click.echo("📖 For more information:")
    click.echo("  • Documentation: See README.md")
    click.echo("  • Field mapping: See chance_c/data/FIELD_MAPPING_README.md")
    click.echo("  • Example notebook: See notebooks/quickstarter.ipynb")
    click.echo("")
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
    click.echo("For detailed help on any command, use: chance-c <command> --help")


if __name__ == '__main__':
    cli()
