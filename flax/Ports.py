# super rough code

class AbstractPort:
    def __init__(self):
        pass
    def put_data(self, value):
        pass
    def get_data(self):
        pass

class Port(AbstractPort):
    "Connects from a node to exactly one node."
    def __init__(self, value=None):
        AbstractPort.__init__(self)
        self.value = value
    def put_data(self, value):
        self.value = value
    def get_data(self):
        return self.value

class MultiPort(AbstractPort):
    "Connects from a node to any number of nodes."
    def __init__(self, values=None):
        AbstractPort.__init__(self)
        self.values = values
    def put_data(self, values):
        self.values = values
    def get_data(self):
        return self.values
