#!/usr/bin/python

"""

dvcam test
gst-launch dv1394src ! dvdemux name=d ! dvdec ! ffmpegcolorspace ! hqdn3d ! xvimagesink

"""
import pygst
pygst.require("0.10")
import gst, gobject, time, jsonlib, restkit, logging, os, traceback
from decimal import Decimal
from bisect import bisect_left
import pygtk
import gtk
from twisted.python.util import sibpath
import Image
from threading import Thread
from Queue import Queue
from light9 import networking
logging.basicConfig(level=logging.WARN)
logging.getLogger().setLevel(logging.WARN)
#restkit.set_logging(logging.WARN)

existingDir = "/tmp/vidref/play-light9.bigasterisk.com_show_dance2010_song7-1276065914"
existingFrames = sorted([Decimal(f.split('.jpg')[0])
                         for f in os.listdir(existingDir)])

otherPic = None

class VideoRecordSink(gst.Element):
    _sinkpadtemplate = gst.PadTemplate ("sinkpadtemplate",
                                        gst.PAD_SINK,
                                        gst.PAD_ALWAYS,
                                        gst.caps_new_any())

    def __init__(self):
        gst.Element.__init__(self)
        self.sinkpad = gst.Pad(self._sinkpadtemplate, "sink")
        self.add_pad(self.sinkpad)
        self.sinkpad.set_chain_function(self.chainfunc)
        self.lastTime = 0
        
        self.musicResource = restkit.Resource(networking.musicUrl(api='rest'))

        self.imagesToSave = Queue()
        self.startBackgroundImageSaver(self.imagesToSave)

    def startBackgroundImageSaver(self, imagesToSave):
        """do image saves in another thread to not block gst"""
        def imageSaver():
            while True:
                args = imagesToSave.get()
                self.saveImg(*args)
                imagesToSave.task_done()
        
        t = Thread(target=imageSaver)
        t.setDaemon(True)
        t.start()
        
    def chainfunc(self, pad, buffer):
        global nextImageCb
        self.info("%s timestamp(buffer):%d" % (pad, buffer.timestamp))

        try:
            position = jsonlib.loads(self.musicResource.get("position").body,
                                     use_float=True)
            if not position['song']:
                return gst.FLOW_OK
            

            cap = buffer.caps[0]
            img = Image.fromstring('RGB', (cap['width'], cap['height']),
                                   buffer.data)
            self.imagesToSave.put((position, img, buffer.timestamp))
        except:
            traceback.print_exc()

        try:
            self.updateOtherFrames(position)
        except:
            traceback.print_exc()
        
        return gst.FLOW_OK

    def saveImg(self, position, img, bufferTimestamp):
        outDir = "/tmp/vidref/play-%s-%d" % (
            position['song'].split('://')[-1].replace('/','_'),
            position['started'])
        outFilename = "%s/%08.03f.jpg" % (outDir, position['t'])
        if os.path.exists(outFilename): # we're paused on one time
            return
        
        try:
            os.makedirs(outDir)
        except OSError:
            pass

        img.save(outFilename)

        now = time.time()
        print "wrote %s delay of %.2fms %s" % (outFilename,
                                        (now - self.lastTime) * 1000,
                                               bufferTimestamp)
        self.lastTime = now

    def updateOtherFrames(self, position):
        inPic = self.findClosestFrame(position['t']+.2)
        #print "load", inPic
        with gtk.gdk.lock:
            otherPic.set_from_file(inPic)
            if 0:
                otherPic.queue_draw_area(0,0,320,240)
                otherPic.get_window().process_updates(True)

    def findClosestFrame(self, t):
        i = bisect_left(existingFrames, Decimal(str(t)))
        if i >= len(existingFrames):
            i = len(existingFrames) - 1
        return os.path.join(existingDir, "%08.03f.jpg" % existingFrames[i])
    


gobject.type_register(VideoRecordSink)

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

        # other sources: videotestsrc, v4l2src device=/dev/video0
        ## if 0:
        ##     source = makeElem("videotestsrc", "video")
        ## else:
        ##     source = makeElem("v4l2src", "vsource")
        ##     source.set_property("device", "/dev/video0")

        dv = "dv1394src ! dvdemux ! dvdec ! videoscale ! video/x-raw-yuv,width=320,height=240;video/x-raw-rgb,width=320,height=240 ! queue name=vid"
        v4l = "v4l2src device=/dev/video0 ! hqdn3d name=vid" 

        pipeline = gst.parse_launch(dv)

        def makeElem(t, n=None):
            e = gst.element_factory_make(t, n)
            pipeline.add(e)
            return e
        
        sink = makeElem("xvimagesink")
        recSink = VideoRecordSink()
        pipeline.add(recSink)

        tee = makeElem("tee")
        
        caps = makeElem("capsfilter")
        caps.set_property('caps', gst.caps_from_string('video/x-raw-rgb'))

        gst.element_link_many(pipeline.get_by_name("vid"), tee, sink)
        gst.element_link_many(tee, makeElem("ffmpegcolorspace"), caps, recSink)

        mainwin.show_all()

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
