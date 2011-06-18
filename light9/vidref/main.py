#!/usr/bin/python

"""

dvcam test
gst-launch dv1394src ! dvdemux name=d ! dvdec ! ffmpegcolorspace ! hqdn3d ! xvimagesink

"""
import pygst
pygst.require("0.10")
import gst, gobject, time, jsonlib, restkit, logging, os, traceback
import gtk
from twisted.python.util import sibpath
import Image
from threading import Thread
from Queue import Queue
from light9 import networking
from light9.vidref.replay import ReplayViews, songDir, takeDir, framerate

log = logging.getLogger()

class MusicTime(object):
    """
    fetch times from ascoltami in a background thread; return times
    upon request, adjusted to be more precise with the system clock
    """
    def __init__(self, period=.2, onChange=lambda position: None):
        """period is the seconds between http time requests.

        We call onChange with the time in seconds and the total time

        The choice of period doesn't need to be tied to framerate,
        it's more the size of the error you can tolerate (since we
        make up times between the samples, and we'll just run off the
        end of a song)
        """
        self.period = period
        self.onChange = onChange
        self.musicResource = restkit.Resource(networking.musicPlayer.url)
        t = Thread(target=self._timeUpdate)
        t.setDaemon(True)
        t.start()

    def getLatest(self):
        """
        dict with 't' and 'song', etc.
        """
        if not hasattr(self, 'position'):
            return {'t' : 0, 'song' : None}
        pos = self.position.copy()
        if pos['playing']:
            pos['t'] = pos['t'] + (time.time() - self.positionFetchTime)
        return pos

    def _timeUpdate(self):
        while True:
            try:
                position = jsonlib.loads(self.musicResource.get("time").body_string(),
                                         use_float=True)

                # this is meant to be the time when the server gave me its
                # report, and I don't know if that's closer to the
                # beginning of my request or the end of it (or some
                # fraction of the way through)
                self.positionFetchTime = time.time()

                self.position = position
                self.onChange(position)
            except restkit.RequestError, e:
                log.error(e)
                time.sleep(1)
            time.sleep(self.period)

    def sendTime(self, t):
        """request that the player go to this time"""
        self.musicResource.post("time", payload=jsonlib.dumps({"t" : t}),
                                headers={"content-type" : "application/json"})
        
class VideoRecordSink(gst.Element):
    _sinkpadtemplate = gst.PadTemplate ("sinkpadtemplate",
                                        gst.PAD_SINK,
                                        gst.PAD_ALWAYS,
                                        gst.caps_new_any())

    def __init__(self, musicTime, updateRecordingTo):
        gst.Element.__init__(self)
        self.updateRecordingTo = updateRecordingTo
        self.sinkpad = gst.Pad(self._sinkpadtemplate, "sink")
        self.add_pad(self.sinkpad)
        self.sinkpad.set_chain_function(self.chainfunc)
        self.lastTime = 0
        
        self.musicTime = musicTime

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
        position = self.musicTime.getLatest()

        if not position['song']:
            print "no song" # todo: this prints too much when the player has no song
            return gst.FLOW_OK

        try:
            cap = buffer.caps[0]
            img = Image.fromstring('RGB', (cap['width'], cap['height']),
                                   buffer.data)
            self.imagesToSave.put((position, img, buffer.timestamp))
        except:
            traceback.print_exc()

        return gst.FLOW_OK

    def saveImg(self, position, img, bufferTimestamp):
        t1 = time.time()
        outDir = takeDir(songDir(position['song']), position['started'])
        outFilename = "%s/%08.03f.jpg" % (outDir, position['t'])
        if os.path.exists(outFilename): # we're paused on one time
            return
        
        try:
            os.makedirs(outDir)
        except OSError:
            pass

        img.save(outFilename)

        now = time.time()
        log.info("wrote %s delay of %.2fms, took %.2fms",
                  outFilename,
                  (now - self.lastTime) * 1000,
                  (now - t1) * 1000)
        self.updateRecordingTo(outDir)
        self.lastTime = now

gobject.type_register(VideoRecordSink)

class Main(object):
    def __init__(self):
        self.musicTime = MusicTime(onChange=self.onMusicTimeChange)
        wtree = gtk.Builder()
        wtree.add_from_file(sibpath(__file__, "vidref.glade"))
        mainwin = wtree.get_object("MainWindow")
        mainwin.connect("destroy", gtk.main_quit)
        wtree.connect_signals(self)

        self.recordingTo = wtree.get_object('recordingTo')
        self.musicScale = wtree.get_object("musicScale")
        self.musicScale.connect("value-changed", self.onMusicScaleValue)
        self.ignoreScaleChanges = False
        # self.attachLog(wtree.get_object("lastLog"))

        # wtree.get_object("replayPanel").show() # demo only
        rp = wtree.get_object("replayVbox")
        self.replayViews = ReplayViews(rp)

        mainwin.show_all()
        vid3 = wtree.get_object("vid3")
        self.liveVideoXid = vid3.window.xid
        vid3.props.height_request = 240-70-50
        wtree.get_object("frame1").props.height_request = 277-70-50
        

        self.setInput('dv') # auto seems to not search for dv

        gobject.timeout_add(1000 // framerate, self.updateLoop)

    def attachLog(self, textBuffer):
        """write log lines to this gtk buffer"""
        class ToBuffer(logging.Handler):
            def emit(self, record):
                textBuffer.set_text(record.getMessage())

        h = ToBuffer()
        h.setLevel(logging.INFO)
        log.addHandler(h)

    def updateLoop(self):
        position = self.musicTime.getLatest()
        try:
            with gtk.gdk.lock:
                self.replayViews.update(position)
        except:
            traceback.print_exc()
        return True

    def getInputs(self):
        return ['auto', 'dv', 'video0']

    def setInput(self, name):
        sourcePipe = {
            "auto": "autovideosrc name=src1",
            "testpattern" : "videotestsrc name=src1",
            "dv": "dv1394src name=src1 ! dvdemux ! dvdec",
            "v4l": "v4l2src device=/dev/video0 name=src1 ! hqdn3d" ,
            }[name]

        cam = (sourcePipe + " ! "
              "videorate ! video/x-raw-yuv,framerate=%s/1 ! "
              "videoscale ! video/x-raw-yuv,width=320,height=240;video/x-raw-rgb,width=320,height=240 ! "
              "videocrop top=70 bottom=50 ! "
              "queue name=vid" % framerate)

        self.pipeline = gst.parse_launch(cam)

        def makeElem(t, n=None):
            e = gst.element_factory_make(t, n)
            self.pipeline.add(e)
            return e
        
        sink = makeElem("xvimagesink")
        def setRec(t):
            # if you're selecting the text while gtk is updating it,
            # you can get a crash in xcb_io
            if getattr(self, '_lastRecText', None) == t:
                return
            with gtk.gdk.lock:
                self.recordingTo.set_text(t)
            self._lastRecText = t
        recSink = VideoRecordSink(self.musicTime, setRec)
        self.pipeline.add(recSink)

        tee = makeElem("tee")
        
        caps = makeElem("capsfilter")
        caps.set_property('caps', gst.caps_from_string('video/x-raw-rgb'))

        gst.element_link_many(self.pipeline.get_by_name("vid"), tee, sink)
        gst.element_link_many(tee, makeElem("ffmpegcolorspace"), caps, recSink)
        sink.set_xwindow_id(self.liveVideoXid)
        self.pipeline.set_state(gst.STATE_PLAYING)        

    def on_liveVideoEnabled_toggled(self, widget):
        if widget.get_active():
            self.pipeline.set_state(gst.STATE_PLAYING)
            # this is an attempt to bring the dv1394 source back, but
            # it doesn't work right.
            self.pipeline.get_by_name("src1").seek_simple(
                gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, 0 * gst.SECOND)
        else:
            self.pipeline.set_state(gst.STATE_READY)
                                                   
    def on_liveFrameRate_value_changed(self, widget):
        print widget.get_value()

    def onMusicTimeChange(self, position):
        self.ignoreScaleChanges = True
        try:
            self.musicScale.set_range(0, position['duration'])
            self.musicScale.set_value(position['t'])
        finally:
            self.ignoreScaleChanges = False

    def onMusicScaleValue(self, scaleRange):
        """the scale position has changed. if it was by the user, send
        it back to music player"""
        if not self.ignoreScaleChanges:
            self.musicTime.sendTime(scaleRange.get_value())
