"""each node type has an Op within it"""

class Op:
    """nodes can have several versions of their operation function.

    ops don't return anything! 
    """
    def __init__(self):
        """This should not be overridden without being called."""
        pass

    def inputschanged(self, input, output, stateaccess):
        """If you only define one op function body, make it this one. """
        pass
    
    def created(self, input, output, stateaccess):
        """This is called one time when the node is newly created. It's
        not called when the node instance is pickled/unpickled. Use this
        version to initialize state."""
        # an extra call to changed() should help the outputs get set
        # correctly before any real inputs-changed events come around
        # (assuming this method doesn't get overridden with a
        # specialized version)
        self.inputschanged(input, output, stateaccess)        

    def statechanged(self, input, output, stateaccess):
        '''State might have been changed by a user dragging a parameter or by
        a state being hcanged otherwise.'''
        self.inputschanged(input, output, stateaccess)        

    def clocked(self, input, output, stateaccess):
        self.inputschanged(input, output, stateaccess)        
