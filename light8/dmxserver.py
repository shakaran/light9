#!/usr/bin/python
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

todo:
  save dmx on quit and restore on restart
  if parport fails, run in dummy mode (and make an option for that too)
"""

from __future__ import division
from twisted.internet import reactor
from twisted.web import xmlrpc, server
import sys,time
from optik import OptionParser
from io import ParportDMX
from updatefreq import Updatefreq

class XMLRPCServe(xmlrpc.XMLRPC):
    def __init__(self,options):

        xmlrpc.XMLRPC.__init__(self)
        
        self.clientlevels={} # clientID : list of levels
        self.lastseen={} # clientID : time last seen
        self.clientfreq={} # clientID : updatefreq
        
        self.combinedlevels=[] # list of levels, after max'ing the clients
        self.clientschanged=1 # have clients sent anything since the last send?
        self.options=options

        print "starting parport connection"
        self.parportdmx=ParportDMX()
        self.parportdmx.golive()

        # start the loop
        self.updatefreq=Updatefreq()
        self.num_unshown_updates=None
        self.lastshownlevels=None
        self.sendlevels()
        

    def purgeclients(self):
        
        """forget about any clients who haven't sent levels in a while
        (5 seconds)"""
        now=time.time()
        for cid,lastseen in self.lastseen.items():
            if lastseen<now-5:
                print "forgetting client %s (no activity for 5sec)" % cid
                del self.clientlevels[cid]
                del self.lastseen[cid]
                del self.clientfreq[cid]
        
    def sendlevels(self):
        reactor.callLater(1/20,self.sendlevels)
        if self.clientschanged:
            # recalc levels

            self.purgeclients()
            self.calclevels()
         
            if (self.num_unshown_updates is None or # first time
                self.options.fast_updates or # show always
                (self.combinedlevels!=self.lastshownlevels and # changed
                 self.num_unshown_updates>10)): # not too frequent
                self.num_unshown_updates=0
                self.printlevels()
                self.lastshownlevels=self.combinedlevels[:]
            else:
                self.num_unshown_updates+=1

        if (self.num_unshown_updates-1)%50==0:
            self.printstats()
            
        self.sendlevels_dmx()

    def calclevels(self):
        """combine all the known client levels into self.combinedlevels"""
        self.combinedlevels=[]
        for chan in range(0,self.parportdmx.dimmers):
            x=0
            for clientlist in self.clientlevels.values():
                if len(clientlist)>chan:
                    # clamp client levels to 0..1
                    cl=max(0,min(1,clientlist[chan]))
                    x=max(x,cl)
            self.combinedlevels.append(x)


    def printlevels(self):
        """write all the levels to stdout"""
        print "Levels:","".join(["% 2d "%(x*100) for
                                 x in self.combinedlevels])
    
    def printstats(self):
        """print the clock, freq, etc, with a \r at the end"""

        sys.stdout.write("dmxserver up at %s, [server %s] "%
                         (time.strftime("%H:%M:%S"),
                          str(self.updatefreq),
                          ))
        for cid,freq in self.clientfreq.items():
            sys.stdout.write("[%s %s] " % (cid,str(freq)))
        sys.stdout.write("\r")
        sys.stdout.flush()

    
    def sendlevels_dmx(self):
        """output self.combinedlevels to dmx, and keep the updates/sec stats"""
        # they'll get divided by 100
        if self.parportdmx:
            self.parportdmx.sendlevels([l*100 for l in self.combinedlevels])
        self.updatefreq.update()
    
    def xmlrpc_echo(self,x):
        return x
    
    def xmlrpc_outputlevels(self,cid,levellist):
        """send a unique id for your client (name+pid maybe), then
        the variable-length dmx levellist (scaled 0..1)"""
        self.clientlevels[cid]=levellist
        self.clientschanged=1
        if cid not in self.lastseen:
            print "hello new client %s" % cid
            self.clientfreq[cid]=Updatefreq()
        self.lastseen[cid]=time.time()
        self.clientfreq[cid].update()
        return "ok"

parser=OptionParser()
parser.add_option("-f","--fast-updates",action='store_true',
                  help=('display all dmx output to stdout instead '
                        'of the usual reduced output'))
(options,songfiles)=parser.parse_args()

print "starting xmlrpc server on port 8030"
reactor.listenTCP(8030,server.Site(XMLRPCServe(options)))
reactor.run()

