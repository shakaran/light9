"""some of the panels"""
from __future__ import nested_scopes

from Tix import *
from uihelpers import *
import Patch
from FlyingFader import FlyingFader
import Pmw

stdfont = ('Arial', 8)
monofont = ('Courier', 8)

class Controlpanel(Frame):
    def __init__(self, parent, xfader, refresh_cb, quit_cb):
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

class Console:
    def __init__(self,lightboard):
        print "Light 8: Everything's under control"
        t=toplevelat('console', lightboard.windowpos)
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

class Subpanels:
    def __init__(self, scenesparent, effectsparent, lightboard,
                 scalelevels, Subs, xfader,
                 changelevel, subediting, longestname):
        
        sublist = Subs.subs.items()
        sublist.sort()

        for p in scenesparent,effectsparent:
            sw = ScrolledWindow(p)
            for but,units in ( (4,-4),(5,4) ):
                sw.window.bind("<ButtonPress-%s>"%but,lambda ev,s=sw.vsb,u=units: s.tk.call('tkScrollByUnits',s,'hv',u))

            sw.pack(expand=1,fill=BOTH)
            if p==scenesparent:
                scenesparent = sw.window
            else:
                effectsparent = sw.window

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

                    
