"""each node descends from this base class"""

class NodeType:
    def __init__(self):
        """TBD"""
        self.ops = Ops()

        ''' maybe
        self.iports = []
        self.oports = []
        self.params = []
        '''
    def get_state(self, stateaccess):
        """This is similar to the pickle.__getstate__ method, except
        we need this alternate version in order to give the node
        (which holds no state) access to its instance's state.

        If your node keeps some transient items in its state dict
        (such as a buffer of recently received inputs), it may want to
        return a copy of the state dict without those items. set_state
        should restore them properly (if they're missing from the
        current state, which they might not be).

        get_state might be called at any time, and it's certainly not
        guaranteed that the node instance is going out of service.
        get_state might get called to checkpoint the nodes for a
        backup, for example. set_state might also get called anytime.
        """
        return stateaccess
    def set_state(self, stateaccess, dict):
        """dict (named after the pickle.__setstate__ argument) is
        always a value that was previously returned from
        get_state. Don't adjust the current nodetype's state, of course;
        use dict to update stateaccess.  If there were elements
        missing from dict (see the note in get_state for why this
        might be the case), you should restore them here as
        appropriate.
        """        
        stateaccess.update(dict)
    def get_default_params(self):
        '''Returns dictionary of param names and DataType instances.  DataTypes 
        can be given values'''
        return {}
    def get_default_ports(self):
        '''Returns pinless port objects'''
        return {}
