#!/usr/bin/env python
from __future__ import nested_scopes

from Tkinter import *
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
root.tk_focusFollowsMouse()

import Subs, Patch

def get_data(*args):
    Subs.reload_data(DUMMY)
    Patch.reload_data(DUMMY)
    print "Patch:", Patch.patch
    print "Subs:", ', '.join(Subs.subs.keys())

get_data()

io.init(DUMMY)

class Lightboard:
    def __init__(self, master):
        self.master = master

        self.channel_levels = []
        self.scalelevels = {}
        self.oldlevels = [None] * 68

        self.buildinterface()
        self.load()
        self.backgroundloop()
    def buildinterface(self):
        for w in self.master.winfo_children():
            w.destroy()

        stage_tl = toplevelat(165,90)
        s = stage.Stage(stage_tl)
        stage.createlights(s)
        s.pack()

        sub_tl = toplevelat(0,0)
        effect_tl = toplevelat(0,352)

        self.xfader = Xfader(self.scalelevels)

        self.subpanels = Subpanels(sub_tl, effect_tl, self.scalelevels, Subs, 
            self.xfader, self.changelevel)

        leveldisplay_tl = toplevelat(873,400)
        leveldisplay_tl.bind('<Escape>', sys.exit)

        leveldisplay = Leveldisplay(leveldisplay_tl, self.channel_levels)

        Console()

        # root frame
        controlpanel = Controlpanel(root, self.xfader, self.refresh, quit)
        
        xf=Frame(root)
        xf.pack(side='right')

        root.bind('<q>', quit)
        root.bind('<r>', self.refresh)
        leveldisplay_tl.bind('<q>', quit)
        leveldisplay_tl.bind('<r>', self.refresh)

        self.xfader.setupwidget(xf)
        controlpanel.pack()

    def refresh(self, *args):
        'rebuild interface, reload data'
        get_data()
        self.buildinterface()
        bindkeys(root,'<Escape>', quit)

    # this is called on a loop, and ALSO by the Scales
    def changelevel(self, *args):
        'Amp trims slider'

        levels = [0] * 68
        for name, s in Subs.subs.items():
            newlevels = s.get_levels(level=self.scalelevels[name].get())
            for (ch, fadelev) in newlevels.items():
                levels[ch-1] = max(levels[ch-1], fadelev)

        levels = [int(l) for l in levels]

        for lev,lab,oldlev in zip(levels, self.channel_levels, self.oldlevels):
            if lev != oldlev:
                lab.config(text="%d" % lev)
                colorlabel(lab)

        self.oldlevels = levels[:]
            
        io.sendlevels(levels)

    def load(self):
        try:
            filename = '/tmp/light9.prefs'
            if DUMMY:
                filename += '.dummy'
            print "Loading from", filename
            file = open(filename, 'r')
            p = cPickle.load(file)
            for s, v in p.scalelevels.items():
                try:
                    self.scalelevels[s].set(v)
                except:
                    print "Couldn't set %s -> %s" % (s, v)
        except:
            print "Couldn't load prefs (%s)" % filename

    def make_sub(self, name):
        i = 1
        # name = console_entry.get() # read from console
        if not name:
            print "Enter sub name in console."
            return

        st = ''
        linebuf = 'subs["%s"] = {' % name
        for l in self.oldlevels:
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
        self.refresh()
    def backgroundloop(self, *args):
        self.master.after(50, self.backgroundloop, ())
        self.changelevel()
    def quit(self, *args):
        filename = '/tmp/light9.prefs'
        if DUMMY:
            filename += '.dummy'
        print "Saving to", filename
        file = open(filename, 'w')
        cPickle.dump(Pickles(self.scalelevels), file)
        root.destroy()
        sys.exit()

class Pickles:
    def __init__(self, scalelevels):
        self.scalelevels = dict([(name, lev.get()) 
            for name,lev in scalelevels.items()])

mr_lightboard = Lightboard(root)

signal(SIGINT, mr_lightboard.quit)
bindkeys(root,'<Escape>', mr_lightboard.quit)

# bindkeys(root,'<q>', quit)
# bindkeys(root,'<r>', refresh)
# bindkeys(root,'<s>', make_sub)
root.mainloop() # Receiver switches main
