import Tkinter as tk
import xmlrpclib, socket, time

class MusicTime:
    def __init__(self, server, port):
        self.player = xmlrpclib.Server("http://%s:%d" % (server, port))
    def get_music_time(self):
        playtime = None
        while not playtime:
            try:
                playtime = self.player.gettime()
            except socket.error, e:
                print "Server error %s, waiting" % e
                time.sleep(2)
        return playtime

class MusicTimeTk(tk.Frame, MusicTime):
    def __init__(self, master, server, port):
        tk.Frame.__init__(self)
        MusicTime.__init__(self, server, port)
        self.timevar = tk.DoubleVar()
        self.timelabel = tk.Label(self, textvariable=self.timevar, bd=2,
            relief='raised', width=10, padx=2, pady=2, anchor='w')
        self.timelabel.pack(expand=1, fill='both')
        def print_time(evt, *args):
            self.update_time()
            print self.timevar.get(), evt.keysym
        self.timelabel.bind('<KeyPress>', print_time)
        self.timelabel.bind('<1>', print_time)
        self.timelabel.focus()
        self.update_time()
    def update_time(self):
        self.timevar.set(self.get_music_time())
        self.after(100, self.update_time)

if __name__ == "__main__":
    from optik import OptionParser
    parser = OptionParser()
    parser.add_option("-s", "--server", default='dash')
    parser.add_option("-p", "--port", default=8040, type='int')
    options, args = parser.parse_args()
    
    root = tk.Tk()
    root.title("Time")
    MusicTimeTk(root, options.server, options.port).pack(expand=1, fill='both')
    try:
        tk.mainloop()
    except KeyboardInterrupt:
        root.destroy()
