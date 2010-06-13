import os, gtk
from bisect import bisect_left
from decimal import Decimal

existingDir = "/tmp/vidref/play-_my_proj_light9_show_dance2010_music_01-chorusmix.wav-1276415052"
existingFrames = sorted([Decimal(f.split('.jpg')[0])
                         for f in os.listdir(existingDir)])


class ReplayViews(object):
    """
    the whole list of replay windows. parent is the scrolling area for
    these windows to be added
    """
    def __init__(self, parent):
        self.out = ReplayView(parent, Replay(existingDir))
        return
        for x in range(1000):
            lab = gtk.Label()
            lab.set_text("hello")
            parent.add_with_viewport(lab)
    
    def update(self, position):
        """
        freshen all replay windows. We get called this about every
        time there's a new live video frame.

        may be responsible for making new children if we change song
        """
        self.out.updatePic(position)

class Replay(object):
    """
    model for one of the replay widgets
    """
    def __init__(self, sourceDir):
        self.sourceDir = sourceDir

    def findClosestFrame(self, t):
        i = bisect_left(existingFrames, Decimal(str(t)))
        if i >= len(existingFrames):
            i = len(existingFrames) - 1
        return os.path.join(existingDir, "%08.03f.jpg" % existingFrames[i])

class ReplayView(object):
    """
    one of the replay widgets
    """
    def __init__(self, parent, replay):
        self.replay = replay
#        self.loadWindwos
        self.picWidget = parent
        
    def updatePic(self, position):
        inPic = self.replay.findClosestFrame(position['t']+.25)
        with gtk.gdk.lock:
            self.picWidget.set_from_file(inPic)
            if 0:
                # force redraw of that widget
                self.picWidget.queue_draw_area(0,0,320,240)
                self.picWidget.get_window().process_updates(True)
    
