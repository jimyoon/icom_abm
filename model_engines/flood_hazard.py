from pynsim import Engine
import logging

class FloodHazard(Engine):
    def __init__(self, target, **kwargs):
        super(FloodHazard, self).__init__(target, **kwargs)

    def run(self):
        logging.info("Running the flood hazard engine, year " + str(self.target.current_timestep.year))
        if self.timestep.year == 2020:
            for bg in self.target.nodes:
                bg.flood_hazard_risk = 100

        pass  # to accommodate debugger


class FloodGenerator(Engine):
    def __init__(self, target, **kwargs):
        super(FloodHazard, self).__init__(target, **kwargs)

    def run(self):
        if self.timestep.year == 2020:
            for bg in self.target.nodes:
                bg.flood_hazard_risk = 100

        pass  # to accommodate debugger