from pynsim import Institution

class AllHHAgents(Institution):
    def __init__(self, name, **kwargs):
        super(AllHHAgents, self).__init__(name, **kwargs)