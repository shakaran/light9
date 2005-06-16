from light9 import dmxclient
from light9.Submaster import Submaster

# later, this stuff will talk to a SubServer
class SubClient:
    def __init__(self):
        pass # we may later need init code for network setup
    def get_levels_as_sub(self):
        """Subclasses must implement this method and return a Submaster
        object."""
    def get_dmx_list(self):
        maxes = self.get_levels_as_sub()
        return maxes.get_dmx_list()
    def send_sub(self, sub):
        levels = sub.get_dmx_list()
        dmxclient.outputlevels(levels)
    def send_levels(self):
        levels = self.get_dmx_list()
        dmxclient.outputlevels(levels)
    def send_levels_loop(self, delay=1000):
        """This function assumes that we are an instance of a Tk object
        (or at least that we have an 'after' method)"""
        self.send_levels()
        self.after(delay, self.send_levels_loop, delay)
    def send_zeroes(self):
        self.send_sub(Submaster('empty', {}, temporary=1))
