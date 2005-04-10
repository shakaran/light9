from Timeline import *
<<<<<<< TheShow.py
from Submaster import Submasters
from Show import *
=======
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
>>>>>>> 1.2

quad = ExponentialBlender(2)
invquad = ExponentialBlender(0.5)
smoove = SmoothBlender()
strobe = Strobe(ontime=0.25, offtime=0.25)
lightningstrobe = Strobe(ontime=0.1, offtime=0.15, onlevel=1, offlevel=0.02)
changeatend = InstantEnd()
changeatstart = InstantStart()
sine_7s = Sine(7)
sine_5s = Sine(5)
randomstrobe = RandomStrobe(1000, 0.1, 1)

def make_lighting_track(ltime, sub='upfill'):
    ltime -= 0.1
    return TimelineTrack('lightning',
        T(ltime - 1.6, 0, blender=changeatend),
        T(ltime - 1.5, 1, blender=lightningstrobe),
        T(ltime - 0.5, 0),
        default_frame=sub)

# 01 207.046
song01 = Timeline('song01', [
    TimelineTrack('main fade',
        T(0,       0),
        T(2,       1),
        T(207.046, 1),
        T(217,     1), 
        T(222,     0),
        default_frame='song01'),
    TimelineTrack('frontwhite',
        T(-2,      0),
        T(0,       0),
        T(200.046, 0),
        T(204,     1), 
        T(217,     1), 
        T(222,     0),
        default_frame='frontwhite')
    ])

# 02 151.327
song02 = Timeline('song02', translate_tracks_from_file('song02'))

# 03 152.946
song03 = Timeline('song03', translate_tracks_from_file('song03'))

# 04 255.529
song04 = Timeline('song04', [
    TimelineTrack('main fade',
        T(-2,      0),
        T(8,       1),
        T(255.529, 1),
        T(265,     1), 
        T(270,     0),
        default_frame='song04'),
    TimelineTrack('frontwhite',
        T(244,     0),
        T(248,     1), 
        T(265.5,   1), 
        T(270.5,   0),
        default_frame='frontwhite'),
    ])

# 05 241.162
song05 = Timeline('song05', [
    # TimelineTrack('main fade',
        # T(-2,      0),
        # T(0,       1),
        # T(241.162, 1),
        # T(251,     1), 
        # T(256,     0),
        # default_frame='song05'),
    ])
# 226-230   DELETED!!!!!

# 06 145.005
song06 = Timeline('song06', translate_tracks_from_file('song06'))

# 07 461.923
# song07main = TimelineTrack('main fade',
    # T(-2,      0),
    # T(0,       0.6),
    # T(461.923, 0.6),
    # T(471,     1), 
    # T(476,     0),
    # default_frame='song07')

song07 = Timeline('song07', translate_tracks_from_file('song07'))

# 08 200.097
#song08main = TimelineTrack('main fade',
    #T(-2,      0),
    #T(0,       0.6),
    #T(200.097, 0.6),
    ##T(210,     1), 
    #T(215,     0),
    #default_frame='song08')

# song08 = Timeline('song08', 
    # [song08main,
     # translate_tracks_from_file('song08')])
song08 = Timeline('song08', [])

song09 = Timeline('song09', translate_tracks_from_file('song09'))
song10 = Timeline('song10', translate_tracks_from_file('song10'))
song11 = Timeline('song11', translate_tracks_from_file('song11'))
song12 = Timeline('song12', translate_tracks_from_file('song12'))
song13 = Timeline('song13', translate_tracks_from_file('song13'))
song14 = Timeline('song14', translate_tracks_from_file('song14'))
song15 = Timeline('song15', translate_tracks_from_file('song15'))
song16 = Timeline('song16', translate_tracks_from_file('song16'))

flashstart = 184
flashend = 204

song17 = Timeline('song17', translate_tracks_from_file('song17') +
    [
        TimelineTrack('kicking flashes',
            T(flashstart, 0, blender=RandomStrobe()),
            T(flashend, 0), default_frame='red'),
        TimelineTrack('kicking flashes',
            T(flashstart, 0, blender=RandomStrobe()),
            T(flashend, 0), default_frame='frontwhite')
    ])

song18 = Timeline('song18', [])
    # translate_tracks_from_file('song18') + [
       # make_lighting_track(12),
    # ])

# 19 324.675
song19  = Timeline('song19', [
    # TimelineTrack('main fade',
        # T(-2,      0),
        # T(0,       1),
        # T(324.675, 1),
        # T(334,     1), 
        # T(339,     0),
        # default_frame='song19'),
    TimelineTrack('bl',
        T(-0.01,   0),
        T(0,       1),
        T(80,      1),
        T(80.01,   0), 
        T(300,     0), 
        T(300.01,  1), 
        T(333,     1), 
        T(333.01,  0), 
        default_frame='blacklight'),
    TimelineTrack('sill',
        T(-0.01,   0),
        T(0,       0.4),
        T(74,      0.4),
        T(76,      0), 
        T(197,     0), 
        T(197.01,  1), 
        T(201,     1), 
        T(202,     0), 
        default_frame='sill'),
    TimelineTrack('frontwhite',
        T(0,       0),
        T(46,      0),
        T(50,      0.35),
        T(74,      0.35),
        T(76,      0), 
        T(79,      0), 
        T(82,      0.5), 
        T(152,     0.5),
        T(154,     0.7, blender=changeatend),
        T(197,     0), 
        T(200,     0),
        T(202,     0.6),
        T(263,     0.6),
        T(265,     0.8),
        T(324,     0.8),
        T(328,     1.0),
        T(334.7,   1.0),
        T(339.7,   0.0),
        default_frame='frontwhite'),
    TimelineTrack('house',
        T(0,       0),
        T(263,     0),
        T(273,     0.5), 
        T(320,     0.5),
        T(325,     0),
        default_frame='house'),
    TimelineTrack('fx blue',
        T(-2,      0),
        T(0,       0.5),
        T(50,      0.5),
        T(70,      0),
        default_frame='blue'),
    make_lighting_track(5),
    make_lighting_track(20),
    make_lighting_track(26),
    make_lighting_track(31),
    make_lighting_track(36),
    # make_lighting_track(75),  # problems
    make_lighting_track(88),
    make_lighting_track(92),
    # make_lighting_track(136), # problems
    make_lighting_track(140.511),
    make_lighting_track(168.568),
    make_lighting_track(176.875),
    make_lighting_track(219.219),
    make_lighting_track(265.169),
    make_lighting_track(268.277),
    make_lighting_track(271.987),
    make_lighting_track(275.566),
    make_lighting_track(279.066),
    make_lighting_track(282.54),
    make_lighting_track(286.145),
    make_lighting_track(293.721),
    make_lighting_track(300.408),
    make_lighting_track(303.987),

    ])

randomstrobetest = Timeline('strobing', [
    TimelineTrack('whatever1',
        T(0, 1, blender=RandomStrobe()),
        T(600, 1), default_frame='red'),
    TimelineTrack('whatever2',
        T(0, 1, blender=RandomStrobe()),
        T(600, 1), default_frame='blue'),
    TimelineTrack('whatever3',
        T(0, 1, blender=RandomStrobe()),
        T(600, 1), default_frame='green')
    ])

show = Show([
    song01,
    song02,
    song03,
    song04,
    song05,
    song06,
    song07,
    song08,
    song09,
    song10,
    song11,
    song12,
    song13,
    song14,
    song15,
    song16,
    song17,
    song18,
    song19, 
    randomstrobetest,
], Submasters())
