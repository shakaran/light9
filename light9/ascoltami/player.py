#!/usr/bin/python

"""
alternate to the mpd music player, for ascoltami
"""
from __future__ import division
import time, logging
import gst
log = logging.getLogger()

class Player(object):
    def __init__(self):

        self.playbin = self.pipeline = gst.parse_launch("playbin2 name=b")
        self.playStartTime = 0
        self._duration = 0
        self.pauseTime = 0

        self.setSong("file:///my/proj/light9/show/dance2010/music/07-jacksonmix-complete.wav")
        
        #self.pipeline = gst.parse_launch("filesrc name=file location=%s ! wavparse name=src ! audioconvert ! alsasink name=out" % songFile)

        def on_any(bus, msg):
            print bus, msg

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        #bus.connect('message', on_any)

        def onStreamStatus(bus, message):
            (statusType, _elem) = message.parse_stream_status()
            if statusType == gst.STREAM_STATUS_TYPE_ENTER:
                self.setupAutostop()

            # we should run our own poller looking for crosses over the autostop threshold and pausing. When i used the pipeline.seek end-time, it caused lots of unwanted other pausing and was hard to turn off.
                
            #print message, bus
        bus.connect('message::stream-status', onStreamStatus)

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



#        GST_MESSAGE_DURATION
        

    def currentTime(self):
        cur, _format = self.playbin.query_position(gst.FORMAT_TIME)
        return cur / gst.SECOND

    def duration(self):
        return self.playbin.query_duration(gst.FORMAT_TIME)[0] / gst.SECOND
        
    def pause(self):
        self.pipeline.set_state(gst.STATE_PAUSED)

    def resume(self):
        self.pipeline.set_state(gst.STATE_PLAYING)
        pos = self.currentTime()
        autoStop = self.duration() - 10
        if abs(pos - autoStop) < .01:
            self.releaseAutostop()


    def setupAutostop(self):
        return
        dur = self.duration()
        autoStop = (dur - 10.0)
        log.info("autostop will be at %s", autoStop)
        print "seek", self.pipeline.seek(1.0, gst.FORMAT_TIME,
                           gst.SEEK_FLAG_ACCURATE,
                           gst.SEEK_TYPE_NONE, 0,
                           gst.SEEK_TYPE_SET, autoStop * gst.SECOND)

    def releaseAutostop(self):
        log.info("release autostop")
        
        print "seek", self.pipeline.seek(
            1.0, gst.FORMAT_TIME,
            gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE | gst.SEEK_FLAG_SKIP,
            gst.SEEK_TYPE_NONE, 0,
            gst.SEEK_TYPE_END, 0)
        print self.pipeline.get_state()
        self.pipeline.set_state(gst.STATE_PLAYING)

                           
                           
        
