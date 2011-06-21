#!/usr/bin/python

"""
alternate to the mpd music player, for ascoltami
"""
from __future__ import division
import time, logging, traceback
import gst, gobject
log = logging.getLogger()

class Player(object):
    def __init__(self, autoStopOffset=4, onEOS=None):
        """autoStopOffset is the number of seconds before the end of
        song before automatically stopping (which is really pausing).
        onEOS is an optional function to be called when we reach the
        end of a stream (for example, can be used to advance the song).
        It is called with one argument which is the URI of the song that
        just finished."""
        self.autoStopOffset = autoStopOffset
        self.playbin = self.pipeline = gst.parse_launch("playbin2")
        self.playStartTime = 0
        self.lastWatchTime = 0
        self.autoStopTime = 0
        self.onEOS = onEOS
        
        # before playbin2:
        #self.pipeline = gst.parse_launch("filesrc name=file location=%s ! wavparse name=src ! audioconvert ! alsasink name=out" % songFile)

        gobject.timeout_add(50, self.watchTime)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()

        def on_any(bus, msg):
            print bus, msg, msg.type
            if msg.type == gst.MESSAGE_EOS:
                if self.onEOS is not None:
                    self.onEOS(self.getSong())
        bus.connect('message', on_any)

        def onStreamStatus(bus, message):
            print "streamstatus", bus, message
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

                # new EOS logic above should be better
            ## if not self.onEOS:
            ##     if self.isPlaying() and t >= self.duration() - .2:
            ##         # i don't expect to hit dur exactly with this
            ##         # polling. What would be better would be to watch for
            ##         # the EOS signal and react to that
            ##         self.onEOS(self.getSong())

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

    def setSong(self, songLoc, play=True):
        """
        uri like file:///my/proj/light9/show/dance2010/music/07.wav
        """
        log.info("set song to %r" % songLoc)
        self.pipeline.set_state(gst.STATE_READY)
        self.preload(songLoc)
        self.pipeline.set_property("uri", songLoc)
        # todo: don't have any error report yet if the uri can't be read
        if play:
            self.pipeline.set_state(gst.STATE_PLAYING)
            self.playStartTime = time.time()

    def getSong(self):
        """Returns the URI of the current song."""
        return self.playbin.get_property("uri")

    def preload(self, songPath):
        """
        to avoid disk seek stutters, which happened sometimes (in 2007) with the
        non-gst version of this program, we read the whole file to get
        more OS caching.

        i don't care that it's blocking.
        """
        log.info("preloading %s", songPath)
        assert songPath.startswith("file://"), songPath
        open(songPath[len("file://"):]).read()

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

    def states(self):
        """json-friendly object describing the interesting states of
        the player nodes"""
        success, state, pending = self.playbin.get_state(timeout=0)
        return {"current": {"name":state.value_nick},
                "pending": {"name":state.value_nick}}
        
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
