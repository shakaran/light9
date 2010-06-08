#!/usr/bin/python
import pygst
pygst.require("0.10")
import gst, gobject
import pygtk
import gtk
from twisted.python.util import sibpath
import Image

otherPic = None


import StringIO
# gtk.gdk.pixbuf_new_from_data(img.tostring() seems like it would be better
# http://www.daa.com.au/pipermail/pygtk/2003-June/005268.html
def Image_to_GdkPixbuf (image):
    file = StringIO.StringIO ()
    image.save (file, 'ppm')
    contents = file.getvalue()
    file.close ()
    loader = gtk.gdk.PixbufLoader ('pnm')
    loader.write (contents, len (contents))
    pixbuf = loader.get_pixbuf ()
    loader.close ()
    return pixbuf

class MySink(gst.Element):
    _sinkpadtemplate = gst.PadTemplate ("sinkpadtemplate",
                                        gst.PAD_SINK,
                                        gst.PAD_ALWAYS,
                                        gst.caps_new_any())

    def __init__(self):
        gst.Element.__init__(self)
        self.sinkpad = gst.Pad(self._sinkpadtemplate, "sink")
        self.add_pad(self.sinkpad)
        self.sinkpad.set_chain_function(self.chainfunc)
        
    def chainfunc(self, pad, buffer):
        global nextImageCb
        self.info("%s timestamp(buffer):%d" % (pad, buffer.timestamp))
        
        if 1:
            try:
                cap = buffer.caps[0]
                img = Image.fromstring('RGB', (cap['width'], cap['height']),
                                       buffer.data)
            except:
                import traceback
                traceback.print_exc()
                raise

            print "got image to save"
            #pixbuf = Image_to_GdkPixbuf(img)
            #otherPic.set_from_pixbuf(pixbuf)
            
        return gst.FLOW_OK
gobject.type_register(MySink)

class Main(object):
    def __init__(self):
        global otherPic
        wtree = gtk.Builder()
        wtree.add_from_file(sibpath(__file__, "vidref.glade"))
        mainwin = wtree.get_object("MainWindow")
        otherPic = wtree.get_object("liveVideo")
        mainwin.connect("destroy", gtk.main_quit)
        wtree.connect_signals({
            "foo" : self.OnPlay,
            })

        pipeline = gst.Pipeline("player")

        def makeElem(t, n=None):
            e = gst.element_factory_make(t, n)
            pipeline.add(e)
            return e
        
        if 0:
            source = makeElem("videotestsrc", "video")
        else:
            source = makeElem("v4l2src", "vsource")
            source.set_property("device", "/dev/video0")

        csp = makeElem("ffmpegcolorspace")

        caps = makeElem("capsfilter")
        caps.set_property('caps', gst.caps_from_string('video/x-raw-rgb'))

        sink = makeElem("xvimagesink", "sink")

        recSink = MySink()
        pipeline.add(recSink)

        # using this adds 5% cpu; not sure the advantage
        scaler = makeElem("videoscale", "vscale")
        
        tee = makeElem("tee")

        source.link(sink)#csp)
#        csp.link(caps)
#        caps.link(tee)
#        tee.link(sink)

#        tee.link(recSink)
#        tee.link(sink2)

        mainwin.show_all()

#        sink2.set_xwindow_id(wtree.get_object("liveVideo").window.xid)
        sink.set_xwindow_id(wtree.get_object("vid3").window.xid)

        pipeline.set_state(gst.STATE_PLAYING)

    def OnPlay(self, widget):
        print "play"
       # Tell the video sink to display the output in our DrawingArea
        self.sinkx.set_xwindow_id(self.da.window.xid)
        self.pipeline.set_state(gst.STATE_PLAYING)

    def OnStop(self, widget):
        print "stop"
        self.pipeline.set_state(gst.STATE_READY)

    def OnQuit(self, widget):
        gtk.main_quit()
