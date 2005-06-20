"""node that performs a simple gamma (exp) function on its input"""

class GammaOps(Ops):
    def started(self, input, output, stateaccess):
        self.startmeup(stateaccess)
    def changed(self, input, output, stateaccess):
        port.output = port.input ** stateaccess.gamma + stateaccess.offset
        stateaccess.lastvalue = State.FloatingPoint(port.input)

        output = gamma(input)
    # no timed function
    def startmeup(self, stateaccess):
        # whatever
        pass

class Gamma(Node):
    def __init__(self):
        Node.__init__(self)
        self.node_params = {'gamma':State.FloatingPoint,'offset':State.FloatingPoint}
        self.ops = GammaOps()

    def getnodeparams(self):
        return self.node_params
        
    def getports(self):
        return (Port('a', optional=1),
                Port('b'))

    def __str__(self):
        return "3"

world.register_node(Gamma)
