from parport import *
import socket, os

lastlevels = {}

def gethostlist(host):
    return lastlevels[host]

def parselist(levels):
    newlist = [0] * 68
    # levels has at least one pair
    ch, lev = None, None
    while len(levels) >= 2:
        ch, lev = levels.pop(0), levels.pop(0)

        # off by one errors -- i hate them sooo much
        newlist[int(ch) - 1] = int(lev)
    return newlist

def sethostlist(host, changes):
    if not changes: return
    global lastlevels
    if host not in lastlevels:
        lastlevels[host] = [0] * 68

    lastlevels[host] = parselist(changes)
    '''
    # changes has at least one pair
    ch, lev = None, None
    while len(changes) >= 2:
        ch, lev = changes.pop(0), changes.pop(0)

        # off by one errors -- i hate them sooo much
        lastlevels[host][ch - 1] = lev 
    '''


def sendlevels(levels):
    print "sendlevels: i'm a level hobo:", levels
    levels = levels + [0]
    # if levels[14] > 0: levels[14] = 100 # non-dim
    print "sendlevels: wait for it... length =", len(levels)
    outstart()
    for p in range(1, 68 + 2):
        outbyte(levels[p-1]*255 / 100)
    print "sendlevels: done"

class ParportDMX: # ethdmx client or standalone server
    def __init__(self, dummy=1, dimmers=68, machine_name='localhost', 
                 standalone=0):
        self.dimmers = dimmers
        self.dummy = dummy
        if not dummy:
            getparport()

        self.standalone = standalone
        self.machine_name = machine_name

    def sendupdates(self, levels):
        if (not self.dummy) and levels:
            print "update:", levels

            if self.standalone:
                print "standalone sendlevels", levels
                sendlevels(parselist(levels))
                return

            pid = os.getpid()
            s = ('%d ' % pid) + ' '.join([str(l) for l in levels]) + '\n'
            # print "sending", s
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.machine_name, 
                socket.getservbyname('ethdmx', 'tcp')))
            self.sock.send(s)

            # response = self.sock.recv(100)
            # print "response", response
            # if response != 'ACK\n':
                # raise "Didn't get ACK from DMX server"

if __name__ == '__main__':
    import SocketServer
    getparport()
            
    class DMXHandler(SocketServer.StreamRequestHandler):
        def handle(self):
            global lastlevels
            changed = self.rfile.readline(1000)
            # self.wfile.write("ACK\n")
            pairs = changed.split()
            pid = pairs[0]
            changes = pairs[1:]

            # print 'pairs', pairs
            sethostlist(pid, changes)

            self.preplevels()
        def preplevels(self):
            global lastlevels
            hosts = lastlevels.keys()
            maxlevels = [0] * 68
            for h in hosts:
                maxlevels = [max(hostlev, maxlev) 
                    for hostlev, maxlev in zip(maxlevels, gethostlist(h))]
            print "dmxhandler sending levels:", maxlevels
            sendlevels(maxlevels)

    print "Running DMX over Ethernet socket server.  Everything is under " + \
          "control."

    server = SocketServer.TCPServer(('', 
        socket.getservbyname('ethdmx', 'tcp')), DMXHandler)
    server.serve_forever()
