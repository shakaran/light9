#!/usr/bin/python

"""
alternate to the mpd music player, for ascoltami
"""
from __future__ import division
import time, logging, traceback
import gst, gobject
log = logging.getLogger()

class Player(object):
    def __init__(self, autoStopOffset=4):
        self.autoStopOffset = autoStopOffset
        self.playbin = self.pipeline = gst.parse_launch("playbin2")
        self.playStartTime = 0
        self.lastWatchTime = 0
        self.autoStopTime = 0

        # before playbin2:
        #self.pipeline = gst.parse_launch("filesrc name=file location=%s ! wavparse name=src ! audioconvert ! alsasink name=out" % songFile)

        gobject.timeout_add(50, self.watchTime)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()

        def on_any(bus, msg):
            print bus, msg
        #bus.connect('message', on_any)

        def onStreamStatus(bus, message):
            (statusType, _elem) = message.parse_stream_status()
            if statusType == gst.STREAM_STATUS_TYPE_ENTER:
                self.setupAutostop()
        bus.connect('message::stream-status', onStreamStatus)

    def watchTime(self):
        try:
            try:
                t = self.currentTime()
            except gst.QueryError:
                return True
            log.debug("watch %s < %s < %s",
                      self.lastWatchTime, self.autoStopTime, t)
            if self.lastWatchTime < self.autoStopTime < t:
                log.info("autostop")
                self.pause()
            self.lastWatchTime = t
        except:
            traceback.print_exc()
        return True

    def seek(self, t):
        assert self.playbin.seek_simple(
            gst.FORMAT_TIME,
            gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE | gst.SEEK_FLAG_SKIP,
            t * gst.SECOND)
        self.playStartTime = time.time()

    def setSong(self, songUri):
        """
        uri like file:///my/proj/light9/show/dance2010/music/07.wav
        """
        log.info("set song to %r" % songUri)
        self.pipeline.set_state(gst.STATE_READY)
        self.pipeline.set_property("uri", songUri)
        self.pipeline.set_state(gst.STATE_PLAYING)
        self.playStartTime = time.time()

    def currentTime(self):
        try:
            cur, _format = self.playbin.query_position(gst.FORMAT_TIME)
        except gst.QueryError:
            return 0
        return cur / gst.SECOND

    def duration(self):
        try:
            return self.playbin.query_duration(gst.FORMAT_TIME)[0] / gst.SECOND
        except gst.QueryError:
            return 0
        
    def pause(self):
        self.pipeline.set_state(gst.STATE_PAUSED)

    def resume(self):
        self.pipeline.set_state(gst.STATE_PLAYING)
        pos = self.currentTime()
        autoStop = self.duration() - self.autoStopOffset
        if abs(pos - autoStop) < .01:
            self.releaseAutostop()

    def setupAutostop(self):
        dur = self.duration()
        self.autoStopTime = (dur - self.autoStopOffset)
        log.info("autostop will be at %s", self.autoStopTime)
        # pipeline.seek can take a stop time, but using that wasn't
        # working out well. I'd get pauses at other times that were
        # hard to remove.

    def isPlaying(self):
        _, state, _ = self.pipeline.get_state()
        return state == gst.STATE_PLAYING
                  
                           
        
