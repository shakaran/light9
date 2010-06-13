import os, gtk
from bisect import bisect_left
from decimal import Decimal


def songDir(song):
    return "/tmp/vidref/play-%s" % song.split('://')[-1].replace('/','_')

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
        self.lastSong = None

        self.views = []
     
    def update(self, position):
        """
        freshen all replay windows. We get called this about every
        time there's a new live video frame.

        may be responsible for making new children if we change song
        """
        if position['song'] != self.lastSong:
            self.loadViewsForSong(position['song'])
            self.lastSong = position['song']
        for v in self.views:
            v.updatePic(position)


    def loadViewsForSong(self, song):
        # remove previous ones
        
        takes = os.listdir(songDir(song))
        for take in takes:
            td = takeDir(songDir(song), take)
            rv = ReplayView(self.parent, Replay(td))
            self.views.append(rv)

class ReplayView(object):
    """
    one of the replay widgets
    """
    def __init__(self, parent, replay):
        self.replay = replay

        # this *should* be a composite widget from glade
        img = gtk.Image()
        img.set_size_request(320, 240)
        parent.pack_end(img, False, False)
        img.show()
        self.picWidget = img
        
#        self.picWidget = parent.get_children()[0].get_child()
        
    def updatePic(self, position):
        inPic = self.replay.findClosestFrame(position['t']+.25)
        with gtk.gdk.lock:
            self.picWidget.set_from_file(inPic)
            if 0:
                # force redraw of that widget
                self.picWidget.queue_draw_area(0,0,320,240)
                self.picWidget.get_window().process_updates(True)
    
class Replay(object):
    """
    model for one of the replay widgets
    """
    def __init__(self, takeDir):
        self.takeDir = takeDir

    def findClosestFrame(self, t):
        existingFrames = sorted([Decimal(f.split('.jpg')[0])
                                 for f in os.listdir(self.takeDir)])
        i = bisect_left(existingFrames, Decimal(str(t)))
        if i >= len(existingFrames):
            i = len(existingFrames) - 1
        return os.path.join(self.takeDir, "%08.03f.jpg" % existingFrames[i])
