#!/usr/bin/env python
from __future__ import nested_scopes

from Tix import *
from time import sleep
from signal import signal, SIGINT
import sys, cPickle

import io
from uihelpers import *
from panels import *
from Xfader import *
from subediting import Subediting
from Fader import Fader
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
root.wm_geometry('+462+470')
root.tk_focusFollowsMouse()

import Subs, Patch

def get_data(*args):
    Subs.reload_data(DUMMY)
    Patch.reload_data(DUMMY)
    print "Patch:", Patch.patch
    print "Subs:", ', '.join(Subs.subs.keys())

get_data()

parportdmx = io.ParportDMX(DUMMY)

class Lightboard:
    def __init__(self, master):
        self.master = master

        self.channel_levels = []
        self.scalelevels = {}
        self.xfader = Xfader(self.scalelevels) # doesn't draw any UI yet-- look for self.xfader.setupwidget()
        self.oldlevels = [None] * 68 # never replace this; just clear it
        self.subediting = Subediting(currentoutputlevels=self.oldlevels)

        self.buildinterface()
        self.load()
        self.backgroundloop()
        
    def buildinterface(self):
        global DUMMY
        for w in self.master.winfo_children():
            w.destroy()

        stage_tl = toplevelat(22,30)
        s = stage.Stage(stage_tl)
        stage.createlights(s)
        s.setsubediting(self.subediting)
        s.pack()

        sub_tl = toplevelat(0,0)
        effect_tl = toplevelat(462,4)

        self.subpanels = Subpanels(sub_tl, effect_tl, self, self.scalelevels,
                                   Subs, self.xfader, self.changelevel,
                                   self.subediting, Subs.longestsubname())

        leveldisplay_tl = toplevelat(873,400)
        leveldisplay_tl.bind('<Escape>', sys.exit)

        self.leveldisplay = Leveldisplay(leveldisplay_tl, self.channel_levels)
        for i in range(0,len(self.channel_levels)):
            self.channel_levels[i].config(text=self.oldlevels[i])
            colorlabel(self.channel_levels[i])

        Console(self)

        # root frame
        controlpanel = Controlpanel(root, self.xfader, self.refresh, self.quit)
        
        xf=Frame(root)
        xf.pack(side='right')

        root.bind('<q>', self.quit)
        root.bind('<r>', self.refresh)
        leveldisplay_tl.bind('<q>', self.quit)
        leveldisplay_tl.bind('<r>', self.refresh)

        self.xfader.setupwidget(xf)
        controlpanel.pack()

        # cuefader_tl = toplevelat(98, 480)
        # cuefader = Fader(cuefader_tl, Subs.cues, self.scalelevels)
        # cuefader.pack()

    def refresh(self, *args):
        'rebuild interface, reload data'
        get_data()
        self.subediting.refresh()
        self.buildinterface()
        bindkeys(root,'<Escape>', self.quit)

    def stageassub(self):
        """returns the current onstage lighting as a levels
        dictionary, skipping the zeros, and using names where
        possible"""
        levs=self.oldlevels
        
        return dict([(Patch.get_channel_name(i),l) for i,l
                     in zip(range(1,len(levs)+1),levs)
                     if l>0])
    def save_sub(self, name, levels):
        if not name:
            print "Enter sub name in console."
            return

        st = ''
        linebuf = 'subs["%s"] = {' % name
        for channame,lev in levels.items():
            if len(linebuf) > 60: 
                st += linebuf + '\n   '
                linebuf = ''

            linebuf += ' "%s" : %d,' % (channame, lev)
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

    # this is called on a loop, and ALSO by the Scales
    def changelevel(self, *args):
        'Amp trims slider'

        levels = [0] * 68
        for name, s in Subs.subs.items():
            newlevels = s.get_levels(level=self.scalelevels[name].get())
            for (ch, fadelev) in newlevels.items():
                levels[ch-1] = max(levels[ch-1], fadelev)

        levels = [int(l) for l in levels]

        for lev,lab,oldlev,numlab in zip(levels, self.channel_levels, 
                                         self.oldlevels, 
                                         self.leveldisplay.number_labels):
            if lev != oldlev:
                lab.config(text="%d" % lev)
                colorlabel(lab)
                if lev < oldlev:
                    numlab['bg'] = 'blue'
                else:
                    numlab['bg'] = 'red'
            else:
                numlab['bg'] = 'lightPink'

        self.oldlevels[:] = levels[:] # replace the elements in oldlevels - don't make a new list (Subediting is watching it)
            
        parportdmx.sendlevels(levels)

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
            for name, substate in p.substate.items():
                try:
                    Subs.subs[name].set_state(substate)
                except:
                    print "Couldn't set sub %s state" % name
        except IOError:
            print "IOError: Couldn't load prefs (%s)" % filename
        except EOFError:
            print "EOFrror: Couldn't load prefs (%s)" % filename
        except:
            print "BigTrouble: Couldn't load prefs (%s)" % filename

    def backgroundloop(self, *args):
        self.master.after(50, self.backgroundloop, ())
        self.changelevel()
    def quit(self, *args):
        self.save()
        root.destroy()
        sys.exit()
    def save(self, *args):
        filename = '/tmp/light9.prefs'
        if DUMMY:
            filename += '.dummy'
        print "Saving to", filename
        file = open(filename, 'w')
        try:
            cPickle.dump(Pickles(self.scalelevels, Subs.subs.items()), file)
        except cPickle.UnpickleableError:
            print "UnpickleableError!  There's yer problem."

class Pickles:
    def __init__(self, scalelevels, subs=None):
        self.scalelevels = dict([(name, lev.get()) 
            for name, lev in scalelevels.items()])
        self.substate = dict([(name, subobj.get_state())
            for name, subobj in subs])
        # print "substate", self.substate

mr_lightboard = Lightboard(root)

signal(SIGINT, mr_lightboard.quit)
bindkeys(root,'<Escape>', mr_lightboard.quit)

root.mainloop() # Receiver switches main
