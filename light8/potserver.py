#!/usr/bin/python

import socket,time

from io import *

pots = SerialPots()
pots.golive()

laste=""
while 1:
    
    l=pots.getlevels()
        
    try:
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(1)
        ret=s.connect_ex(("dash", socket.getservbyname('rlslider','tcp')))
#        print ret        
        s.send("%d %d %d %d\n" % l)
        s.close()
    except Exception,e:
        print str(e)
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if ret==111:
            print time.ctime(),"waiting for server"
            time.sleep(3)
        else:
            print time.ctime(),"connected"



