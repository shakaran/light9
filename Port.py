from nodetypes import DiscoType

ANY = -1

class Port:
    def __setattr__(self, key, value):
        '''Alias for __setitem___'''
        self[key] = value
    def __setitem__(self, key, value):
        pass
    def __getattr__(self, key):
        '''Alias for __getitem___'''
        return self[key]
    def __getitem__(self, key):
        pass

class InputPort(Port):
    def __init__(self, required=1, maxpins=ANY):
        self.pins = []

class OutputPort(Port):
    def __init__(self):
        self.pins = []

class Pin:
    def __init__(self, connection, value=DiscoType):
        pass

'''
Snippet Pi=3: RFC 2: New port semantics

# an example of the max node's op
def changed(self, inputs):
    # note how this function does not use stateaccess, as it doesn't use state
    return max(inputs.values())

# so, how the heck does this work?
# we check the function to get the names of kw args in the function.
# we always pass self, but everything else is optional
# the node asked for inputs, which looks like this:
# inputs = {'portname' : PortObj, 'portname2', PortObj}
# somehow, the PortObjs are max'ible.
# the node has only one output so it can just return the value to set the 
# output.  (maybe)
# alteratively, if we decide that you always return a new dict of outputs:
# return {'outputportname' : max(inputs.values())}
# which isn't horrible, but not great

# another example: an adder.  the node has ports A and B, and an output C:
# C also gets capped at stateaccess[min].
def changed(self, a, b, c, stateaccess):
    c.set(max(stateaccess['min'], a + b))
    return {}

# or:
def changed(self, a, b, stateaccess):
    c = max(stateaccess['min'], a + b)
    return {'c' : c}

# which i think is clearer.  doing all port changes at the end has some
# book-keeping advantages (we can detect easily which ports are changed)
# the counter node could work this way:

def changed(self, someoutput):
    return {'someoutput' : someoutput + 1}
'''

'''
type 1: a, b, d, e
type 2: b, c, d, f

conversion maps:
a -> [ ]
b -> b
d -> d
e -> f
'''
