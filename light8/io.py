from parport import *

class ParportDMX:
    def __init__(self, dummy=1, dimmers=68):
        self.dummy = dummy
        if not dummy:
            getparport()
    def sendlevels(self, levels):
        if self.dummy: return
        levels = list(levels) + [0]
        # if levels[14] > 0: levels[14] = 100 # non-dim
        outstart()
        for p in range(1, dimmers + 2):
            outbyte(levels[p-1]*255 / 100)
