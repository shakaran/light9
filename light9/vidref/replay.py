from __future__ import division
import os, gtk, shutil, logging, time
from bisect import bisect_left
from decimal import Decimal
log = logging.getLogger()

framerate = 15

def songDir(song):
    safeUri = song.split('://')[-1].replace('/','_')
    return os.path.expanduser("~/light9-vidref/play-%s" % safeUri)

def takeDir(songDir, startTime):
    """
    startTime: unix seconds (str ok)
    """
    return os.path.join(songDir, str(int(startTime)))

class ReplayViews(object):
    """
    the whole list of replay windows. parent is the scrolling area for
    these windows to be added
    """
    def __init__(self, parent):
        # today, parent is the vbox the replay windows should appear in
        self.parent = parent
        self.lastStart = None

        self.views = []
     
    def update(self, position):
        """
        freshen all replay windows. We get called this about every
        time there's a new live video frame.

        Calls loadViewsForSong if we change songs, or even if we just
        restart the playback of the current song (since there could be
        a new replay view)
        """
        t1 = time.time()
        if position.get('started') != self.lastStart and position['song']:
            self.loadViewsForSong(position['song'])
            self.lastStart = position['started']
        for v in self.views:
            v.updatePic(position)
        log.debug("update %s views in %.2fms",
                  len(self.views), (time.time() - t1) * 1000)

    def loadViewsForSong(self, song):
        """
        replace previous views, and cleanup short ones
        """
        for v in self.views:
            v.destroy()
        self.views[:] = []

        d = songDir(song)
        try:
            takes = sorted(t for t in os.listdir(d) if t.isdigit())
        except OSError:
            return
        
        for take in takes:
            td = takeDir(songDir(song), take)
            r = Replay(td)
            if r.tooShort():
                log.warn("cleaning up %s; too short" % r.takeDir)
                r.deleteDir()
                continue
            rv = ReplayView(self.parent, r)
            self.views.append(rv)

class ReplayView(object):
    """
    one of the replay widgets
    """
    def __init__(self, parent, replay):
        self.replay = replay
        self.enabled = True
        self.showingPic = None

        # this *should* be a composite widget from glade

        delImage = gtk.Image()
        delImage.set_visible(True)
        delImage.set_from_stock("gtk-delete", gtk.ICON_SIZE_BUTTON)

        def withLabel(cls, label):
            x = cls()
            x.set_visible(True)
            x.set_label(label)
            return x

        def labeledProperty(key, value, width=12):
            lab = withLabel(gtk.Label, key)

            ent = gtk.Entry()
            ent.set_visible(True)
            ent.props.editable = False
            ent.props.width_chars = width
            ent.props.text = value

            cols = gtk.HBox()
            cols.set_visible(True)
            cols.add(lab)
            cols.add(ent)
            return cols

        replayPanel = gtk.HBox()
        replayPanel.set_visible(True)
        if True:
            af = gtk.AspectFrame()
            af.set_visible(True)
            af.set_size_request(320, 240-70-50)
            af.set_shadow_type(gtk.SHADOW_OUT)
            af.props.obey_child = True

            img = gtk.Image()
            img.set_visible(True)
            img.set_size_request(320, 240-70-50)
            self.picWidget = img

            af.add(img)
            replayPanel.pack_start(af, False, False, 0)

        if True:
            rows = []
            rows.append(labeledProperty("Started:", self.replay.getTitle()))
            rows.append(labeledProperty("Seconds:", self.replay.getDuration()))
            if True:
                en = withLabel(gtk.ToggleButton, "Enabled")
                en.set_active(True)
                def tog(w):
                    self.enabled = w.get_active()
                en.connect("toggled", tog)
                rows.append(en)
            if True:
                d = withLabel(gtk.Button, "Delete")
                d.props.image = delImage
                def onClicked(w):
                    self.replay.deleteDir()
                    self.destroy()
                d.connect("clicked", onClicked)
                rows.append(d)
            if True:
                pin = withLabel(gtk.CheckButton, "Pin to top")
                pin.props.draw_indicator = True
                rows.append(pin)

            stack = gtk.VBox()
            stack.set_visible(True)
            for r in rows:
                stack.add(r)
                stack.set_child_packing(r, False, False, 0, gtk.PACK_START)
            
            replayPanel.pack_start(stack, False, False, 0)

        parent.pack_start(replayPanel, False, False)
        self.replayPanel = replayPanel

    def destroy(self):
        self.replayPanel.destroy()
        self.enabled = False
        
    def updatePic(self, position, lag=.2):

        # this should skip updating off-screen widgets! maybe that is
        # done by declaring the widget dirty and then reacting to a
        # paint message if one comes

        if not self.enabled:
            return
        
        inPic = self.replay.findClosestFrame(position['t'] + lag)

        if inPic == self.showingPic:
            return
        with gtk.gdk.lock:
            self.picWidget.set_from_file(inPic)
            if 0:
                # force redraw of that widget
                self.picWidget.queue_draw_area(0,0,320,240)
                self.picWidget.get_window().process_updates(True)
        self.showingPic = inPic

_existingFrames = {}  # takeDir : frames
    
class Replay(object):
    """
    model for one of the replay widgets
    """
    def __init__(self, takeDir):
        self.takeDir = takeDir
        try:
            self.existingFrames = _existingFrames[self.takeDir]
        except KeyError:
            log.info("scanning %s", self.takeDir)
            self.existingFrames = sorted([Decimal(f.split('.jpg')[0])
                                          for f in os.listdir(self.takeDir)])
            if not self.existingFrames:
                raise NotImplementedError("suspiciously found no frames in dir %s" % self.takeDir)
            _existingFrames[self.takeDir] = self.existingFrames

    def tooShort(self, minSeconds=5):
        return len(self.existingFrames) < (minSeconds * framerate)

    def deleteDir(self):
        shutil.rmtree(self.takeDir)

    def getTitle(self):
        tm = time.localtime(int(os.path.basename(self.takeDir)))
        return time.strftime("%a %H:%M:%S", tm)

    def getDuration(self):
        """total number of seconds represented, which is most probably
        a continuous section, but we aren't saying where in the song
        that is"""
        return "%.1f" % (len(self.existingFrames) / framerate)

    def findClosestFrame(self, t):
        # this is weird to be snapping our playback time to the frames
        # on disk. More efficient and accurate would be to schedule
        # the disk frames to playback exactly as fast as they want
        # to. This might spread cpu load since the recorded streams
        # might be a little more out of phase. It would also
        # accomodate changes in framerate between playback streams.
        i = bisect_left(self.existingFrames, Decimal(str(t)))
        if i >= len(self.existingFrames):
            i = len(self.existingFrames) - 1
        return os.path.join(self.takeDir, "%08.03f.jpg" %
                            self.existingFrames[i])
