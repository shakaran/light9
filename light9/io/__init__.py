from __future__ import division
import sys

class BaseIO:
    def __init__(self):
        self.dummy=1
        self.__name__ = 'BaseIO'
        # please override and set __name__ to your class name

    def golive(self):
        """call this if you want to promote the dummy object becomes a live object"""
        print "IO: %s is going live" % self.__name__
        self.dummy=0
        # you'd override with additional startup stuff here,
        # perhaps even loading a module and saving it to a class
        # attr so the subclass-specific functions can use it

    def godummy(self):
        print "IO: %s is going dummy" % self.__name__
        self.dummy=1
        # you might override this to close ports, etc
        
    def isdummy(self):
        return self.dummy

    def __repr__(self):
        if self.dummy:
            return "<dummy %s instance>" % self.__name__
        else:
            return "<live %s instance>" % self.__name__

    # the derived class will have more methods to do whatever it does,
    # and they should return dummy values if self.dummy==1.

class ParportDMX(BaseIO):
    def __init__(self, dimmers=68):
        BaseIO.__init__(self)
        self.__name__='ParportDMX'
        self.dimmers = dimmers

    def golive(self):
        BaseIO.golive(self)
        import parport
        self.parport = parport
        self.parport.getparport()
        
    def sendlevels(self, levels):
        if self.dummy:
            return
        
        levels = list(levels) + [0]
        # if levels[14] > 0: levels[14] = 100 # non-dim
        self.parport.outstart()
        for p in range(1, self.dimmers + 2):
            self.parport.outbyte(levels[p-1]*255 / 100)

class UsbDMX(BaseIO):
    def __init__(self, dimmers=72):
        BaseIO.__init__(self)
        self.__name__ = "UsbDMX"
        self.out = None
        self.dimmers = dimmers

    def _dmx(self):
        if self.out is None:
            sys.path.append("dmx_usb_module")
            from dmx import Dmx
            self.out = Dmx()
        return self.out
        

    def sendlevels(self, levels):
        if self.dummy:
            return
        # I was outputting on 76 and it was turning on the light at
        # dmx75. So I added the 0 byte.
        packet = '\x00' + ''.join([chr(int(lev * 255 / 100)) 
                                  for lev in levels]) + "\x55"
        self._dmx().write(packet)

class SerialPots(BaseIO):
    """
    this is a dummy object (that returns zeros forever) until you call startup()
    which makes it bind to the port, etc
    
    """
    def __init__(self):
        # no init here- call getport() to actually initialize
        self.dummy=1
        self.__name__='SerialPots' # i thought this was automatic!

    def golive(self):
        """
        ls -l /dev/i2c-0
        crw-rw-rw-    1 root     root      89,   0 Jul 11 12:27 /dev/i2c-0
        """
        import serport
        self.serport = serport
        
        self.f = open("/dev/i2c-0","rw")

        # this is for a chip with A0,A1,A2 lines all low:
        port = 72

        from fcntl import *

        I2C_SLAVE = 0x0703  #/* Change slave address                 */
        ioctl(self.f,I2C_SLAVE,port)
        self.dummy=0

    def godummy(self):
        BaseIO.godummy(self)
        self.f.close()

    def getlevels(self):
        if self.dummy:
            return (0,0,0,0)
        else:
            return self.serport.read_all_adc(self.f.fileno())


if __name__=='__main__':
    
    """ tester program that just dumps levels for a while """
    from time import sleep
    from serport import *

    i=0
    while i<100:
        sleep(.033)
        i=i+1

        print read_all_adc(f.fileno())

