

from parport import *

DUMMY=1

def init(DUMMY_in):
    global DUMMY
    if not DUMMY_in:
        
        getparport()
        DUMMY=0

def sendlevels(levels):
    if DUMMY: return
    levels = list(levels) + [0]
    if levels[14] > 0: levels[14] = 100
    # print "levels", ' '.join(["%3.1f" % l for l in levels])
    outstart()
    for p in range(1,70):
        outbyte(levels[p-1]*255/100)
