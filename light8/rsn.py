#!/usr/bin/env python
from __future__ import nested_scopes

from Tkinter import *
from parport import *
from time import sleep
from signal import *
import sys, thread, cPickle

from Xfader import *

if len(sys.argv) >= 2:
    DUMMY = 0
    print "This is the real thing, baby"
    window_title = "Light 8.8 (On Air)"
else:
    DUMMY = 1
    print "Dummy mode"
    window_title = "Light 8.8 (Bogus)"

root = Tk()
root.wm_title(window_title)
root.wm_geometry('+447+373')

import Subs, Patch

def get_data(*args):
    Subs.reload_data(DUMMY)
    Patch.reload_data(DUMMY)
    print "Patch:", Patch.patch
    print "Subs:", ', '.join(Subs.subs.keys())

get_data()

if not DUMMY:
    getparport()

def sendlevels(levels):
    if DUMMY: return
    levels = list(levels) + [0]
    if levels[14] > 0: levels[14] = 100
    # print "levels", ' '.join(["%3.1f" % l for l in levels])
    outstart()
    for p in range(1,70):
        outbyte(levels[p-1]*255/100)

channel_levels = []
scalelevels = {}
fades = {}
stdfont = ('Arial', 8)
monofont = ('Courier', 8)

def colorlabel(label):
    txt=label['text'] or "0"
    lev=float(txt)/100
    low=(80,80,180)
    high=(255,55,050)
    out = [int(l+lev*(h-l)) for h,l in zip(high,low)]
    col="#%02X%02X%02X" % tuple(out)
    label.config(bg=col)

_oldlevels=[None] * 68

def changelevel(*args):
    'Amp trims slider'
    global _oldlevels

    levels = [0] * 68
    for name, s in Subs.subs.items():
        newlevels = s.get_levels(level=scalelevels[name].get())
        for (ch, fadelev) in newlevels.items():
            levels[ch-1] = max(levels[ch-1], fadelev)

    levels = [int(l) for l in levels]
    
    for lev,lab,oldlev in zip(levels, channel_levels, _oldlevels):
        if lev != oldlev:
            lab.config(text="%d" % lev)
            colorlabel(lab)

    _oldlevels = levels[:]
        
    sendlevels(levels)

def backgroundloop(*args):
    root.after(50, backgroundloop, ())
    changelevel()
    
def make_frame(parent):
    f = Frame(parent, bd=0)
    f.pack(side='left')
    return f

def add_fade(slider, evt):
    print 'b3!'

def execute(evt, str):
    if str[0] == '*': # make a new sub
        make_sub(str)
    else:
        print '>>>', str
        print eval(str)
    console_frame.focus()
    
def console():
    global console_entry, console_frame
    print "Light 8: Everything's under control"
    t=Toplevel(root)
    console_frame = Frame(t)
    console_entry=Entry(console_frame)
    console_entry.pack(expand=1, fill='x')
    console_entry.bind('<Return>', lambda evt: execute(evt, 
                                        console_entry.get()))
    console_frame.pack(fill=BOTH, expand=1)
    t.wm_geometry("599x19+267+717")

buildinterface = None # temporary
def refresh(*args):
    get_data()
    buildinterface()
    bindkeys('<Escape>', quit)

def quit(*args):
    filename = '/tmp/light9.prefs'
    if DUMMY:
        filename += '.dummy'
    print "Saving to", filename
    file = open(filename, 'w')
    cPickle.dump(Pickles(scalelevels), file)
    root.destroy()
    sys.exit()

def bindkeys(key, func):
    root.bind(key, func)
    for w in root.winfo_children():
        w.bind(key, func)


def toggle_slider(s):
    if s.get() == 0:
        s.set(100)
    else:
        s.set(0)
def printout(t):
    print t
    
xfader=Xfader(scalelevels)

def buildinterface(*args):
    global channel_levels, _oldlevels, leveldisplay, stdfont, monofnt, xfader
    for w in root.winfo_children():
        w.destroy()

    sublist = Subs.subs.items()
    sublist.sort()

    sub_tl = Toplevel()
    sub_tl.wm_geometry("+0+0")
    effect_tl = Toplevel()
    effect_tl.wm_geometry("+0+352")

    for name, sub in sublist:
        if sub.is_effect:
            f=Frame(effect_tl, bd=1, relief='raised')
        else:
            f=Frame(sub_tl, bd=1, relief='raised')

        f.pack(fill='both',exp=1,side='left')
        
        if name not in scalelevels:
            scalelevels[name]=DoubleVar()

        sub.set_slider_var(scalelevels[name])

        scaleopts = {}
        if sub.color:
            scaleopts['troughcolor'] = sub.color
        s=Scale(f,command=lambda l,name=name: changelevel(name,l),showvalue=0,
                length=300-17,variable=scalelevels[name],width=20,
                to=0,res=.001,from_=1,bd=1, **scaleopts)
        l=Label(f,text=str(name), font=stdfont, padx=0, pady=0)
        v=Label(f,textvariable=scalelevels[name], font=stdfont, padx=0, pady=0)
        l.pack(side='bottom')
        v.pack(side='bottom')

        for axis in ('y','x'):
            cvar=IntVar()
            cb=Checkbutton(f,text=axis,variable=cvar,font=stdfont, padx=0, pady=0, bd=1)
            button = ('Alt','Control')[axis=='y'] # unused?
#            s.bind('<Key-%s>'%axis, lambda ev,cb=cb: cb.invoke)
            cb.pack(side='bottom',fill='both', padx=0, pady=0)
            xfader.registerbutton(name,axis,cvar)

        s.pack(side='left')
        s.bind('<3>', lambda evt, v=scalelevels[name]: toggle_slider(v))\
        
        sframe = Frame(f,bd=2,relief='groove')
        sub.draw_tk(sframe)
        sframe.pack(side='left',fill='y')

    # def event_printer(evt):
        # print dir(evt)

    # sub_tl.bind('<b>', event_printer)
    leveldisplay=Toplevel(root)    
    leveldisplay.bind('<Escape>', sys.exit)
    leveldisplay.wm_geometry('+873+400')
    frames = (make_frame(leveldisplay), make_frame(leveldisplay))
    channel_levels=[]
    for channel in range(1, 69):
        f=Frame(frames[channel > 34])
        Label(f,text=str(channel), width=3, bg='lightPink', 
            font=stdfont, padx=0, pady=0, bd=0, height=1).pack(side='left')
        Label(f,text=Patch.get_channel_name(channel), width=8, 
            font=stdfont, anchor='w', padx=0, pady=0, bd=0, height=1).pack(side='left')
        l=Label(f,text=_oldlevels[channel-1], width=3, bg='lightBlue', 
            font=stdfont, anchor='e', padx=1, pady=0, bd=0, height=1)
        l.pack(side='left')
        colorlabel(l)
        channel_levels.append(l)
        f.pack(side='top')
    
    console()

    # root frame
    controlpanel = Frame(root)
    xf=Frame(controlpanel)
    xf.pack(side='right')
    for txt,cmd in (
        ('Quit',       quit),
        ('Refresh',    refresh),
        ('Clear all', xfader.clearallbuttons),
        ('On -> X',     lambda: xfader.grab('x')),
        ('Clear X',     lambda: xfader.clearallbuttons('x')),
        ('On -> Y',     lambda: xfader.grab('y')),
        ('Clear Y',     lambda: xfader.clearallbuttons('y'))):
        Button(controlpanel, text=txt, command=cmd).pack(side='top', fill='x')

    # Button(controlpanel, text='Quit',       command=quit).pack(side='left')
    # Button(controlpanel, text='Refresh',    command=refresh).pack(side='left')
    # Button(controlpanel, text='Clearxfade', command=xfader.clearallbuttons).pack(side='left')
    # Button(controlpanel, text='Grab x',     command=lambda: xfader.grab('x')).pack(side='left')
    # Button(controlpanel, text='Grab y',     command=lambda: xfader.grab('y')).pack(side='left')

    root.bind('<q>', quit)
    root.bind('<r>', refresh)
    leveldisplay.bind('<q>', quit)
    leveldisplay.bind('<r>', refresh)

    xfader.setupwidget(xf)
    controlpanel.pack()

buildinterface()

class Pickles:
    def __init__(self, scalelevels):
        self.scalelevels = dict([(name, lev.get()) 
            for name,lev in scalelevels.items()])

def load():
    try:
        filename = '/tmp/light9.prefs'
        if DUMMY:
            filename += '.dummy'
        print "Loading from", filename
        file = open(filename, 'r')
        p = cPickle.load(file)
        for s, v in p.scalelevels.items():
            try:
                scalelevels[s].set(v)
            except:
                print "Couldn't set %s -> %s" % (s, v)
    except:
        print "Couldn't load prefs (%s)" % filename

def make_sub(name):
    global _oldlevels
    i = 1
    # name = console_entry.get() # read from console
    if not name:
        print "Enter sub name in console."
        return

    st = ''
    linebuf = 'subs["%s"] = {' % name
    for l in _oldlevels:
        if l:
            if len(linebuf) > 60: 
                st += linebuf + '\n   '
                linebuf = ''

            linebuf += ' "%s" : %d,' % (Patch.get_channel_name(i), l)
        i += 1
    st += linebuf + '}\n'
    if DUMMY:
        filename = 'ConfigDummy.py'
    else:
        filename = 'Config.py'
    f = open(filename, 'a')
    f.write(st)
    f.close()
    print 'Added sub:', st
    refresh()

load()
signal(SIGINT, quit)
bindkeys('<Escape>', quit)

# bindkeys('<q>', quit)
# bindkeys('<r>', refresh)
# bindkeys('<s>', make_sub)
backgroundloop()
root.mainloop() # Receiver switches main

while 1:
    for lev in range(0,255,25)+range(255,0,-25):
        sleep(.2)
