"""

this is the only process to talk to the dmx hardware. other clients
can connect to this server and present dmx output, and this server
will max ('pile-on') all the client requests.

this server has a level display which is the final set of values that
goes to the hardware.

clients shall connect to the xmlrpc server and send:

  their PID (or some other cookie)

  a length-n list of 0..1 levels which will represent the channel
    values for the n first dmx channels.

server is port 8030; xmlrpc method is called outputlevels(pid,levellist).

"""

from __future__ import division
from twisted.internet import reactor
from twisted.web import xmlrpc, server

import sys
sys.path.append("../light8")
from io import ParportDMX

class XMLRPCServe(xmlrpc.XMLRPC):
    def __init__(self):
        self.clientlevels={} # clientPID : list of levels
        self.combinedlevels=[] # list of levels, after max'ing the clients
        self.clientschanged=1 # have clients sent anything since the last send?

        print "starting parport connection"
        self.parportdmx=ParportDMX()
        self.parportdmx.golive()

        # start the loop
        self.numupdates=0
        self.sendlevels()

    def sendlevels(self):
        reactor.callLater(.02,self.sendlevels)
        if self.clientschanged:
            # recalc levels
            self.combinedlevels=[]
            for chan in range(0,self.parportdmx.dimmers):
                x=0
                for clientlist in self.clientlevels.values():
                    if len(clientlist)>chan:
                        x=max(x,clientlist[chan])
                self.combinedlevels.append(x)

        self.numupdates=self.numupdates+1
        if (self.numupdates%200)==0:
            print self.combinedlevels
            
        # now send combinedlevels (they'll get divided by 100)
        self.parportdmx.sendlevels([l*100 for l in self.combinedlevels]) 
        
    def xmlrpc_echo(self,x):
        return x
    
    def xmlrpc_outputlevels(self,pid,levellist):
        self.clientlevels[pid]=levellist
        self.clientschanged=1
        return "ok"

print "starting server on 8030"
reactor.listenTCP(8030,server.Site(XMLRPCServe()))
reactor.run()

