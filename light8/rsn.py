#!/usr/bin/python
from __future__ import nested_scopes

from Tix import *
from signal import signal, SIGINT
from uihelpers import *
from Fader import Fader
from Lightboard import Lightboard

if len(sys.argv) >= 2:
    DUMMY = 0
    print "Light 8.8: This is the real thing, baby"
    window_title = "Light 8.8 (On Air)"
else:
    DUMMY = 1
    print "Light 8.8: Dummy mode"
    window_title = "Light 8.8 (Bogus)"

root = Tk()
root.wm_title(window_title)
root.wm_geometry('+462+470')
root.tk_focusFollowsMouse()


if not DUMMY:
    # this turns the parportdmx from dummy to live
    print "Light 8.8: Preparing DMX interface..."
    parportdmx.golive()

print "Light 8.8: And this...is Mr. Lightboard"
mr_lightboard = Lightboard(root,DUMMY)
# root.tk_setPalette('gray40')

signal(SIGINT, mr_lightboard.quit)

#
# start net slider server in separate thread 
#
print "Light 8.8: External input server spawned"
import ExternalInput, thread
thread.start_new_thread(ExternalInput.start_server,())

bindkeys(root,'<Escape>', mr_lightboard.quit)

root.bind_class("all","<ButtonPress-4>",lambda ev: eventtoparent(ev,"<ButtonPress-4>"))
root.bind_class("all","<ButtonPress-5>",lambda ev: eventtoparent(ev,"<ButtonPress-5>"))

print 'Light 8.8: "Uh...Shiny McShine?"'
root.mainloop() # Receiver switches main

#import profile
#profile.run("root.mainloop()","profile/idlemanysubs")
