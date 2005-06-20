

class ops(Ops):
    def changed(self, input, output, stateaccess):
        input.dmx
    
class DMXOut(Node):
    def get_default_ports(self):
        return {'dmx':InputPort(DMX,required=1,maxpins=1)}
    def get_default_params(self):
        return {'outputrefresh':NextTime,'outputdevice':DMXDevice}
