

from Timeline import *
from Submaster import Submasters, sub_maxes

class Show:
    def __init__(self, timelines, submasters):
        self.timelines = dict([(timeline.name, timeline)
            for timeline in timelines])
        self.submasters = submasters
        self.current_timeline = None
        self.current_time = 0
        try:
            self.current_timeline = timelines[0]
        except ValueError:
            pass
    def calc_active_submaster(self):
        "get levels from the current timeline at the current time"
        if not (self.current_timeline or self.current_time):
            return {}
        tl = self.current_timeline
        tl.set_time(self.current_time)
        levels = tl.get_levels()
        scaledsubs = [self.submasters.get_sub_by_name(sub) * level \
            for sub, level in levels.items()]
        maxes = sub_maxes(*scaledsubs)

        return maxes
    def set_timeline(self, name):
        "select a timeline"
        self.current_timeline = self.timelines.get(name)
        self.set_time(0)
        if not self.current_timeline:
            print "Show: '%s' is not the same of a timeline."
    def set_time(self, time):
        "set time of current timeline"
        self.current_time = time
        self.current_timeline.set_time(time)

# this is the default blender
linear = LinearBlender()
def T(time, level, **kw):
    """This used to be a synonym for TimedEvent:

    T = TimedEvent

    It now acts in a similar way, except that it will fill in a default 
    blender if you don't.  The default blender is a LinearBlender.  It also
    sets frame to MISSING so the track can fill it in."""
    if 'blender' not in kw:
        global linear
        kw['blender'] = linear

    return TimedEvent(time, level=level, frame=MISSING, **kw)

quad = ExponentialBlender(2)
invquad = ExponentialBlender(0.5)
smoove = SmoothBlender()

track1 = TimelineTrack('red track',
    T(0, 0),
    T(4, 0.5, blender=quad),
    T(12, 0.7, blender=smoove),
    T(15, level=0.0), default_frame='red')
track2 = TimelineTrack('green track',
    T(0, 0.2, blender=invquad),
    T(5, 1.0, blender=smoove),
    T(10, 0.8),
    T(15, 0.6),
    T(20, 0.0), default_frame='green')
track3 = TimelineTrack('tableau demo',
    T(0, 0.0),
    T(2, 1.0, blender=InstantEnd()),
    T(18, 1.0),
    T(20, 0.0), default_frame='blue')
track4 = TimelineTrack('MJ fader',
    T(0, 0.0),
    T(5, 1.0),
    T(10, 0.0), default_frame='red')
bump21 = TimelineTrack('bump at 21',
    T(0,    0),
    T(20.4, 0.05),
    T(20.7,   1),
    T(25,   0.4),
    T(31,   0),
    T(31.1, 1),
    
    default_frame='sill')

# tl = Timeline('test', [track1, track2, track3, track4])
tl = Timeline('test', [track4, bump21])

strobe1 = TimelineTrack('strobify', 
    T(0, 0, blender=Strobe(ontime=0.25, offtime=0.25)),
    T(200, 1), default_frame='sill')

strobe_tl = Timeline('strobe test', [strobe1])

show = Show([tl, strobe_tl], Submasters())

if __name__ == "__main__":
    show.set_timeline('test')
    show.set_time(4)
    print show.get_levels().get_levels()
    print
    print show.get_levels()
