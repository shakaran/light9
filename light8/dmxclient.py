""" module for clients to use for easy talking to the dmx
server. sending levels is now a simple call to
dmxclient.outputlevels(..)

client id is formed from sys.argv[0] and the PID.  """

import xmlrpclib,os,sys,socket,time
_dmx=None

_id="%s-%s" % (sys.argv[0].replace('.py','').replace('./',''),os.getpid())

def outputlevels(levellist):
    """present a list of dmx channel levels, each scaled from
    0..1. list can be any length- it will apply to the first len() dmx
    channels.

    if the server is not found, outputlevels will block for a
    second."""

    global _dmx,_id

    if _dmx is None:
        _dmx=xmlrpclib.Server("http://localhost:8030")

    try:
        _dmx.outputlevels(_id,levellist)
    except socket.error,e:
        print "dmx server error %r, waiting"%e
        time.sleep(1)
    except xmlrpclib.Fault,e:
        print "outputlevels had xml fault: %s" % e
        time.sleep(1)
    
