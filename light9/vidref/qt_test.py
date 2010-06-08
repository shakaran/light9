#!/usr/bin/env python

from PyQt4 import QtCore, QtGui, uic
import gst
import gobject

class Vid(object):
    def __init__(self, windowId):
        self.player = gst.Pipeline("player")
        self.source = gst.element_factory_make("v4l2src", "vsource")
        self.sink = gst.element_factory_make("autovideosink", "outsink")
        self.source.set_property("device", "/dev/video0")
        self.scaler = gst.element_factory_make("videoscale", "vscale")
        self.window_id = None
        self.windowId = windowId

        self.fvidscale_cap = gst.element_factory_make("capsfilter", "fvidscale_cap")
        self.fvidscale_cap.set_property('caps', gst.caps_from_string('video/x-raw-yuv, width=320, height=240'))
        
        self.player.add(self.source, self.scaler, self.fvidscale_cap, self.sink)
        gst.element_link_many(self.source,self.scaler, self.fvidscale_cap, self.sink)

        self.s = MySink()
        self.player.add(self.s)
#        self.scaler.link(self.s)

        bus = self.player.get_bus()
        bus.add_signal_watch()
#        bus.enable_sync_message_emission() # with this we segv
#        bus.connect("message", self.on_message) # with this we segv
        bus.connect("sync-message::element", self.on_sync_message)

    def on_message(self, bus, message):
        print "msg", bus, message
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
           err, debug = message.parse_error()
           print "Error: %s" % err, debug
           self.player.set_state(gst.STATE_NULL)

    def on_sync_message(self, bus, message):
        print "syncmsg", bus, message
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            print "pxi"
            win_id = self.windowId
            assert win_id
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            print "set_xwindow_id"
            imagesink.set_xwindow_id(win_id)
            print "dnoe msg"

    def startPrev(self):
        self.player.set_state(gst.STATE_PLAYING)
        print "should be playing"
        

class MainWin(QtGui.QMainWindow):
    def __init__(self, *args):
        super(MainWin, self).__init__(*args)

        uic.loadUi('light9/vidref/vidref.ui', self)
        v = Vid(self.liveView.winId())
        v.startPrev()

    @QtCore.pyqtSlot()
    def startLiveView(self):
        print "slv"


