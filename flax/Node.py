# super rough code

# The magic value
NoChange = "NoChange"

class NodeType:
    def __init__(self, iports=None, oports=None):
        make_attributes_from_args('iports', 'oports')
    def process(self,iports,oports):
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
        NodeType.__init__(self, iports={'in1' : Port(), 
                                        'scale1' : Port()},
                                oports={'out1' : Port()},
    def process(self, iports, oports):
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

Persistence
node instance saves:
    node name, id, and such
    input ports:
        any port details
        what the port connects to
    values:
        maybe UI.Scale level
        maybe group contents


p=InputPort(node=self,minconns=1,maxconns=2) # an input port to this node
p.connect(othernode)
print p.connections()
p.connect(yetanother)

op=OutputPort(node=self) # an output port
print op.connections() # lists all the nodes that call us an input node
op.connect(n) # calls n.connect(self)



        
Ports
    Port: "scalar"
    MultiPort: "array of Port"
    ^ all wrong

    Ports II:
        min/max number of connections
           (failure to fit these numbers means port is "deactivated")
        "Normal" ports are min=1, max=1
        "Multiports" are min=0, max=None
        "Binary" ports are min=2, max=2
        oh yeah, there are two totally different types of ports

        Input ports: min/max numbers of connections
           store current connections
        Output ports: nothing
           store nothing!

fake node persistence for subtract node

<!-- "my subtract" is a unique id -->
<!-- drew: there is no such thing as a subtract group -->
<node name="my subtract" type="math.Add">
  <inputs>
    <port name="in1">
       <noderef name="node I"/>
       <noderef name="node II"/>
    </port>
  </inputs>
  <state>
  </state>
    
</node>


<node name="the group" type="group">

  <!-- all of the port names of the group are being made up right
  here- a group has no preset inputs or outputs-->

  <inputs>
    <port name="group-in 1">
      <noderef name="node5"/>
      <noderef name="node6"/>
    </port>
  </inputs>
  
  <state>  
    <children>
      <noderef name="node3">
        <connect localPort="in1" groupPort="group-in1"/>
      </noderef>
      <noderef name="node4">
        <connect localPort="in1" groupPort="group-in1"/>
        <connect localPort="out1" groupPort="theoutput"/>
      </noderef>
    </children>

  </state>  
</node>

<node name="preset value" type="source.Scalar">
  <!-- no inputs, node has output only -->
  <state>
    <value>8.3</value>

    <minvalue>0</minvalue>
    <maxvalue>100</maxvalue>
    
    <gui>
      <slider res=".1" height="200" bgcolor="red"/>
      <priority>very high</priority>
      <xpos>395</xpos>
      <ypos>21</ypos>
    </gui>
    
  </state>

</node>
