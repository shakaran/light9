'''Internal class for StateManager'''

# warning: pseduocode
class NodeInstance:
    ip_addr?
    get_this_nodes_url()

    type = the node type (a subclass of Node)
        ops (get from type)
    input,output = the ports that are created for the node instance
    state = associated state
