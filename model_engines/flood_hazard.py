from pynsim import Engine

class FloodHazard(Engine):
    def __init__(self, target, **kwargs):
        super(FloodHazard, self).__init__(target, **kwargs)

    def run(self):
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