"""some more of the panels"""
from Tix import *

class SliderMapping:
    def __init__(self, default='disconnected', attached=0, extinputlevel=0, 
                 sublevel=0):
        self.subname = StringVar() # name of submaster we're connected to
        self.subname.set(default)
        self.sublevel = DoubleVar() # scalelevel variable of that submaster
        self.sublevel.set(sublevel)
        self.attached = BooleanVar() # currently attached
        self.attached.set(attached)
        self.extlevel = DoubleVar() # external slider's input
        self.extlevel.set(extinputlevel)
        self.extlabel = None
        self.sublabel = None
    def attach(self):
        self.attached.set(1)
        self.color_text()
    def detach(self):
        self.attached.set(0)
        self.color_text()
    def isattached(self):
        return self.attached.get()
    def isdisconnected(self):
        return self.subname.get() == 'disconnected'
    def check_attached(self):
        'If external level is higher than the sublevel, it attaches'
        if self.isdisconnected(): 
            self.detach()
            return

        if self.extlevel.get() > self.sublevel.get():
            self.attached.set(1)
        self.color_text()
    def changed_extinput(self, newlevel):
        'When a new external level is received, this incorporates it'
        self.extlevel.set(newlevel)
        self.check_attached()
        self.color_text()
    def set_subname(self, newname):
        self.subname.set(newname)
        self.detach()
        self.color_text()
    def color_text(self):
        if self.extlabel:
            if self.isdisconnected():
                self.extlabel.configure(fg='honeyDew4')
            elif self.isattached():
                self.extlabel.configure(fg='honeyDew2')
            else:
                self.extlabel.configure(fg='red')
    def disconnect(self):
        self.set_subname('disconnected') # a bit hack-like
        self.sublabel.configure(text="N/A")
    def set_sublevel_var(self, newvar):
        'newvar is one of the variables in scalelevels'
        self.sublevel = newvar
        if self.sublabel:
            self.sublabel.configure(textvariable=newvar)
        self.check_attached()
    def get_mapping(self):
        'Get name of submaster currently mapped'
        return self.subname.get()
    def get_level_pair(self):
        'Returns suitable output for ExtSliderMapper.get_levels()'
        return (self.subname.get(), self.extlevel.get())
    def draw_interface(self, master, subnames):
        'Draw interface into master, given a list of submaster names'
        frame = Frame(master)
        c = ComboBox(frame, variable=self.subname)
        c.slistbox.listbox.insert(END, "disconnected")
        for s in subnames:
            c.slistbox.listbox.insert(END, s)
        c.entry.configure(width=12)
        statframe = Frame(frame)
        Checkbutton(statframe, variable=self.attached, 
            text="Attached").grid(columnspan=2, sticky=W)
        Label(statframe, text="Input", fg='red').grid(row=1, sticky=W)
        self.extlabel = Label(statframe, textvariable=self.extlevel, width=5)
        self.extlabel.grid(row=1, column=1)
        Label(statframe, text="Real").grid(row=2, sticky=W)
        self.sublabel = Label(statframe, text="N/A", width=5)
        self.sublabel.grid(row=2, column=1)
        statframe.pack(side=BOTTOM, expand=1, fill=X)
        c.pack()
        frame.pack(side=LEFT, expand=1, fill=BOTH)

class ExtSliderMapper(Frame):
    def __init__(self, parent, sliderlevels, sliderinput, filename='slidermapping',
                 numsliders=4):
        'Slider levels is scalelevels, sliderinput is an ExternalInput object'
        Frame.__init__(self, parent)
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
            except KeyError:
                pass
                
    def get_levels(self):
        'Called by changelevels, returns a dict of new values for submasters'
        if not self.sliderinput: return {}

        self.load_scalelevels() # freshen our input from the physical sliders

        rawlevels = self.sliderinput.get_levels()
        for rawlev, slidermap in zip(rawlevels, self.current_mappings):
            slidermap.changed_extinput(rawlev)

        outputlevels = {}
        return dict([m.get_level_pair()
            for m in self.current_mappings
            if m.isattached()])
    def draw_interface(self):
        self.reallevellabels = []
        subchoiceframe = Frame(self)
        for m in self.current_mappings:
            m.draw_interface(subchoiceframe, self.subnames)
        subchoiceframe.pack()
        
        presetframe = Frame(self)
        Label(presetframe, text="Preset:").pack(side=LEFT)
        self.presetcombo = ComboBox(presetframe, variable=self.current_preset, 
                                    editable=1, command=self.apply_preset)
        self.draw_presets()
        self.presetcombo.pack(side=LEFT)
        Button(presetframe, text="Add", padx=0, pady=0, 
                command=self.add_preset).pack(side=LEFT)
        Button(presetframe, text="Delete", padx=0, pady=0, 
                command=self.delete_preset).pack(side=LEFT)
        Button(presetframe, text="Disconnect", padx=0, pady=0, 
                command=self.disconnect_all).pack(side=LEFT)
        presetframe.pack(side=BOTTOM)
    def apply_preset(self, preset):
        if not preset: return
        preset_mapping = self.presets.get(preset)
        if not preset_mapping: return
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
