import sys, time, socket
sys.path.append("../light8")

import Patch, Timeline, dmxclient, xmlrpclib
import TheShow

Patch.reload_data()

class ShowRunner:
    def __init__(self, show):
        self.show = show
        self.find_player()
    def find_player(self):
        self.player = xmlrpclib.Server("http://localhost:8040")
    def send_levels(self):
        """
        sub = self.show.get_levels() # gets levels of subs
        leveldict = sub.get_levels() # gets levels of sub contents
        print 'resolved levels', leveldict

        levels = [0] * 68
        for k, v in leveldict.items():
            levels[Patch.get_dmx_channel(k)] = v
        """
        levels = self.show.calc_active_submaster().get_dmx_list()
        
        dmxclient.outputlevels(levels)
    def sync_times(self):
        try:
            playtime = self.player.gettime()
            self.show.set_time(playtime)
        except socket.error, e:
            print "Server error %s, waiting"%e
            time.sleep(2)
    def mainloop(self):
        try:
            while 1:
                self.sync_times()
                self.send_levels()
                time.sleep(0.01)
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    s = ShowRunner(TheShow.show)
    s.show.set_timeline('strobe test')
    s.mainloop()
