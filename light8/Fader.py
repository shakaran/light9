from Tix import *
from time import time # time is on my side
from util import subsetdict

# statuses are:
# stopped - no cue is loaded
# running - cue is running, not complete
# halted - cue stops wherever it was, can't continue
# finished - cue is finished, next is loaded

stdfont = ('Arial', 10)

class Fader(Frame):
    'User interface for cue fader'
    def __init__(self, master, cues, scalelevels):
        self.master = master
        self.cues = cues
        self.scalelevels = scalelevels
        self.init_layout()
    def init_layout(self):
        Frame.__init__(self, self.master)

        # info variables
        self.cuename = StringVar()
        self.cuelength = DoubleVar()
        self.cuetarget = StringVar()

        # info about a running cue
        self.cuestatus = StringVar() # text description
        self.cuestatus.set("stopped")
        
        self.cuepercent = DoubleVar() # percent complete
        self.cuepercent.set(0)
        self.cuetime = StringVar() # time left
        self.cuetime.set('0 / 0')

        buttonframe = Frame(self)

        self.listbox = ScrolledListBox(buttonframe)
        self.listbox.listbox.configure({'exportselection' : 0})
        for c in self.cues:
            self.listbox.listbox.insert(END, c.name)
        self.listbox.pack(side=TOP)
        Button(buttonframe, text="Go", command=self.go).pack(side=LEFT)
        Button(buttonframe, text="Halt").pack(side=LEFT)
        Button(buttonframe, text="Clear").pack(side=LEFT)

        infoframe = Frame(self)
        Label(infoframe, textvariable=self.cuename, 
            font=('Arial', 12), bg='lightBlue').grid(columnspan=2, sticky=NE+SW)

        Label(infoframe, text="Length", font=stdfont, 
            bg='lightPink').grid(row=1, sticky=NE+SW)
        Label(infoframe, textvariable=self.cuelength, 
            font=stdfont).grid(row=1, column=1, sticky=NE+SW)

        Label(infoframe, text="Target", font=stdfont,
            bg='lightPink', wraplength=50).grid(row=2, sticky=NE+SW)
        Label(infoframe, textvariable=self.cuetarget, 
            font=stdfont).grid(row=2, column=1, sticky=NE+SW)

        Label(infoframe, text="Status", font=stdfont,
            bg='lightPink').grid(row=3, sticky=NE+SW)
        Label(infoframe, textvariable=self.cuestatus, 
            font=stdfont).grid(row=3, column=1, sticky=NE+SW)

        Label(infoframe, text="Time", font=stdfont,
            bg='lightPink').grid(row=4, sticky=NE+SW)
        Label(infoframe, textvariable=self.cuetime, 
            font=stdfont).grid(row=4, column=1, sticky=NE+SW)

        Label(infoframe, text="Percent Complete", font=stdfont,
            bg='lightPink').grid(row=5, sticky=NE+SW)
        Label(infoframe, textvariable=self.cuepercent, 
            font=stdfont).grid(row=5, column=1, sticky=NE+SW)

        infoframe.pack(side=RIGHT, fill=BOTH, expand=1)
        buttonframe.pack(side=BOTTOM)

        self.listbox.listbox.select_set(0)
        self.update_selection()
    def update_selection(self):
        selection = int(self.listbox.listbox.curselection()[0]) # blech
        self.current = self.cues[selection]
        self.cuename.set(self.current.name)
        self.cuelength.set(self.current.dur)
        self.cuetarget.set(str(self.current.get_end_levels()))
    def go(self):
        print 'Fade to', self.current.name
        self.cuestatus.set("running")
        self.time_start = time()
        startlevels = dict([(k, v.get()) for k, v in self.scalelevels.items()])
        self.current.start(startlevels, self.time_start)
        self.running_loop()
    def running_loop(self):
        curtime = time()
        if (curtime - self.time_start) > self.current.dur:
            return
        newlevels = self.current.get_levels(time())
        print newlevels
        self.after(30, self.running_loop)
