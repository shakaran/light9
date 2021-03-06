"""calculates your updates-per-second"""

from __future__ import division
import time

class Updatefreq:
    """make one of these, call update() on it as much as you want,
    and then float() or str() the object to learn the updates per second.

    the samples param to __init__ specifies how many past updates will
    be stored.  """
    
    def __init__(self,samples=20):
        self.times=[0]
        self.samples=samples

    def update(self):

        """call this every time you do an update"""
        self.times=self.times[-self.samples:]
        self.times.append(time.time())

    def __float__(self):
        
        """a cheap algorithm, for now, which looks at the first and
        last times only"""

        try:
            hz=len(self.times)/(self.times[-1]-self.times[0])
        except ZeroDivisionError:
            return 0.0
        return hz
    def __str__(self):
        return "%.2fHz"%float(self)
