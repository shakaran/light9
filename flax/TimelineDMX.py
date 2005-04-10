import sys, time, socket
sys.path.append("../light8")
import Tix as tk

import Patch, Timeline, dmxclient, xmlrpclib
import TheShow

Patch.reload_data()

class ShowRunner(tk.Frame):
    def __init__(self, master, show):
        tk.Frame.__init__(self, master)
        self.master = master

        self.show = show
        self.find_player()
        self.build_timeline_list()
    def build_timeline_list(self):
        self.tl_list = tk.Frame(self)
        for tl in self.show.get_timelines():
            b=tk.Button(self.tl_list,text=tl,
                        anchor='w',pady=1)
            b.config(command=lambda tl=tl: self.set_timeline(tl))
            b.pack(side='top',fill='x')
        self.tl_list.pack()
    def set_timeline(self, tlname):
        print "TimelineDMX: set timeline to", tlname
        self.show.set_timeline(tlname)
    def find_player(self):
        self.player = xmlrpclib.Server("http://spot:8040")
    def send_levels(self):
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
                self.master.update()
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    s = ShowRunner(root, TheShow.show)
    s.show.set_timeline('strobe test')
    s.pack()
    s.mainloop()
