"""some of the panels"""

from Tkinter import *
from uihelpers import *
import Patch
from FlyingFader import FlyingFader

stdfont = ('Arial', 8)
monofont = ('Courier', 8)



class Controlpanel(Frame):
    def __init__(self,parent,xfader,refresh_cb,quit_cb):
        Frame.__init__(self,parent)
        controlpanel=self
        for txt,cmd in (
            ('Quit',       quit_cb),
            ('Refresh',    refresh_cb),
            ('Clear all', xfader.clearallbuttons),
            ('On -> X',     lambda: xfader.grab('x')),
            ('Clear X',     lambda: xfader.clearallbuttons('x')),
            ('On -> Y',     lambda: xfader.grab('y')),
            ('Clear Y',     lambda: xfader.clearallbuttons('y'))):
            Button(controlpanel, text=txt, command=cmd).pack(side='top', fill='x')


class Console:
    def __init__(self):
        print "Light 8: Everything's under control"
        t=toplevelat(267,717,w=599,h=19)
        self.frame = Frame(t)
        self.entry=Entry(self.frame)
        self.entry.pack(expand=1, fill='x')
        self.entry.bind('<Return>', lambda evt: self.execute(evt, self.entry.get()))
        self.frame.pack(fill=BOTH, expand=1)
    
    def execute(evt, str):
        if str[0] == '*': # make a new sub
            make_sub(str)
        else:
            print '>>>', str
            print eval(str)
        self.frame.focus()

class Leveldisplay:
    def __init__(self,parent,_oldlevels,channel_levels):
        
        frames = (make_frame(parent), make_frame(parent))
        channel_levels[:]=[]
        for channel in range(1, 69):
            f=Frame(frames[channel > 34])
            Label(f,text=str(channel), width=3, bg='lightPink', 
                font=stdfont, padx=0, pady=0, bd=0, height=1).pack(side='left')
            Label(f,text=Patch.get_channel_name(channel), width=8, 
                font=stdfont, anchor='w', padx=0, pady=0, bd=0, height=1).pack(side='left')
            l=Label(f, width=3, bg='lightBlue', #text=_oldlevels[channel-1],
                font=stdfont, anchor='e', padx=1, pady=0, bd=0, height=1)
            l.pack(side='left')
            colorlabel(l)
            channel_levels.append(l)
            f.pack(side='top')
        # channel_levels is an output - changelevel will use it to access these labels

class Subpanels:
    def __init__(self, scenesparent, effectsparent, scalelevels, Subs, xfader,
        changelevel):
        
        sublist = Subs.subs.items()
        sublist.sort()

        for name, sub in sublist:
            if sub.is_effect:
                parent=effectsparent
            else:
                parent=scenesparent

            f=Frame(parent, bd=1, relief='raised')
            f.pack(fill='both',exp=1,side='left')

            if name not in scalelevels:
                scalelevels[name]=DoubleVar()

            sub.set_slider_var(scalelevels[name])

            scaleopts = {}
            if sub.color:
                scaleopts['troughcolor'] = sub.color

            s = FlyingFader(f, label=str(name), variable=scalelevels[name],
                    showvalue=0, length=300-17,
                    width=20, to=0,res=.001,from_=1,bd=1, font=stdfont,
                    **scaleopts)

            for axis in ('y','x'):
                cvar=IntVar()
                cb=Checkbutton(f,text=axis,variable=cvar,font=stdfont, padx=0, 
                               pady=0, bd=1)
                button = ('Alt','Control')[axis=='y'] # unused?
                # s.bind('<Key-%s>'%axis, lambda ev,cb=cb: cb.invoke)
                cb.pack(side='bottom',fill='both', padx=0, pady=0)
                xfader.registerbutton(name,axis,cvar)

            s.pack(side='left', fill=BOTH)

            # effects frame?
            sframe = Frame(f,bd=2,relief='groove')
            sub.draw_tk(sframe)
            sframe.pack(side='left',fill='y')
