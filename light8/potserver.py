#!/usr/bin/python

import socket

from io import *

pots = SerialPots()
pots.golive()

while 1:
    l=pots.getlevels()
    try:
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("dash", socket.getservbyname('serpots','tcp')))

        s.send("%d %d %d %d\n" % l)
        s.close()
    except Exception,e:
        print "Exception: %s" % e


