from __future__ import nested_scopes

from Tix import *
from signal import signal, SIGINT
import sys, cPickle, random

from uihelpers import *
from panels import *
from Xfader import *
from subediting import Subediting
from Fader import Fader
from ExternalInput import ExternalSliders
import io, stage, Subs, Patch, ExtSliderMapper

class Pickles:
    def __init__(self, scalelevels, subs=None, windowpos=None):
        self.scalelevels = dict([(name, lev.get()) 
            for name, lev in scalelevels.items()])
        self.substate = dict([(name, subobj.get_state())
            for name, subobj in subs])
        self.windowpos = windowpos

class Lightboard:
    def __init__(self, master, parportdmx, DUMMY):
        self.master = master
        self.parportdmx = parportdmx
        self.DUMMY = DUMMY
        self.jostle_mode = 0

        self.channel_levels = []
        self.scalelevels = {}
        # doesn't draw any UI yet-- look for self.xfader.setupwidget()
        self.xfader = Xfader(self.scalelevels) 
        self.oldlevels = [None] * 68 # never replace this; just clear it
        self.subediting = Subediting(currentoutputlevels=self.oldlevels)

        self.windowpos = 0
        self.get_data()
        self.buildinterface()
        self.load()
        self.backgroundloop()
        self.updatestagelevels()
        
    def buildinterface(self):
        for w in self.master.winfo_children():
            w.destroy()

        stage_tl = toplevelat('stage')
        s = stage.Stage(stage_tl)
        stage.createlights(s)
        s.setsubediting(self.subediting)
        s.pack()
        self.stage = s # save it

        sub_tl = toplevelat('sub')
        scene_tl = toplevelat('scenes')
        effect_tl = toplevelat('effect')

        mapping_tl = toplevelat('mapping')
        self.slidermapper = ExtSliderMapper.ExtSliderMapper(mapping_tl, 
                                                            self.scalelevels, 
                                                            ExternalSliders())
        self.slidermapper.pack()

        self.subpanels = Subpanels(sub_tl, effect_tl, scene_tl, self, self.scalelevels,
                                   Subs, self.xfader, self.changelevel,
                                   self.subediting, Subs.longestsubname())

        leveldisplay_tl = toplevelat('leveldisplay')
        leveldisplay_tl.bind('<Escape>', sys.exit)

        self.leveldisplay = Leveldisplay(leveldisplay_tl, self.channel_levels)
        for i in range(0,len(self.channel_levels)):
            self.channel_levels[i].config(text=self.oldlevels[i])
            colorlabel(self.channel_levels[i])

        Console(self)

        # root frame
        controlpanel = Controlpanel(self.master, self.xfader, self.refresh, 
            self.quit, self.toggle_jostle)
        
        xf=Frame(self.master)
        xf.pack(side='right')

        self.master.bind('<q>', self.quit)
        self.master.bind('<r>', self.refresh)
        leveldisplay_tl.bind('<q>', self.quit)
        leveldisplay_tl.bind('<r>', self.refresh)

        self.xfader.setupwidget(xf)
        controlpanel.pack()

        cuefader_tl = toplevelat('cuefader')
        cuefader = Fader(cuefader_tl, Subs.cues, self.scalelevels)
        cuefader.pack()

    def get_data(self,*args):
        Subs.reload_data(self.DUMMY)
        Patch.reload_data(self.DUMMY)
        print "Patch:", Patch.patch
        print "Subs:", ', '.join(Subs.subs.keys())

    def refresh(self, *args):
        'rebuild interface, reload data'
        self.get_data()
        self.subediting.refresh()
        self.buildinterface()
        bindkeys(self.master,'<Escape>', self.quit)
        self.master.tk_setPalette('gray40')

    def stageassub(self):
        """returns the current onstage lighting as a levels
        dictionary, skipping the zeros, and using names where
        possible"""
        levs=self.oldlevels
        
        return dict([(Patch.get_channel_name(i),l) for i,l
                     in zip(range(1,len(levs)+1),levs)
                     if l>0])
    def save_sub(self, name, levels, refresh=1):
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
        if self.DUMMY:
            filename = 'ConfigDummy.py'
        else:
            filename = 'Config.py'
        f = open(filename, 'a')
        f.write(st)
        f.close()
        print 'Added sub:', st
        if refresh:
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

        # load levels from external sliders
        extlevels = self.slidermapper.get_levels()
        for name, val in extlevels.items():
            if name in self.scalelevels:
                self.scalelevels[name].set(val)
        
        for lev,lab,oldlev,numlab in zip(levels, self.channel_levels, 
                                         self.oldlevels, 
                                         self.leveldisplay.number_labels):
            if lev != oldlev:
                lab.config(text="%d" % lev) # update labels in lev display
                colorlabel(lab)             # recolor labels
                if lev < oldlev:
                    numlab['bg'] = 'blue'
                else:
                    numlab['bg'] = 'red'
            else:
                numlab['bg'] = 'lightPink'

        self.oldlevels[:] = levels[:] # replace the elements in oldlevels - don't make a new list (Subediting is watching it)
            
        if self.jostle_mode:
            delta = random.randrange(-1, 2, 1) # (-1, 0, or 1)
            # print "delta", delta
            levels = [min(100, max(x + delta, 0)) for x in levels]
            # print "jostled", levels

        self.parportdmx.sendlevels(levels)

    def updatestagelevels(self):
        self.master.after(100, self.updatestagelevels)
        for lev, idx in zip(self.oldlevels, xrange(0, 68 + 1)):
            self.stage.updatelightlevel(Patch.get_channel_name(idx + 1), lev)

    def load(self):
        try:
            filename = '/tmp/light9.prefs'
            if self.DUMMY:
                filename += '.dummy'
            print "Loading from", filename
            file = open(filename, 'r')
            p = cPickle.load(file)
            for s, v in p.scalelevels.items():
                try:
                    self.scalelevels[s].set(v)
                except Exception,e:
                    print "Couldn't set %s -> %s: %s" % (s, v,e)
            for name, substate in p.substate.items():
                try:
                    Subs.subs[name].set_state(substate)
                except Exception, e:
                    print "Couldn't set sub %s state: %s" % (name,e)
        except IOError, e:
            print "IOError: Couldn't load prefs (%s): %s" % (filename,e)
        except EOFError, e:
            print "EOFrror: Couldn't load prefs (%s): %s" % (filename,e)
        except Exception,e:
            print "Couldn't load prefs (%s): %s" % (filename,e)
        self.slidermapper.setup()

    def backgroundloop(self, *args):
        self.master.after(50, self.backgroundloop, ())
        self.changelevel()
    def quit(self, *args):
        self.save()
        self.master.destroy()
        sys.exit()
    def save(self, *args):
        filename = '/tmp/light9.prefs'
        if self.DUMMY:
            filename += '.dummy'
        print "Saving to", filename
        file = open(filename, 'w')

        try:
            cPickle.dump(Pickles(self.scalelevels, Subs.subs.items()), file)
        except cPickle.UnpickleableError:
            print "UnpickleableError!  There's yer problem."
    def toggle_jostle(self, *args):
        self.jostle_mode = not self.jostle_mode
