from typing import Tuple,Union
import logging
import time

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import contextily as ctx
from pynsim import Network

from .data_loader import SimulationConfig
from .model_classes.simulator import ICOMSimulator
from .model_classes.institutional_categories import AllHouseholdAgents
from .model_engines.agent_creation import NewAgentCreation
from .model_engines.existing_agent_relocation import ExistingAgentReloSampler
from .model_engines.new_agent_location import NewAgentLocation
from .model_engines.existing_agent_relocation import ExistingAgentLocation
from .model_engines.housing_market import HousingMarket
from .model_engines.building_development import BuildingDevelopment
from .model_engines.housing_pricing import HousingPricing
from .model_engines.landscape_statistics import LandscapeStatistics
from .model_classes.institutional_agents import CountyZoningManager, RealEstate
from .model_engines.real_estate_prices import RealEstatePrices
from .model_engines.flood_hazard import FloodHazard
from .model_engines.zoning import Zoning
from .model_classes.urban_agents import HouseholdAgent


# Setup logging
logging.basicConfig(level=logging.INFO)


class Model:
    """Agent-based model for housing market dynamics simulation.
    
    This class implements a comprehensive agent-based model (ABM) for simulating
    housing market dynamics, including population growth, agent relocation,
    housing choice, market pricing, and environmental factors like flood hazards.
    
    The model integrates multiple engines for different aspects of the simulation:
    - Agent creation and relocation
    - Housing market dynamics
    - Building development
    - Environmental hazard assessment
    - Zoning and regulatory factors
    
    Attributes:
        config_file_path (Union[str, None]): Path to configuration YAML file
        config (SimulationConfig): Configuration object containing all simulation parameters
        start_time (float): Timestamp when simulation started
        simulator (ICOMSimulator): The main simulation engine
    """
    
    def __init__(
        self,   
        config: SimulationConfig = None,
        config_file_path: Union[str, None] = None,
        simulation_name: str = 'ABM_Baltimore_example',
        scenario: str = 'Baseline',
        intervention: str = 'Baseline',
        start_year: int = 2018,
        n_years: int = 2,
        agent_housing_aggregation: int = 10,
        household_size: float = 2.7,
        initial_vacancy: float = 0.20,
        pop_growth_mode: str = 'perc',
        pop_growth_perc: float = 0.01,
        inc_growth_mode: str = 'random_agent_replication',
        pop_growth_inc_perc: float = 0.90,
        inc_growth_perc: float = 0.05,
        bld_growth_perc: float = 0.01,
        perc_move: float = 0.10,
        perc_move_mode: str = 'random',
        house_budget_mode: str = 'rhea',
        house_choice_mode: str = 'simple_avoidance_utility',
        simple_anova_coefficients: Tuple[int] = (-121428, 294707, 130553, 128990, 154887, -500000),
        simple_avoidance_perc: float = 0.95,
        budget_reduction_perc: float = 0.90,
        stock_increase_mode: str = 'simple_perc',
        stock_increase_perc: float = 0.05,
        housing_pricing_mode: str = 'simple_perc',
        price_increase_perc: float = 0.05,
        landscape_name: str = 'Baltimore',
        geo_filename: str = '',
        pop_filename: str = '',
        flood_filename: str = '',
        housing_filename: str = '',
        hedonic_filename: str = '',
        field_mapping_file: str = None,
        record_time: bool = False,
        progress: bool = False,
        max_iterations: int = 1,
        name: str = 'ABM_Baltimore_example',
        network: Network = None, 
        sensitivity_run: bool = False,
        county_agent_id: str = '005',
        block_group_sample_size: int = 10, # the number of homes that a new agent samples for residential choice
        zoning_mode: str = 'simple_perc',
        zoning_perc: float = 0.05,
        market_mode: str = 'top_candidate',
    ) -> None:
        """Initialize the Model with configuration parameters.
        
        Args:
            config: SimulationConfig object. If None, uses default parameters.
            config_file_path: Path to YAML configuration file. If None, uses default parameters.
            simulation_name: Name identifier for the simulation.
            scenario: Scenario name for the simulation run.
            intervention: Intervention type being simulated.
            start_year: Starting year for the simulation.
            n_years: Number of years to simulate.
            agent_housing_aggregation: Number of households represented by each agent.
            household_size: Average household size.
            initial_vacancy: Initial vacancy rate in the housing market.
            pop_growth_mode: Mode for population growth calculation.
            pop_growth_perc: Percentage rate of population growth.
            inc_growth_mode: Mode for income growth calculation.
            pop_growth_inc_perc: Percentage of population growth attributed to income.
            inc_growth_perc: Percentage rate of income growth.
            bld_growth_perc: Percentage rate of building growth.
            perc_move: Percentage of agents that move each year.
            perc_move_mode: Mode for determining which agents move.
            house_budget_mode: Mode for calculating housing budgets.
            house_choice_mode: Mode for housing choice decisions.
            simple_anova_coefficients: Coefficients for ANOVA-based utility calculation.
            simple_avoidance_perc: Percentage of agents that avoid flood-prone areas.
            budget_reduction_perc: Percentage reduction in budget for flood-prone areas.
            stock_increase_mode: Mode for housing stock increase.
            stock_increase_perc: Percentage increase in housing stock.
            housing_pricing_mode: Mode for housing price calculations.
            price_increase_perc: Percentage increase in housing prices.
            landscape_name: Name of the geographic landscape.
            geo_filename: Filename for geographic boundary data.
            pop_filename: Filename for population data.
            flood_filename: Filename for flood hazard data.
            housing_filename: Filename for housing data.
            hedonic_filename: Filename for hedonic pricing data.
            record_time: Whether to record timing information.
            progress: Whether to show progress indicators.
            max_iterations: Maximum number of iterations per timestep.
            name: Name of the simulation instance.
            network: Network object (if None, will be created).
            sensitivity_run: Whether this is a sensitivity analysis run.
            county_agent_id: County identifier for zoning decisions.
            block_group_sample_size: Number of block groups to sample for residential choice.
            zoning_mode: Mode for zoning decisions.
            zoning_perc: Percentage for zoning calculations.
            market_mode: Mode for housing market operations.
            
        Returns:
            None
        """
        if config is not None and config_file_path is not None:
            print("Warning: Both config and config_file_path provided. Using config object and ignoring config_file_path.")
            self.config = config
        elif config is not None:
            self.config = config
        elif config_file_path is not None:
            self.config = SimulationConfig.from_yaml(config_file_path)
        else:
            self.config = SimulationConfig(
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
                field_mapping_file=field_mapping_file,
            )
        
        self.config.record_time = record_time
        self.config.progress = progress
        self.config.max_iterations = max_iterations
        self.config.name = name
        self.config.sensitivity_run = sensitivity_run
        self.config.block_group_sample_size = block_group_sample_size
        self.config.market_mode = market_mode
        self.network = network

        if self.config.sensitivity_run is False:
            self.config.county_agent_id = county_agent_id
            self.config.zoning_mode = zoning_mode
            self.config.zoning_perc = zoning_perc

    def run_simulation(self) -> None:
        """Run the ICoM ABM simulation with the configured parameters.
        
        This method initializes and executes a complete agent-based model simulation
        for housing market dynamics. It creates the simulation landscape, populates
        it with household agents, and runs various engines for agent behavior,
        market dynamics, and environmental factors.
        
        The simulation includes:
        - Landscape setup with geographic and demographic data
        - Household agent creation and initialization
        - Various behavioral engines (agent creation, relocation, housing choice)
        - Market dynamics (pricing, development, housing market)
        - Environmental factors (flood hazards, zoning) when not in sensitivity mode
        - Statistical tracking and analysis
        
        Returns:
            None
            
        Raises:
            RuntimeError: If simulation fails to start or complete successfully
        """
        self.start_time = time.time()

        # Create pynsim simulation object and set timesteps, landscape on simulation
        self.simulator = ICOMSimulator(
            network=self.network, 
            record_time=self.config.record_time, 
            progress=self.config.progress, 
            max_iterations=self.config.max_iterations,
            name=self.config.simulation_name, 
            scenario=self.config.scenario, 
            intervention=self.config.intervention, 
            start_year=self.config.start_year, 
            n_years=self.config.n_years
        )

        # sets up timestep information based on model options (start_year, n_years)
        self.simulator.set_timestep_information() 

        # Load geography/landscape information to simulation object
        self.simulator.set_landscape(
            landscape_name=self.config.landscape_name, 
            geo_filename=self.config.geo_filename, 
            pop_filename=self.config.pop_filename,
            pop_fieldname=self.config.get_population_field_name(), 
            flood_filename=self.config.flood_filename,
            housing_filename=self.config.housing_filename, 
            hedonic_filename=self.config.hedonic_filename,
            field_mapping_file=self.config.field_mapping_file
        )
        
        if self.config.sensitivity_run is False:
            # Create a county-level institution (agent) that will make zoning decisions (DEACTIVATE for sensitivity experiments)
            self.simulator.network.add_institution(CountyZoningManager(name=f'zoning_manager_{self.config.county_agent_id}'))
            for block_group in self.simulator.network.nodes:
                if block_group.county == self.config.county_agent_id:
                    self.simulator.network.get_institution(f'zoning_manager_{self.config.county_agent_id}').add_node(block_group)

        if self.config.sensitivity_run is False:
            # Create a real estate agent that will perform analysis of market (hedonic regression) and inform buyers/sellers on prices (DEACTIVATE for sensitivity experiments)
            self.simulator.network.add_institution(RealEstate(name='real_estate'))

        # Create an institution (categorical) that will contain all household agents
        self.simulator.network.add_institution(AllHouseholdAgents(name='all_household_agents'))

        # Create household agents based on initial population data
        self.simulator.convert_initial_population_to_agents(
            no_households_per_agent=self.config.agent_housing_aggregation, 
            simple_avoidance_perc=self.config.simple_avoidance_perc
        )

        # Initialize available units on block groups based on initial population data
        self.simulator.initialize_available_building_units(initial_vacancy=self.config.initial_vacancy)

        if self.config.sensitivity_run is False:
            # Load real estate pricing engine to simulation object (DEACTIVATED for sensitivity experiments)
            target = self.simulator.network.get_institution('real_estate')
            estimation_mode = "OLS_hedonic"
            self.simulator.add_engine(RealEstatePrices(target, estimation_mode=estimation_mode))

        # Load new agent creation engine to simulation object
        target = self.simulator.network
        self.simulator.add_engine(NewAgentCreation(
                target, 
                growth_mode=self.config.pop_growth_mode, 
                growth_rate=self.config.pop_growth_perc, 
                inc_growth_mode=self.config.inc_growth_mode,
                pop_growth_inc_perc=self.config.pop_growth_inc_perc, 
                inc_growth_perc=self.config.inc_growth_perc, 
                no_households_per_agent=self.config.agent_housing_aggregation, 
                household_size=self.config.household_size,
                simple_avoidance_perc=self.config.simple_avoidance_perc
            )
        )

        # Load existing agent sampler (for re-location) to simulation object
        target = self.simulator.network
        self.simulator.add_engine(ExistingAgentReloSampler(target, perc_move=self.config.perc_move))

        # Load new agent location engine to simulation object
        self.simulator.add_engine(
            NewAgentLocation(
                target, 
                self.config.block_group_sample_size, 
                house_choice_mode=self.config.house_choice_mode, 
                simple_anova_coefficients=self.config.simple_anova_coefficients, 
                budget_reduction_perc=self.config.budget_reduction_perc
            )
        )

        # Load existing agent re-location engine to simulation object
        target = self.simulator.network
        self.simulator.add_engine(
            ExistingAgentLocation(
                target, 
                block_group_sample_size=self.config.block_group_sample_size, 
                house_choice_mode=self.config.house_choice_mode, 
                simple_anova_coefficients=self.config.simple_anova_coefficients
            )
        )

        # Load housing market engine to simulation object
        target = self.simulator.network
        self.simulator.add_engine(
            HousingMarket(
                target, 
                market_mode=self.config.market_mode, 
                block_group_sample_size=self.config.block_group_sample_size
            )
        )

        # Load housing market engine to simulation object  # JY to complete
        target = self.simulator.network
        self.simulator.add_engine(
            BuildingDevelopment(
                target, 
                stock_increase_mode=self.config.stock_increase_mode, 
                stock_increase_perc=self.config.stock_increase_perc
            )
        )

        # Load housing market engine to simulation object  # JY to complete
        target = self.simulator.network
        self.simulator.add_engine(
            HousingPricing(
                target, 
                housing_pricing_mode=self.config.housing_pricing_mode, 
                price_increase_perc=self.config.price_increase_perc
            )
        )

        if self.config.sensitivity_run is False:
            # Load flood hazard engine to simulation object (DEACTIVATED for sensitivity run)
            target = self.simulator.network
            self.simulator.add_engine(FloodHazard(target))

        if self.config.sensitivity_run is False: 
            # Load Zoning engine to simulation object (DEACTIVATED for sensitivity run)
            target = self.simulator.network.get_institution(f'zoning_manager_{self.config.county_agent_id}')
            self.simulator.add_engine(
                Zoning(
                    target, 
                    zoning_mode=self.config.zoning_mode, 
                    zoning_perc=self.config.zoning_perc
                    )
            )

        # Load landscape statistics engine to simulation object  # JY to complete
        target = self.simulator.network
        self.simulator.add_engine(LandscapeStatistics(target))

        # Run simulation
        self.simulator.start()

        # Record end time
        end_time = time.time()
        sim_time = end_time-self.start_time
        logging.info("Simulation took (seconds):  %s" % sim_time)


    def write_config(self, config_output_file_path: str) -> None:
        """Write the current configuration to a YAML file.
        
        Args:
            config_output_file_path: The file path where the configuration will be written.
            
        Returns:
            None
            
        Raises:
            IOError: If the file cannot be written to the specified path.
        """
        self.config.to_yaml(config_output_file_path)
        logging.info(f"Config written to {config_output_file_path}")


    def view_network_properties(self) -> dict:
        """See which histories are stored on the network"""
        # See which histories are stored on the network
        return self.simulator.network._properties
    
    def get_history(self, history_name: str) -> pd.DataFrame:
        """Get history for total population"""
        return self.    s.network.get_history(history_name)

    def get_node_history(
            self, 
            node_id: Union[int, str], 
            history_name: str = 'population'
    ) -> pd.DataFrame:
        """Get history for population of a particular block group
        
        Args:
            node_id: The node ID (can be integer index or string ID)
            history_name: The name of the history to retrieve (default: 'population')
            
        Returns:
            pd.DataFrame: The history data for the specified node and history type
        """
        if isinstance(node_id, int):
            return self.simulator.network.nodes[node_id].get_history(history_name)
        else:
            return self.simulator.network.get_node(node_id).get_history(history_name)

    def get_agent_location_history(
            self, agent_id: int, 
            history_name: str = 'location'
    ) -> pd.DataFrame:
        """Get location history for a specific household agent
        
        Args:
            agent_id: The ID of the household agent
            history_name: The name of the history to retrieve (default: 'location')
            
        Returns:
            pd.DataFrame: The location history data for the specified agent
        """
        return self.simulator.network.get_institution('all_household_agents').components[agent_id].get_history(history_name)

    def get_agents_in_node(self, node_id: Union[int, str]) -> list:
        """Get list of agents that reside in a specific block group
        
        Args:
            node_id: The node ID (can be integer index or string ID)
            
        Returns:
            list: The list of household agents residing in the specified node
        """
        if isinstance(node_id, int):
            return self.simulator.network.nodes[node_id].household_agents
        else:
            return self.simulator.network.get_node(node_id).household_agents

    def export_housing_dataframe(
            self, 
            filename: str = "result_test.shp", 
            driver: str = 'ESRI Shapefile'
    ) -> None:
        """Export final housing dataframe to geopackage
        
        Args:
            filename: The output filename (default: "result_test.shp")
            driver: The file format driver (default: 'ESRI Shapefile')
        """
        self.simulator.network.get_history('housing_block_group_df')[-1].to_file(driver=driver, filename=filename)

    def plot_initial_population(
            self, 
            column: str = 'population', 
            cmap: str = 'OrRd', 
            legend: bool = True
    ) -> None:
        """Plot initial population
        
        Args:
            column: The column to plot (default: 'population')
            cmap: The colormap to use (default: 'OrRd')
            legend: Whether to show legend (default: True)
        """
        self.simulator.network.get_history('housing_block_group_df')[0].plot(column=column, cmap=cmap, legend=legend)

    def plot_initial_population_with_basemap(
            self, 
            column: str = 'population', 
            cmap: str = 'OrRd', 
            alpha: float = 0.8, 
            legend: bool = True,
            basemap_source = ctx.providers.CartoDB.Positron
    ) -> None:
        """Plot initial population with basemap
        
        Args:
            column: The column to plot (default: 'population')
            cmap: The colormap to use (default: 'OrRd')
            alpha: The transparency level (default: 0.8)
            legend: Whether to show legend (default: True)
            basemap_source: The basemap source to use (default: ctx.providers.CartoDB.Positron)
        """
        df = self.simulator.network.get_history('housing_block_group_df')[0]
        ax = df.plot(column=column, cmap=cmap, alpha=alpha, legend=legend)
        ctx.add_basemap(ax, source=basemap_source)

    def plot_residuals_with_basemap(
            self, 
            column: str = 'residuals', 
            cmap: str = 'OrRd', 
            alpha: float = 0.8, 
            legend: bool = True,
            basemap_source = ctx.providers.CartoDB.Positron
    ) -> None:
        """Plot residuals with basemap
        
        Args:
            column: The column to plot (default: 'residuals')
            cmap: The colormap to use (default: 'OrRd')
            alpha: The transparency level (default: 0.8)
            legend: Whether to show legend (default: True)
            basemap_source: The basemap source to use (default: ctx.providers.CartoDB.Positron)
        """
        df = self.simulator.network.housing_block_group_df
        ax = df.plot(column=column, cmap=cmap, alpha=alpha, legend=legend)
        ctx.add_basemap(ax, source=basemap_source)

    def plot_final_population(
            self, 
            column: str = 'population', 
            cmap: str = 'OrRd', 
            legend: bool = True
    ) -> None:
        """Plot final population
        
        Args:
            column: The column to plot (default: 'population')
            cmap: The colormap to use (default: 'OrRd')
            legend: Whether to show legend (default: True)
        """
        self.simulator.network.get_history('housing_block_group_df')[-1].plot(column=column, cmap=cmap, legend=legend)

    def plot_population_change(
            self, 
            column: str = 'population', 
            cmap: str = 'OrRd', 
            alpha: float = 0.8, 
            legend: bool = True,
            basemap_source = ctx.providers.CartoDB.Positron
    ) -> None:
        """Plot population change with basemap
        
        Args:
            column: The column to plot (default: 'population')
            cmap: The colormap to use (default: 'OrRd')
            alpha: The transparency level (default: 0.8)
            legend: Whether to show legend (default: True)
            basemap_source: The basemap source to use (default: ctx.providers.CartoDB.Positron)
        """
        gdf = self.simulator.network.get_history('housing_block_group_df')[-1]  # copy of final block_group df
        gdf['population_change'] = self.simulator.network.get_history('housing_block_group_df')[-1]['population'] - self.simulator.network.get_history('housing_block_group_df')[0]['population']
        ax = gdf.plot(column=column, cmap=cmap, alpha=alpha, legend=legend)
        ctx.add_basemap(ax, source=basemap_source)

    def plot_population_change_divergent(
            self, 
            cmap: str = 'RdBu', 
            alpha: float = 0.8, 
            legend: bool = True,
            basemap_source = ctx.providers.CartoDB.Positron
    ) -> None:
        """Plot population change with divergent chloropleth map centered on 0
        
        Args:
            cmap: The colormap to use (default: 'RdBu')
            alpha: The transparency level (default: 0.8)
            legend: Whether to show legend (default: True)
            basemap_source: The basemap source to use (default: ctx.providers.CartoDB.Positron)
        """
        gdf = self.simulator.network.get_history('housing_block_group_df')[-1]  # copy of final block_group df
        gdf['population_change'] = self.simulator.network.get_history('housing_block_group_df')[-1]['population'] - self.simulator.network.get_history('housing_block_group_df')[0]['population']
        # normalize color
        vmin, vmax, vcenter = gdf.population_change.min(), gdf.population_change.max(), 0
        norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
        # create a normalized colorbar
        cbar = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        # with normalization
        ax = gdf.plot(column='population_change', cmap=cmap, alpha=alpha, norm=norm, legend=legend)
        ctx.add_basemap(ax, source=basemap_source)

    def plot_population_side_by_side(
            self, 
            column: str = 'population', 
            cmap: str = 'OrRd', 
            figsize: tuple = (15, 7), 
            legend: bool = True
    ) -> None:
        """Plot initial and final population side-by-side with consistent scale
        
        Args:
            column: The column to plot (default: 'population')
            cmap: The colormap to use (default: 'OrRd')
            figsize: The figure size (default: (15, 7))
            legend: Whether to show legend (default: True)
        """
        # Get min, max, average for color scale
        vmin = min(self.simulator.network.get_history('housing_block_group_df')[0][column].min(), 
                  self.simulator.network.get_history('housing_block_group_df')[-1][column].min())
        vmax = min(self.simulator.network.get_history('housing_block_group_df')[0][column].max(), 
                  self.simulator.network.get_history('housing_block_group_df')[-1][column].max())
        vcenter = np.mean([vmin, vmax])
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        self.simulator.network.get_history('housing_block_group_df')[0].plot(column=column, vmin=vmin, vmax=vmax, cmap=cmap, ax=ax1, legend=legend)
        self.simulator.network.get_history('housing_block_group_df')[-1].plot(column=column, vmin=vmin, vmax=vmax, cmap=cmap, ax=ax2, legend=legend)

    def plot_population_change_vs_sales_price(self, style: str = 'o') -> None:
        """Create a scatterplot of population change vs sales price
        
        Args:
            style: The plot style (default: 'o')
        """
        df = pd.DataFrame(self.simulator.network.housing_block_group_df)
        df['population_change'] = df['population'] - df['pop1990']
        df.plot(x='salesprice1993', y='population_change', style=style)

    def plot_population_change_vs_sales_price_with_hue(self, aspect: float = 1.61) -> None:
        """Create a scatterplot of population change vs sales price with average income as hue
        
        Args:
            aspect: The aspect ratio of the plot (default: 1.61)
        """
        import seaborn
        df = pd.DataFrame(self.simulator.network.housing_block_group_df)
        df['population_change'] = df['population'] - df['pop1990']
        seaborn.relplot(data=df, x='salesprice1993', y='population_change', hue='average_income', aspect=aspect)

    def plot_population_change_percentage_vs_flood_area_with_hue(
            self,
            aspect: float = 1.61
    ) -> None:
        """Create a scatterplot of population change percentage vs flood area with average income as hue
        
        Args:
            aspect: The aspect ratio of the plot (default: 1.61)
        """
        import seaborn
        df = pd.DataFrame(self.simulator.network.housing_block_group_df)
        df['population_change_perc'] = (df['population'] - df['pop1990']) / df['pop1990']
        seaborn.relplot(data=df, x='perc_fld_area', y='population_change_perc', hue='average_income', aspect=aspect)

    def plot_price_change_vs_flood_area_with_hue(self, aspect: float = 1.61) -> None:
        """Create a scatterplot of price change vs flood area with average income as hue
        
        Args:
            aspect: The aspect ratio of the plot (default: 1.61)
        """
        import seaborn
        df = pd.DataFrame(self.simulator.network.housing_block_group_df)
        df['price_change'] = df['new_price'] - df['salesprice1993']
        seaborn.relplot(data=df, x='perc_fld_area', y='price_change', hue='average_income', aspect=aspect)

    def plot_flood_zone_metric_over_time(
            self, 
            flood_coefficient: float = -1000000, 
            csv_file: str = 'temp_flood.csv'
    ) -> None:
        """Plot metric in flood zone threshold over time
        
        Args:
            flood_coefficient: The flood coefficient value (default: -1000000)
            csv_file: Path to CSV file with additional data (default: 'temp_flood.csv')
        """
        import seaborn as sns
        
        years = []
        pop_perc_change = []
        fld_coeff_list = []
        
        for t in range(self.simulator.network.current_timestep_idx):
            df = self.simulator.network.get_history('housing_block_group_df')[t]
            df_fld = df[(df.perc_fld_area >= df.perc_fld_area.quantile(.9))]
            pop_perc_change_fld = (df_fld.average_income.sum() - df_fld.mhi1990.sum()) / df_fld.mhi1990.sum()
            years.append(t+1)
            pop_perc_change.append(pop_perc_change_fld)
            fld_coeff_list.append(flood_coefficient)
        
        data_dict = {
            'Model Year': years,
            'Pop Perc Change Flood Zone': pop_perc_change,
            'Flood Coefficient': fld_coeff_list
        }
        df = pd.DataFrame(data_dict)
        
        # Load additional data from CSV if file exists
        try:
            df_append = pd.read_csv(csv_file, index_col=False)
            df = pd.concat([df, df_append], join='inner')
        except FileNotFoundError:
            pass  # Continue without additional data if file doesn't exist
        
        sns.lineplot(x='Model Year',
                     y='Pop Perc Change Flood Zone',
                     hue='Flood Coefficient',
                     data=df)

    def combine_housing_dataframes(self) -> pd.DataFrame:
        """Combine relevant housing dataframes from each model run year into a single dataframe
        
        Returns:
            pd.DataFrame: Combined dataframe with housing data from all timesteps
        """
        first = True
        for t in range(self.simulator.network.current_timestep_idx):
            df = self.simulator.network.get_history('housing_block_group_df')[t]
            df = df[['GEOID','GISJOIN','new_price','population','occupied_units','available_units','demand_exceeds_supply',
                   'perc_fld_area','mhi1990','salesprice1993','pop1990', 'average_income']].copy()
            df['model_year'] = t+1
            if first:
                df_combined = df
                first = False
            else:
                df_combined = pd.concat([df_combined,df])
        
        return df_combined

