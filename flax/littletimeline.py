#!/usr/bin/python

""" a test that listens to ascoltami player and outputs a light to
dmxserver """

from __future__ import division
import xmlrpclib,time,socket,sys
sys.path.append("../light8")
import dmxclient

player=xmlrpclib.Server("http://localhost:8040")
print "found player"

t1=time.time()
while 1:
    try:
        playtime=player.gettime()
    except socket.error,e:
        print "server error %r, waiting"%e
        time.sleep(2)

    lev=0
    for low,high,func in ((0,20,0),
                          (20,30,(playtime-20)/10),
                          (30,170,1),
                          (170,189,1-(playtime-170)/19),
                          ):
        if low<=playtime<high:
            lev=func

    print "Send",lev
    dmxclient.outputlevels([lev])
  
    time.sleep(.01)
