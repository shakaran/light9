#!/usr/bin/env python
from __future__ import nested_scopes

from Tix import *
from signal import signal, SIGINT
import io
from uihelpers import *
from Fader import Fader
from Lightboard import Lightboard

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

parportdmx = io.ParportDMX()

if not DUMMY:
    # this turns the parportdmx from dummy to live
    parportdmx.golive()

mr_lightboard = Lightboard(root,parportdmx,DUMMY)
root.tk_setPalette('gray40')

signal(SIGINT, mr_lightboard.quit)

#
# start net slider server in separate thread 
#
import ExternalInput, thread
thread.start_new_thread(ExternalInput.start_server,())

bindkeys(root,'<Escape>', mr_lightboard.quit)

root.bind_class("all","<ButtonPress-4>",lambda ev: eventtoparent(ev,"<ButtonPress-4>"))
root.bind_class("all","<ButtonPress-5>",lambda ev: eventtoparent(ev,"<ButtonPress-5>"))

root.mainloop() # Receiver switches main

#import profile
#profile.run("root.mainloop()","profile/idlemanysubs")
