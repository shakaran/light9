from Tix import *
from time import time # time is on my side
from util import subsetdict
from FlyingFader import FlyingFader

# statuses are:
# stopped - no cue is loaded or cue is stopped
# running - cue is running, not complete
# finished - cue is finished, next is loaded

stdfont = ('Arial', 10)

class Fader(Frame):
    'User interface for cue fader'
    def __init__(self, master, cues, scalelevels):
        self.master = master
        self.cues = cues
        self.scalelevels = scalelevels
        self.time_start = 0
        self.init_layout()
        self.stop()
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
        self.cuepercent.trace('w', self.update_percent)
        self.cuetimeelapse = StringVar() # time elapsed
        self.cuetimeelapse.set('0s')
        self.cuetimeleft = StringVar() # time left
        self.cuetimeleft.set('0s')

        buttonframe = Frame(self)

        self.listbox = ScrolledListBox(buttonframe, 
            command=self.update_selection)
        self.listbox.listbox.configure({'exportselection' : 0, 
            'selectmode' : EXTENDED})
        for c in self.cues:
            self.listbox.listbox.insert(END, c.name)
        self.listbox.pack(side=TOP)
        self.listbox.listbox.bind("<<ListboxSelect>>", self.update_selection, 
            add=1)
        Button(buttonframe, text="Go", command=self.go, font=stdfont,
            bg='green').pack(side=LEFT)
        Button(buttonframe, text="Stop", command=self.stop, font=stdfont,
            bg='red').pack(side=LEFT)
        Button(buttonframe, text="Prev", command=self.prev, 
            font=stdfont).pack(side=LEFT)
        Button(buttonframe, text="Next", command=self.next, 
            font=stdfont).pack(side=LEFT)

        infoframe = Frame(self)
        Label(infoframe, textvariable=self.cuename, 
            font=('Arial', 12), bg='lightBlue').grid(columnspan=4, sticky=NE+SW)

        Label(infoframe, text="Length", font=stdfont, 
            bg='lightPink').grid(row=1, sticky=NE+SW)
        Label(infoframe, textvariable=self.cuelength, 
            font=stdfont).grid(row=1, column=1, columnspan=3, sticky=NE+SW)

        Label(infoframe, text="Target", font=stdfont,
            bg='lightPink', wraplength=50).grid(row=2, sticky=NE+SW)
        Label(infoframe, textvariable=self.cuetarget, 
            font=stdfont).grid(row=2, column=1, columnspan=3, sticky=NE+SW)

        Label(infoframe, text="Status", font=stdfont,
            bg='lightPink').grid(row=3, sticky=NE+SW)
        Label(infoframe, textvariable=self.cuestatus, 
            font=stdfont).grid(row=3, column=1, columnspan=3, sticky=NE+SW)

        Label(infoframe, text="Time Elapsed", font=stdfont,
            bg='lightPink').grid(row=4, sticky=NE+SW)
        Label(infoframe, textvariable=self.cuetimeelapse, 
            font=stdfont).grid(row=4, column=1, sticky=NE+SW)

        Label(infoframe, text="Time Remain", font=stdfont,
            bg='lightPink').grid(row=4, column=2, sticky=NE+SW)
        Label(infoframe, textvariable=self.cuetimeleft, 
            font=stdfont).grid(row=4, column=3, sticky=NE+SW)

        Label(infoframe, text="Percent Complete", font=stdfont,
            bg='lightPink').grid(row=5, column=0, sticky=NE+SW)
        self.percentlabel = Label(infoframe, 
            font=stdfont)
        self.percentlabel.grid(row=5, column=1, columnspan=3, sticky=NE+SW)

        s = Scale(infoframe, variable=self.cuepercent,
                        showvalue=0, length=220,
                        width=18, sliderlength=30,
                        to=100,res=.1,from_=0,bd=1, font=stdfont,
                        orient='horiz')
        s.grid(row=6, columnspan=4, sticky='ew')

        infoframe.pack(side=RIGHT, fill=BOTH, expand=1)
        buttonframe.pack(side=BOTTOM)

        self.listbox.listbox.select_set(0)
        self.update_selection()
    def update_percent(self, *args):
        if self.cuestatus.get() != 'running':
            self.cuestatus.set("running")
            self.time_start = time()
            startlevels = dict([(k, v.get()) 
                for k, v in self.scalelevels.items()])
            self.current.start(startlevels, self.time_start)

        percent = self.cuepercent.get()
        self.percentlabel.config(text='%.1f%%' % percent)
        percent /= 100

        elapsed = percent * self.current.dur
        self.cuetimeelapse.set('%.1fs' % elapsed)
        self.cuetimeleft.set('%.1fs' % (self.current.dur - elapsed))
        newlevels = self.current.get_levels(self.time_start + elapsed)
        for ch, lev in newlevels.items():
            try:
                self.scalelevels[ch].set(lev / 100.0)
            except KeyError:
                pass

    def update_selection(self, *args):
        selection = int(self.listbox.listbox.curselection()[0]) # blech
        self.current = self.cues[selection]
        self.cuename.set(self.current.name)
        self.cuelength.set(self.current.dur)
        target = ', '.join(['%s -> %.1f' % (n, lev) 
            for n, lev in self.current.get_end_levels().items()])
        self.cuetarget.set(target)
        self.cuetimeelapse.set('0s')
        self.cuetimeleft.set('%.1fs' % self.current.dur)
        self.cuepercent.set(0)
    def go(self):
        self.update_selection()
        self.cuestatus.set("running")
        self.time_start = time()
        startlevels = dict([(k, v.get()) for k, v in self.scalelevels.items()])
        self.current.start(startlevels, self.time_start)
        self.running_loop()
    def stop(self):
        self.cuestatus.set('stopped')
    def prev(self):
        self.cuestatus.set('stopped')
        selection = int(self.listbox.listbox.curselection()[0]) # blech
        if selection != 0:
            self.listbox.listbox.select_clear(selection)
            self.listbox.listbox.select_set(selection - 1)
            self.update_selection()
    def next(self):
        self.cuestatus.set('stopped')
        selection = int(self.listbox.listbox.curselection()[0]) # blech
        if selection != self.listbox.listbox.size() - 1:
            self.listbox.listbox.select_clear(selection)
            self.listbox.listbox.select_set(selection + 1)
            self.update_selection()
    def running_loop(self):
        if self.cuestatus.get() == 'stopped':
            return
        curtime = time()
        elapsed = (curtime - self.time_start)
        if elapsed > self.current.dur:
            self.cuestatus.set('finished')
            self.cuepercent.set(100)

            # advance cues if okay
            self.next()
            return

        self.cuepercent.set(100 * elapsed / self.current.dur)
        self.after(30, self.running_loop)
