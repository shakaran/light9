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
from Lightboard import Lightboard

import Subs, Patch



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


parportdmx = io.ParportDMX(DUMMY)

mr_lightboard = Lightboard(root,parportdmx,DUMMY)

signal(SIGINT, mr_lightboard.quit)
bindkeys(root,'<Escape>', mr_lightboard.quit)

root.mainloop() # Receiver switches main
