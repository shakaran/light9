from Timeline import *
from Submaster import Submasters, sub_maxes

class Show:
    def __init__(self, timelines, submasters):
        self.timelines = dict([(timeline.name, timeline)
            for timeline in timelines])
        self.submasters = submasters
        self.current_timeline = None
        self.current_time = 0
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
        if not self.current_timeline:
            print "Show: '%s' is not the name of a timeline." % name
        else:
            self.set_time(0)
    def set_time(self, time):
        "set time of current timeline"
        self.current_time = time
        if not self.current_timeline:
            return
        self.current_timeline.set_time(time)
    def get_timelines(self):
        "Get names of all timelines"
        return self.timelines.keys()

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

def translate_tracks_from_file(timelinename):
    try:
        f = open('timelines/' + timelinename)
    except IOError:
        return []

    events = {}
    current_sub = None
    current_time = None
    lines = f.readlines()
    alltext = ' '.join(lines)

    for token in alltext.split():
        # print 't', token
        if token.endswith(':'):
            # print 'sub'
            current_sub = token[:-1]
            current_time = None
        else:
            if not current_sub:
                raise "invalid file format", line
            if current_time is not None: # we now have a level
                # print 'level'
                try:
                    level = float(token)
                except:
                    print "bad level token", token
                    level = 0
                # time to write
                events.setdefault(current_sub, [])
                events[current_sub].append((current_time, level))
                current_time = None
            else:
                # print 'time'
                try:
                    current_time = float(token)
                except ValueError:
                    print "bad time token", token
                    current_time = 0

    tracks = []
    for sub, timelevels in events.items():
        tracks.append(TimelineTrack(sub, default_frame=sub,
            *[T(time, level) for time, level in timelevels]))

    return tracks

