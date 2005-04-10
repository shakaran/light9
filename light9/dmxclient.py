""" module for clients to use for easy talking to the dmx
server. sending levels is now a simple call to
dmxclient.outputlevels(..)

client id is formed from sys.argv[0] and the PID.  """

import xmlrpclib,os,sys,socket,time
from twisted.web.xmlrpc import Proxy
_dmx=None

_id="%s-%s" % (sys.argv[0].replace('.py','').replace('./',''),os.getpid())

def outputlevels(levellist,twisted=0,clientid=_id):
    """present a list of dmx channel levels, each scaled from
    0..1. list can be any length- it will apply to the first len() dmx
    channels.

    if the server is not found, outputlevels will block for a
    second."""

    global _dmx,_id

    if _dmx is None:
        host = os.getenv('DMXHOST', 'localhost')
        url = "http://%s:8030" % host
        if not twisted:
            _dmx=xmlrpclib.Server(url)
        else:
            _dmx = Proxy(url)

    if not twisted:
        try:
            _dmx.outputlevels(clientid,levellist)
        except socket.error,e:
            print "dmx server error %s, waiting"%e
            time.sleep(1)
        except xmlrpclib.Fault,e:
            print "outputlevels had xml fault: %s" % e
            time.sleep(1)
    else:
        def err(error):
            print "dmx server error",error
            time.sleep(1)
        d = _dmx.callRemote('outputlevels',clientid,levellist)
        d.addErrback(err)

    
dummy = os.getenv('DMXDUMMY')
if dummy:
    print "dmxclient: DMX is in dummy mode."
    def bogus(*args):
        pass
    outputlevels = bogus
