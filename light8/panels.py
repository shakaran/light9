"""some of the panels"""
from __future__ import nested_scopes

from Tix import *
from uihelpers import *
import Patch
from FlyingFader import FlyingFader

stdfont = ('Arial', 8)
monofont = ('Courier', 8)

class Controlpanel(Frame):
    def __init__(self, parent, xfader, refresh_cb, quit_cb, jostle_cb):
        Frame.__init__(self,parent)
        controlpanel = self
        for txt,cmd in (
            ('Quit',       quit_cb),
            ('Refresh',    refresh_cb),
            ('Clear all', xfader.clearallbuttons),
            ('On -> X',     lambda: xfader.grab('x')),
            ('Clear X',     lambda: xfader.clearallbuttons('x')),
            ('On -> Y',     lambda: xfader.grab('y')),
            ('Clear Y',     lambda: xfader.clearallbuttons('y'))):
            Button(controlpanel, text=txt, command=cmd).pack(side='top', 
                fill='x')
        # jostle button
        Checkbutton(controlpanel, text="Jostle", 
            command=jostle_cb).pack(side=TOP, fill=X)

class Console:
    def __init__(self,lightboard):
        print "Light 8: Everything's under control"
        t=toplevelat('console')
        self.frame = Frame(t)
        self.entry=Entry(self.frame)
        self.entry.pack(expand=1, fill='x')
        self.entry.bind('<Return>',
                        lambda evt: self.execute(evt, self.entry.get()))
        self.frame.pack(fill=BOTH, expand=1)
        self.lightboard=lightboard
    
    def execute(self, evt, str):
        if str[0] == '*': # make a new sub from the current levels
            self.lightboard.save_sub(str,self.lightboard.stageassub())
        else:
            print '>>>', str
            print eval(str)
            self.frame.focus()

class Leveldisplay:
    def __init__(self, parent, channel_levels, num_channels=68):
        frames = (make_frame(parent), make_frame(parent))
        channel_levels[:]=[]
        self.number_labels = []
        for channel in range(1, num_channels+1):

            # frame for this channel
            f = Frame(frames[channel > (num_channels/2)])
            # channel number -- will turn yellow when being altered
            num_lab = Label(f, text=str(channel), width=3, bg='lightPink', 
                font=stdfont, padx=0, pady=0, bd=0, height=1)
            num_lab.pack(side='left')
            self.number_labels.append(num_lab)

            # text description of channel
            Label(f, text=Patch.get_channel_name(channel), width=8, 
                font=stdfont, anchor='w', padx=0, pady=0, bd=0, 
                height=1).pack(side='left')

            # current level of channel, shows intensity with color
            l = Label(f, width=3, bg='lightBlue', font=stdfont, anchor='e', 
                      padx=1, pady=0, bd=0, height=1)
            l.pack(side='left')
            colorlabel(l)
            channel_levels.append(l)
            f.pack(side='top')

        self.channel_levels = channel_levels
        # channel_levels is an output - changelevel will use it to access 
        # these labels

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

        # self.setup()
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
            self.current_mapping.append(StringVar())
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
        for m, rll in zip(self.current_mapping, self.reallevellabels):
            try:
                v = self.sliderlevels[m.get()]
                rll.configure(textvariable=v)
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
            f.pack(side=LEFT)
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

                

class Subpanels:
    def __init__(self, scenesparent, effectsparent, scenes, lightboard,
                 scalelevels, Subs, xfader,
                 changelevel, subediting, longestname):
        
        sublist = Subs.subs.items()
        sublist.sort()

        for p in scenesparent,effectsparent,scenes:
            sw = ScrolledWindow(p)
            for but,units in ( (4,-4),(5,4) ):
                sw.window.bind("<ButtonPress-%s>"%but,lambda ev,s=sw.vsb,u=units: s.tk.call('tkScrollByUnits',s,'hv',u))

            sw.pack(expand=1,fill=BOTH)
            if p==scenesparent:
                scenesparent = sw.window
            elif p==effectsparent:
                effectsparent = sw.window
            else:
                scenes=sw.window

        for name, sub in sublist:
            # choose one of the sub panels to add to
            if sub.is_effect:
                parent=effectsparent
                side1='bottom'
                side2='left'
                orient1='vert'
                end1=0
                end2=1
                width1=len(name)
            elif name.startswith("*") and name[1].isdigit():
                parent=scenes
                side1='right'
                side2='top'
                orient1='horiz'
                end1=1
                end2=0
                width1=longestname
            else:
                parent=scenesparent
                side1='right'
                side2='top'
                orient1='horiz'
                end1=1
                end2=0
                width1=longestname

            # make frame that surrounds the whole submaster
            f=Frame(parent, bd=1, relief='raised')
            f.pack(fill='both',exp=1,side=side2)
            

            # make DoubleVar (there might be one left around from
            # before a refresh)
            if name not in scalelevels:
                scalelevels[name]=DoubleVar()

            sub.set_slider_var(scalelevels[name])

            scaleopts = {'troughcolor' : 'grey70'}
            if sub.color:
                scaleopts['troughcolor'] = sub.color

            s = FlyingFader(f, label=str(name), variable=scalelevels[name],
                            showvalue=0, length=100,
                            width=14, sliderlength=14,
                            to=end1,res=.001,from_=end2,bd=1, font=stdfont,
                            orient=orient1,
                            labelwidth=width1,
                            **scaleopts)

            # tell subediting what widgets to highlight when it's
            # editing a sub
            for w in (s,s.label,s.vlabel, s.scale):
                subediting.register(subname=name,widget=w)

            if not sub.is_effect:
                self.subeditingbuttons(f,side1,sub,name,lightboard,subediting)

            self.axisbuttons(f,s,xfader,stdfont,side1,name)

            s.pack(side='left', fill=BOTH, expand=1)

            # effects frame?
            sframe = Frame(f,bd=2,relief='groove')
            sub.draw_tk(sframe)
            sframe.pack(side='left',fill='y')

    def subediting_edit(self,subediting,sub):
        subediting.setsub(sub)
        
    def subediting_save(self,name,sub,lightboard):
        lightboard.save_sub(name,sub.getlevels(),refresh=0)
        
    def subeditingbuttons(self,f,side1,sub,name,lightboard,subediting):
        for txt,cmd in (("Edit",lambda subediting=subediting,sub=sub: self.subediting_edit(subediting,sub)),
                        ("Save",lambda sub=sub,name=name,lightboard=lightboard: self.subediting_save(name,sub,lightboard)),
                        ("SaveStg",lambda l=lightboard,name=name: l.save_sub(name,l.stageassub(),refresh=1)),
                        ):
            eb = Button(f,text=txt,font=stdfont,padx=0,pady=0,
                        bd=1,command=cmd)
            eb.pack(side=side1,fill='both',padx=0,pady=0)
            
    def axisbuttons(self,f,s,xfader,stdfont,side1,name):
        for axis in ('y','x'):
            cvar=IntVar()
            eb_color = ('red', 'green')[axis == 'y']
            cb=Togglebutton(f,text=axis.upper(),variable=cvar,font=stdfont, 
                            padx=3, pady=0, bd=1, downcolor=eb_color)
            cb.pack(side=side1,fill='both', padx=0, pady=0)
            s.bind('<Key-%s>'%axis, lambda ev,cb=cb: cb.invoke)
            xfader.registerbutton(name,axis,cvar)

                    
if __name__ == '__main__':
    print "testing external sliders"
    root = Tk()
    fakesliderlevels = dict([('sub%d' % n, DoubleVar()) for n in range(12)])
    esm = ExtSliderMapper(root, fakesliderlevels, None)
    esm.pack()
    
    mainloop()
