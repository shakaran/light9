''' Database of NodeInstances, part of the Core '''

# this will be hard to write until NodeInstances are written, but I'll try
# anyway

__version__ = "$Id: StateManager.py,v 1.1 2002/07/04 00:21:35 drewp Exp $"

class StateManager:
    '''StateManager is the second of the core to be built.  It should be 
       after the network, then the scheduler.

       After StateManager is constructed, you probably want to do load_state().
       All of the above is taken care of by the Core module.
       
       Also, in general, 'name' indicates the name of a node, in NRL
       (like URL) syntax:
       node:group/innergroup/node

       or

       node:node

       if node is in the top level group (the root, or universe, or whatever
        you want to call it
    '''
    def __init__(self, network):
        '''Sets up some dicts, maybe'''
        # need some storage locations, etc.
        self.network = network
    def save_state(self):
        '''Save state to disk'''
        pass
    def load_state(self):
        '''Load state from disk'''
        pass
    def get_input_names(self, name):
        '''Get the names of the nodes which are inputs to a node'''
        pass
    def get_output_names(self, name):
        '''Get the names of the nodes which are outputs to a node'''
        pass
