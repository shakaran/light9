"""some more of the panels"""
from Tix import *

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

        self.current_mapping_name = StringVar()
        self.current_mapping = []
        self.attached = []
        self.levels_read = []
        for i in range(self.numsliders):
            cm_var = StringVar()
            cm_var.set('disconnected')
            self.current_mapping.append(cm_var)
            self.attached.append(BooleanVar())
            self.levels_read.append(DoubleVar())

        self.reallevellabels = []
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
        for m, rll, levread, att in zip(self.current_mapping, self.reallevellabels, 
                                        self.levels_read, self.attached):
            try:
                v = self.sliderlevels[m.get()] # actual scalelevel variable
                rll.configure(textvariable=v)
                if levread.get() >= v.get():   # attach if physical goes above virtual
                    att.set(1)
            except KeyError:
                pass
                
    def get_levels(self):
        'To be called by changelevels, I think'
        if not self.current_mapping_name: return {}
        if not self.sliderinput: return {}

        self.load_scalelevels()

        rawlevels = self.sliderinput.get_levels()
        for rawlev, levlabvar in zip(rawlevels, self.levels_read):
            levlabvar.set(rawlev)
        outputlevels = {}
        return dict([(name.get(), lev) 
            for name, lev, att in zip(self.current_mapping, 
                                      rawlevels, 
                                      self.attached) 
            if att.get()])

    def draw_interface(self):
        self.reallevellabels = []
        subchoiceframe = Frame(self)
        for i, mapping, isattached, lev in zip(range(self.numsliders), 
                                               self.current_mapping, 
                                               self.attached,
                                               self.levels_read):
            f = Frame(subchoiceframe)
            # Label(f, text="Slider %d" % (i+1)).pack(side=LEFT)
            c = ComboBox(f, variable=mapping)
            c.slistbox.listbox.insert(END, "disconnected")
            for s in self.subnames:
                c.slistbox.listbox.insert(END, s)
            c.entry.configure(width=12)
            statframe = Frame(f)
            Checkbutton(statframe, variable=isattached, 
                text="Attached").grid(columnspan=2, sticky=W)
            Label(statframe, text="Input", fg='red').grid(row=1, sticky=W)
            Label(statframe, textvariable=lev, fg='red', width=5).grid(row=1, column=1)
            Label(statframe, text="Real").grid(row=2, sticky=W)
            l = Label(statframe, text="N/A", width=5)
            l.grid(row=2, column=1)
            self.reallevellabels.append(l)
            statframe.pack(side=BOTTOM, expand=1, fill=X)
            c.pack()
            f.pack(side=LEFT, expand=1, fill=BOTH)
        subchoiceframe.pack()
        
        presetframe = Frame(self)
        Label(presetframe, text="Preset:").pack(side=LEFT)
        self.presetcombo = ComboBox(presetframe, variable=self.current_mapping_name, 
                                    editable=1, command=self.apply_preset)
        self.draw_presets()
        self.presetcombo.pack(side=LEFT)
        Button(presetframe, text="Add", padx=0, pady=0, 
                command=self.add_preset).pack(side=LEFT)
        Button(presetframe, text="Delete", padx=0, pady=0, 
                command=self.delete_preset).pack(side=LEFT)
        presetframe.pack(side=BOTTOM)
    def apply_preset(self, preset):
        if not preset: return
        mapping = self.presets.get(preset)
        if not mapping: return
        for name, var, att in zip(mapping, self.current_mapping, self.attached):
            var.set(name)
            att.set(0) # detach all sliders
    def delete_preset(self, *args):
        del self.presets[self.current_mapping_name.get()]
        self.presetcombo.slistbox.listbox.delete(0, END)
        self.draw_presets()
        self.save_presets()
    def add_preset(self, *args):
        self.presets[self.current_mapping_name.get()] = [m.get() 
                for m in self.current_mapping]
        self.presetcombo.slistbox.listbox.delete(0, END)
        self.draw_presets()
        self.save_presets()
    def draw_presets(self):
        preset_names = self.presets.keys()
        preset_names.sort()
        for p in preset_names:
            self.presetcombo.slistbox.listbox.insert(END, p)
