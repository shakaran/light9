import thread, SocketServer, socket


currentlevels = [0,0,0,0]


class NetSliderHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline(1000)
        currentlevels[:] = [float(x)/255 for x in list(data.split())]

def start_server(levelstorage=0):
    server = SocketServer.TCPServer(
        ('', socket.getservbyname('rlslider', 'tcp')), 
        NetSliderHandler)
    server.serve_forever()

class ExternalSliders:
    def __init__(self, level_storage=[]):
        self.level_storage = level_storage
        self.spawn_server()
    def test(self):
        'Store fake inputs to test operations'
        pass
    def spawn_server(self):
        pass
        # thread.start_new_thread(start_server, (self.update))
    def update(self, *args):
        self.level_storage[:] = args
    def get_levels(self):
        return currentlevels
#        import math, time
#        return [max(0, math.sin(time.time() + i)) for i in range(4)] # bogus
            
        # return self.level_storage
