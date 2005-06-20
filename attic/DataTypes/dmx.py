
class DMX(list):
    """the signal that goes on a real-life dmx wire. it's up to 512
    un-named channels each with a 8-bit value on each channel. this type
    is useful for a DMXOut node or DMXLevelDisplay node. the channels are
    stored in a python list where the first channel is at index 0. the
    first channel in dmx terminology would be called channel 1."""
    
    def __init__(self,dmxlevels):
        if len(dmxlevels)>512:
            raise TypeError("DMX objects can't have more than 512 channels")
        list.extend(dmxlevels) # list.__init__ did't work right

    def append(self,level):
        if len(self)==512:
            raise TypeError("DMX objects can't have more than 512 channels")
        list.append(self,level)

    def extend(self,levels):
        if len(self)+len(levels)>512:
            raise TypeError("DMX objects can't have more than 512 channels")
        list.extend(self,levels)

    def __setslice__(self,i,j,seq):
        newlength = len(self)-(max(0,j)-max(0,i))+len(seq)
        # we could check if newlength>512, but any length-changing slice is
        # probably wrong for this datatype
        if newlength!=len(self):
            raise NotImplementedError("Different-length setslice would disturb DMX channels")
        list.__setslice__(self,i,j,seq)
        
