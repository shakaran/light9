#!/usr/bin/env python
from __future__ import nested_scopes

from Tkinter import *
from parport import *
from time import sleep
from signal import *
import sys, thread, cPickle

import io
from uihelpers import *
from panels import *
from Xfader import *
import stage

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

io.init(DUMMY)

channel_levels = []
scalelevels = {}
fades = {}

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
        
    io.sendlevels(levels)

def backgroundloop(*args):
    root.after(50, backgroundloop, ())
    changelevel()

buildinterface = None # temporary
def refresh(*args):
    get_data()
    buildinterface()
    bindkeys(root,'<Escape>', quit)

def quit(*args):
    filename = '/tmp/light9.prefs'
    if DUMMY:
        filename += '.dummy'
    print "Saving to", filename
    file = open(filename, 'w')
    cPickle.dump(Pickles(scalelevels), file)
    root.destroy()
    sys.exit()


xfader=Xfader(scalelevels)



def buildinterface(*args):
    global channel_levels, _oldlevels, leveldisplay, xfader
    for w in root.winfo_children():
        w.destroy()

    stage_tl=toplevelat(165,90)
    s=stage.Stage(stage_tl)
    stage.createlights(s)
    s.pack()

    sub_tl = toplevelat(0,0)
    effect_tl = toplevelat(0,352)

    Subpanels(sub_tl,effect_tl,scalelevels,Subs,xfader,changelevel)

    # def event_printer(evt):
        # print dir(evt)

    # sub_tl.bind('<b>', event_printer)
    leveldisplay=toplevelat(873,400)
    leveldisplay.bind('<Escape>', sys.exit)

    Leveldisplay(leveldisplay,_oldlevels)

    Console()

    # root frame
    controlpanel = Controlpanel(root,xfader,refresh,quit)
    
    xf=Frame(root)
    xf.pack(side='right')

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
bindkeys(root,'<Escape>', quit)

# bindkeys(root,'<q>', quit)
# bindkeys(root,'<r>', refresh)
# bindkeys(root,'<s>', make_sub)
backgroundloop()
root.mainloop() # Receiver switches main

while 1:
    for lev in range(0,255,25)+range(255,0,-25):
        sleep(.2)
