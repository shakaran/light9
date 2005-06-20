"""delay node outputs the input a fixed time later"""


class DelayOps(Ops):
    def clocked(self, input, output, stateaccess):
        stateaccess.buffer


class Delay(Node):
    def __init__(self):
        Node.__init__(self)
        
    def getnodeparams(self):
        return {'delay':State.Time}
