# super rough code

# The magic value
NoChange = "NoChange"

class NodeType:
    def __init__(self, iports=None, oports=None):
        make_attributes_from_args('iports', 'oports')
    def process(self):
        pass
        # TODO: handle NoChange stuff

class AddNode(NodeType):
    """Adds two nodes together"""
    def __init__(self):
        NodeType.__init__(self, iports={'in1' : Port, 'in2' : Port},
                                oports={'out1' : Port})
    def process(self, ports):
        ports.out1 = ports.in1 + ports.in2

class SumNode(NodeType):
    """Adds any number of nodes together"""
    def __init__(self, empty_val=0):
        NodeType.__init__(self, iports={'in1' : MultiPort},
                                oports={'out1' : Port})
        self.empty_val = 0
    def process(self, ports):
        val = self.empty_val
        for p in ports.in1:
            val += p

        ports.out1 = val

class FadeNode(NodeType):
    """Provides a UI scaler to let you fade a value"""
    def __init__(self):
        NodeType.__init__(self, iports={'in1' : Port, 
                                        'scale1' : Port},
                                oports={'out1' : Port},
    def process(self, ports):
        ports.out1 = ports.in1 * ports.scale1 

class FadeConstellation(Constellation):
    """This somehow describes the following:

    [      ]    [ UI.Scale ]
      |            |
      | in         | scale
      |      ____ /
      |      |
    [ FadeNode ]
      | 
      | out
      |
    [      ]

    Maybe this is a group (I like this more):

      |
      | in
      |                FadeGroup
   - - - - - - - - - - - - -- - -
  |   |                          |
      |          [ UI.Scale ]    
  |   |            |             |
      | in         | scale  
  |   |      ____ /              |
      |      |
  | [ FadeNode ]                 |
      | 
  |   | out                      |
      |                          
  \ - - - - - - - - - - - -- - - /
      |
      | out
      | 
    """
