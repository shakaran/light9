""" The External Slider Mapping widget determines which pots map to which
submasters.  It tells you the status of each mapping and saves and loads
presets.  The show is relying on this module!  Do not lose it!

FUQ (frequently unasked question(s))

1. What's with all the *args?

It lets functions take any number of arguments and throw them away.
Callbacks do this, and we typically don't care about what they have to say. """

from Tix import *
from uihelpers import FancyDoubleVar, get_selection

stdfont = ('Arial', 8)

class SliderMapping:
    def __init__(self, default='disconnected', synced=0, extinputlevel=0, 
                 sublevel=0):
        self.subname = StringVar() # name of submaster we're connected to
        self.subname.set(default)
        self.sublevel = DoubleVar() # scalelevel variable of that submaster
        # self.sublevel = FancyDoubleVar() # scalelevel variable of that submaster
        self.sublevel.set(sublevel)
        self.synced = BooleanVar() # currently synced
        self.synced.set(synced)
        self.extlevel = DoubleVar() # external slider's input
        self.extlevel.set(extinputlevel)
        self.widgets = [] # list of widgets drawn
        self.sublabel = None # the label which represents a sub level.  
                             # we hold on to it so we can change its 
                             # textvariable
        self.statuslabel = None # tells us sync status
        self.lastbgcolor = None # last background color drawn to avoid 
                                # unnecessary redraws
        self.subnames = [] # we need to keep track of this for idiotic reasons
    def sync(self, *args):
        self.synced.set(1)
        self.color_bg()
    def unsync(self, *args):
        self.synced.set(0)
        self.color_bg()
    def issynced(self):
        return self.synced.get()
    def disconnect(self, *args):
        self.set_subname('disconnected') # a bit hack-like
        # self.sublevel.delete_named('sync')
        '''
        try:
            if self.sublevel.unsync_trace_cbname is not None:
                # self.sublevel.trace_vdelete('w', 
                    # self.sublevel.unsync_trace_cbname)
                self.sublevel._tk.call('trace', 'vdelete', self.sublevel._name, 
                    'w', self.sublevel.unsync_trace_cbname)
                self.sublevel.unsync_trace_cbname = None
        except AttributeError:
            pass
        '''
            
        self.sublabel.configure(text="N/A")
        self.color_bg()
    def isdisconnected(self):
        return self.subname.get() == 'disconnected' # a bit more hack-like
    def check_synced(self, *args):
        'If external level is near than the sublevel, it synces'
        if self.isdisconnected(): 
            self.unsync()
            return

        if abs(self.extlevel.get() - self.sublevel.get()) <= 0.02:
            self.sync()
    def changed_extinput(self, newlevel):
        'When a new external level is received, this incorporates it'
        self.extlevel.set(newlevel)
        self.check_synced()
        self.color_bg()
    def set_subname(self, newname):
        try:
            self.listbox.listbox.select_clear(0, END)
        except IndexError:
            pass
        try:
            newindex = self.subnames.index(newname)
            self.listbox.listbox.select_set(newindex)
            self.listbox.listbox.see(newindex)
        except ValueError:
            pass

        self.subname.set(newname)
        self.unsync()
        self.color_bg()
    def color_bg(self):
        if self.widgets:
            if self.isdisconnected():
                color = 'honeyDew4'
            # stupid hack
            # elif abs(self.extlevel.get() - self.sublevel.get()) <= 0.02:
            elif self.issynced():
                color = 'honeyDew2'
            else: # unsynced
                color = 'red'

            if self.statuslabel: # more stupid hackery
                if color == 'honeyDew2': # connected
                    self.statuslabel['text'] = 'Sync'
                elif self.extlevel.get() < self.sublevel.get():
                    self.statuslabel['text'] = 'No sync (go up)'
                else:
                    self.statuslabel['text'] = 'No sync (go down)'

            # print "color", color, "lastbgcolor", self.lastbgcolor
            if self.lastbgcolor == color: return
            for widget in self.widgets:
                widget.configure(bg=color)
            self.lastbgcolor = color
    def set_sublevel_var(self, newvar):
        'newvar is one of the variables in scalelevels'

        if newvar is not self.sublevel:
            # self.sublevel.delete_named('sync')
            self.sublevel = newvar
            self.sublabel.configure(textvariable=newvar)
            # self.sublevel.trace_named('sync', lambda *args: self.unsync(*args))
            '''
            try:
                if self.sublevel.unsync_trace_cbname is not None:
                    # remove an old trace
                    self.sublevel.trace_vdelete('w',
                        self.sublevel.unsync_trace_cbname)
            except AttributeError:
                pass # it didn't have one

            self.sublevel = newvar
            self.sublevel.unsync_trace_cbname = self.sublevel.trace('w', 
                self.unsync)
            '''

        # if self.sublabel:
            # self.sublabel.configure(textvariable=newvar)
        self.check_synced()
    def get_mapping(self):
        'Get name of submaster currently mapped'
        return self.subname.get()
    def get_level_pair(self):
        'Returns suitable output for ExtSliderMapper.get_levels()'
        return (self.subname.get(), self.extlevel.get())
    def listbox_cb(self, *args):
        self.subname.set(self.subnames[get_selection(self.listbox.listbox)-0])
    def draw_interface(self, master, subnames):
        'Draw interface into master, given a list of submaster names'
        self.subnames = subnames
        frame = Frame(master, bg='black')
        self.listbox = ScrolledListBox(frame, scrollbar='y', bg='black')
        self.listbox.listbox.bind("<<ListboxSelect>>", self.listbox_cb, add=1)
        self.listbox.listbox.configure(font=stdfont, exportselection=0, 
            selectmode=BROWSE, bg='black', fg='white')
        self.listbox.vsb.configure(troughcolor='black')
        # self.listbox.listbox.insert(END, "disconnected")
        for s in subnames:
            self.listbox.listbox.insert(END, s)
        statframe = Frame(frame, bg='black')

        self.statuslabel = Label(statframe, text="No sync", width=15, 
            font=stdfont)
        self.statuslabel.grid(columnspan=2, sticky=W)
        ilabel = Label(statframe, text="Input", fg='blue', font=stdfont)
        ilabel.grid(row=1, sticky=W)
        extlabel = Label(statframe, textvariable=self.extlevel, width=5, 
            font=stdfont)
        extlabel.grid(row=1, column=1)
        rlabel = Label(statframe, text="Real", font=stdfont)
        rlabel.grid(row=2, sticky=W)
        self.sublabel = Label(statframe, text="N/A", width=5, font=stdfont)
        self.sublabel.grid(row=2, column=1)
        disc_button = Button(statframe, text="Disconnect", 
            command=self.disconnect, padx=0, pady=0, font=stdfont)
        disc_button.grid(row=3, columnspan=2)
        statframe.pack(side=BOTTOM, expand=1, fill=BOTH)
        self.listbox.pack(expand=1, fill=BOTH)
        frame.pack(side=LEFT, expand=1, fill=BOTH)

        self.widgets = [frame, self.listbox, statframe, self.statuslabel, 
                        ilabel, extlabel, rlabel, self.sublabel, disc_button]

class ExtSliderMapper(Frame):
    def __init__(self, parent, sliderlevels, sliderinput, filename='slidermapping',
                 numsliders=4):
        'Slider levels is scalelevels, sliderinput is an ExternalInput object'
        Frame.__init__(self, parent, bg='black')
        self.parent = parent
        self.sliderlevels = sliderlevels
        self.sliderinput = sliderinput
        self.filename = filename
        self.numsliders = numsliders
        self.file = None

        # don't call setup, let them do that when scalelevels is created
    def setup(self):
        self.subnames = self.sliderlevels.keys()
        self.subnames.sort()
        self.presets = {}
        self.load_presets()

        self.current_preset = StringVar() # name of current preset
        self.current_mappings = []
        for i in range(self.numsliders):
            self.current_mappings.append(SliderMapping())

        self.draw_interface()
    def load_presets(self):
        self.presets = {}
        self.file = open(self.filename, 'r')
        lines = self.file.readlines()
        for l in lines:
            tokens = l[:-1].split('\t')
            name = tokens.pop(0)
            self.presets[name] = tokens
        self.file.close()
    def save_presets(self):
        self.file = open(self.filename, 'w')
        self.file.seek(0)
        preset_names = self.presets.keys()
        preset_names.sort()
        for p in preset_names:
            s = '\t'.join([p] + self.presets[p]) + '\n'
            self.file.write(s)
        self.file.close()
    def load_scalelevels(self):
        for slidermap in self.current_mappings:
            try:
                v = self.sliderlevels[slidermap.get_mapping()]
                slidermap.set_sublevel_var(v)
                # print "ESM: Yes submaster named", slidermap.get_mapping()
            except KeyError:
                name = slidermap.get_mapping()
                if name != 'disconnected':
                    print "ESM: No submaster named", name
                
    def get_levels(self):
        'Called by changelevels, returns a dict of new values for submasters'
        if not self.sliderinput: return {}

        self.load_scalelevels() # freshen our input from the submasters

        rawlevels = self.sliderinput.get_levels()
        for rawlev, slidermap in zip(rawlevels, self.current_mappings):
            slidermap.changed_extinput(rawlev)

        return dict([m.get_level_pair()
            for m in self.current_mappings
            if m.issynced()])
    def draw_interface(self):
        self.reallevellabels = []
        subchoiceframe = Frame(self, bg='black')
        for m in self.current_mappings:
            m.draw_interface(subchoiceframe, self.subnames)
        subchoiceframe.pack()
        
        presetframe = Frame(self, bg='black')
        Label(presetframe, text="Preset:", font=('Arial', 10), bg='black', 
            fg='white').pack(side=LEFT)
        self.presetcombo = ComboBox(presetframe, variable=self.current_preset, 
                                    editable=1, command=self.apply_preset,
                                    dropdown=1)
        self.presetcombo.slistbox.configure(bg='black')
        self.presetcombo.slistbox.listbox.configure(bg='black', fg='white')
        self.presetcombo.entry.configure(bg='black', fg='white')
        self.draw_presets()
        self.presetcombo.pack(side=LEFT)
        Button(presetframe, text="Add", padx=0, pady=0, bg='black', 
                fg='white', font=stdfont, 
                command=self.add_preset).pack(side=LEFT)
        Button(presetframe, text="Delete", padx=0, pady=0, bg='black', 
                fg='white', font=stdfont,
                command=self.delete_preset).pack(side=LEFT)
        Button(presetframe, text="Disconnect", padx=0, pady=0, bg='black', 
                fg='white', font=stdfont,
                command=self.disconnect_all).pack(side=LEFT)
        Button(presetframe, text="Reload", padx=0, pady=0, bg='black', 
                fg='white', font=stdfont,
                command=self.load_presets).pack(side=LEFT)
        presetframe.pack(side=BOTTOM)
    def apply_preset(self, preset):
        if not preset: return
        preset_mapping = self.presets.get(preset)
        if not preset_mapping: return
        self.disconnect_all()
        for subname, slidermap in zip(preset_mapping, self.current_mappings):
            slidermap.set_subname(subname)
    def delete_preset(self, *args):
        del self.presets[self.current_preset.get()]
        self.presetcombo.slistbox.listbox.delete(0, END)
        self.draw_presets()
        self.save_presets()
    def add_preset(self, *args):
        self.presets[self.current_preset.get()] = [m.get_mapping() 
                for m in self.current_mappings]
        self.presetcombo.slistbox.listbox.delete(0, END)
        self.draw_presets()
        self.save_presets()
    def draw_presets(self):
        preset_names = self.presets.keys()
        preset_names.sort()
        for p in preset_names:
            self.presetcombo.slistbox.listbox.insert(END, p)
    def disconnect_all(self):
        for m in self.current_mappings:
            m.disconnect()
