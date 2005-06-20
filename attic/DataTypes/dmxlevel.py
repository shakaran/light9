###

"""
Snippet 0x93.2b: example of outputting a special type

class DMXLevel(float):
  def __init__(self,f):
    self.value = min(max(0,f),255)
  ...
  def __get__(...) # maybe

output.dmxlevel = DMXLevel(300)
    
>>> print output.dmxlevel
    255

dmxlevel = DMXLevel(3)
dmxlevel += 800
d = d + 800

There's yer problem:
http://python.org/doc/current/ref/numeric-types.html#l2h-152

"""
