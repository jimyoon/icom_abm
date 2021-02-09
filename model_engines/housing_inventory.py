from pynsim import Engine
import logging

class HousingInventory(Engine):
    """An engine class that identifies housing inventory for the current timestep.

    The HousingInventory class is a pynsim engine that scans through the model landscape and identifies available
    housing inventory for each of the block groups.

    **Target**:
        s.network

    **Args**:
        growth_mode (string): defined as either "perc" or "exog" depending upon simulation mode
        growth_rate (float): if growth_mode = "perc", defines the annual percentage population growth rate

    **Inter-module Outputs/Modifications**:
        s.network.unassigned_hhs (list): list of HHAgent objects that are in the location queue
        s.network.get_institution('all_hh_agents') (list): all_hh_agents institution
    """

    def __init__(self, target, residences_per_unit=100, **kwargs):
        super(HousingInventory, self).__init__(target, **kwargs)
        self.residences_per_unit = residences_per_unit

    def run(self):
        """ Run the HousingInventory Engine.
        """
        for bg in self.target.nodes:
            if bg.available_units == 0:
                logging.info('no more units available for block group: ' + bg.name)
            for unit in range(bg.available_units):
                self.target.available_units_list.append(bg.name)
        pass

    def run_old(self):
        """ Run the HousingInventory Engine.
        """
        for bg in self.target.nodes:
            bg.available_residences = 10000  # temporarily assume 10,000 residences always available
            bg.available_units = (bg.available_residences + self.residences_per_unit // 2) // self.residences_per_unit  # division with rounding to nearest integer
            for unit in range(bg.available_units):
                self.target.available_units_list.append(bg.name)

        pass  # to accommodate debugger