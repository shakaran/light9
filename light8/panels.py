"""some of the panels"""

from Tkinter import *
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
    def __init__(self):
        print "Light 8: Everything's under control"
        t=toplevelat(267,717,w=599,h=19)
        self.frame = Frame(t)
        self.entry=Entry(self.frame)
        self.entry.pack(expand=1, fill='x')
        self.entry.bind('<Return>', lambda evt: self.execute(evt, 
            self.entry.get()))
        self.frame.pack(fill=BOTH, expand=1)
    
    def execute(evt, str):
        if str[0] == '*': # make a new sub
            make_sub(str)
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
    def __init__(self, scenesparent, effectsparent, scalelevels, Subs, xfader,
        changelevel):
        
        sublist = Subs.subs.items()
        sublist.sort()

        for name, sub in sublist:
            # choose one of the sub panels to add to
            if sub.is_effect:
                parent=effectsparent
                side1='bottom'
                orient='vert'
                end1=0
                end2=1
            else:
                parent=scenesparent
                side1='right'
                orient='horiz'
                end1=1
                end2=0

            # make frame that surrounds the whole submaster
            f=Frame(parent, bd=1, relief='raised')
            f.pack(fill='both',exp=1,side=('top','left')[sub.is_effect])

            # make DoubleVar (there might be one left around from before a refresh)
            if name not in scalelevels:
                scalelevels[name]=DoubleVar()

            sub.set_slider_var(scalelevels[name])

            scaleopts = {}
            if sub.color:
                scaleopts['troughcolor'] = sub.color

            s = FlyingFader(f, label=str(name), variable=scalelevels[name],
                            showvalue=0, length=300-17,
                            width=18, sliderlength=18,
                            to=end1,res=.001,from_=end2,bd=0, font=stdfont,
                            orient=orient,
                            labelwidth=12, # this should be equal to the longest label name
                            **scaleopts)

            for axis in ('y','x'):
                cvar=IntVar()
                cb=Togglebutton(f,text=axis.upper(),variable=cvar,font=stdfont, padx=0, 
                               pady=0, bd=1)
                cb.pack(side=side1,fill='both', padx=0, pady=0)
                s.bind('<Key-%s>'%axis, lambda ev,cb=cb: cb.invoke)
                xfader.registerbutton(name,axis,cvar)

            s.pack(side='left', fill=BOTH)

            # effects frame?
            sframe = Frame(f,bd=2,relief='groove')
            sub.draw_tk(sframe)
            sframe.pack(side='left',fill='y')
