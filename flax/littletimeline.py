#!/usr/bin/python

"""
a test that listens to ascoltami player and outputs a light to dmxserver
"""
import xmlrpclib,time,socket,os

player=xmlrpclib.Server("http://localhost:8040")
dmx=xmlrpclib.Server("http://localhost:8030")

print "found both servers"

t1=time.time()
while 1:
    try:
        playtime=player.gettime()
    except socket.error,e:
        print "server error %r, waiting"%e
        time.sleep(2)
    print time.time()-t1,playtime
    try:
        dmx.outputlevels("littletimeline-%s"%os.getpid(),[.01*(playtime)%100])
    except xmlrpclib.Fault,e:
        print "outputlevels: %s" % e
    
    time.sleep(.01)
