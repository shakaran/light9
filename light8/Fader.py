from Tix import *

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

        self.cuename = StringVar()
        self.cuelength = DoubleVar()
        self.cueend = StringVar()

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
            bg='lightPink').grid(row=2, sticky=NE+SW)
        Label(infoframe, textvariable=self.cueend, 
            font=stdfont).grid(row=2, column=1, sticky=NE+SW)
        infoframe.pack(side=RIGHT, fill=BOTH, expand=1)
        buttonframe.pack(side=BOTTOM)

        self.listbox.listbox.select_set(0)
        self.update_selection()
    def update_selection(self):
        print self.listbox.listbox.curselection()
        selection = int(self.listbox.listbox.curselection()[0]) # blech
        self.current = self.cues[selection]
        self.cuename.set(self.current.name)
        self.cuelength.set(self.current.dur)
        self.cueend.set(str(self.current.get_end_levels()))
    def go(self):
        print 'Fade to', self.current.name
