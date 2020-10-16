from pynsim import Engine

class Zoning(Engine):
    def __init__(self, target, **kwargs):
        super(Zoning, self).__init__(target, **kwargs)

    def run(self):
        if self.timestep.year == 2020:
            self.target.determine_zoning()