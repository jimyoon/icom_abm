from pynsim import Institution

class LeveeManager(Institution):
    def __init__(self, name, **kwargs):
        super(LeveeManager, self).__init__(name, **kwargs)

class ZoningManager(Institution):
    def __init__(self, name, **kwargs):
        super(ZoningManager, self).__init__(name, **kwargs)