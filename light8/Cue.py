"""And that's my cue to exit(0)..."""
from time import time
from util import subsetdict, scaledict

class Cue:
    """Cues are groups of fades.  They can tell you the current levels at a 
    given time.  They contain Fades, which are actually children of Cue,
    meaning that Cues can contain Cues.  This is similar to the Light9 concept
    of Cues and Fades, but without all the Nodes."""
    def __init__(self, name, starttime, dur, *fades):
        'Create a cue'

        endtime = starttime + dur
        dur = endtime - starttime

        self.name = name
        self.starttime = starttime
        self.dur = dur
        self.endtime = endtime
        self.fades = fades
        self.cuestart = None
        self.init_levels = None
    def channels_involved(self):
        'Return which channels are involved.  This is important for marking.'
        c = {}
        for fade in self.fades:
            for f_chan in fade.channels_involved():
                c[f_chan] = 1
        return c.keys()
    def start(self, levels, time):
        'Mark the beginning of a cue'
        # print "cue marked with", levels
        self.init_levels = levels
        self.init_time = time

        for fade in self.fades:
            subdict = subsetdict(levels, fade.channels_involved())
            fade.start(subdict, time)
    def get_levels(self, curtime):
        'Returns the current levels'
        d = {}
        for fade in self.fades:
            fade_d = fade.get_levels(curtime)
            for ch, lev in fade_d.items():
                d[ch] = max(lev, d.get(ch, 0))
        return d
    def get_end_levels(self):
        'Returns the final levels'
        d = {}
        for fade in self.fades:
            fade_d = fade.get_end_levels()
            for ch, lev in fade_d.items():
                d[ch] = max(lev, d.get(ch, 0))
        return d

class Fade(Cue):
    'See Cue.__doc__'
    def __init__(self, channel, starttime, dur=None, endlevel=0, param=None):
        'Fades are simple Cues'
        Cue.__init__(self, "%s -> %.1f" % (channel, endlevel), starttime, dur)
        self.channel = channel
        self.endlevel = endlevel
        self.dur = dur
        self.param = param
    def start(self, levels, time):
        'Mark the beginning of the fade'
        # print "fade", self.name, "marked with", levels
        self.init_levels = levels
        self.init_level = levels[self.channel]
        self.init_time = time
    def channels_involved(self):
        'Speaks for itself, I hope'
        return [self.channel]
    def get_levels(self, curtime):
        elapsed = curtime - self.init_time
        if elapsed <= self.starttime:
            return self.init_levels
        elif elapsed >= self.endtime:
            return {self.channel : self.endlevel}
        else:
            percent = float((curtime - self.init_time) - self.starttime) / \
                        self.dur
            return {self.channel : self.init_level + 
                percent * (self.endlevel - self.init_level)}
    def get_end_levels(self):
        return {self.channel : self.endlevel}

class SimpleCue(Cue):
    'See Cue.__doc__'
    def __init__(self, name, target, dur, **info):
        Cue.__init__(self, name, 0, dur)
        self.target = target
        self.dur = dur
        self.info = info
    def start(self, levels, time):
        'Mark the beginning of the fade'
        self.init_levels = levels
        self.init_time = time
    def channels_involved(self):
        'Speaks for itself, I hope'
        return self.target.keys()
    def get_levels(self, curtime):
        elapsed = curtime - self.init_time
        if elapsed >= self.endtime:
            return self.target
        else:
            percent = float((curtime - self.init_time) - self.starttime) / \
                        self.dur
            return dict([(n, self.init_levels[n] + 
                percent * (lev - self.init_levels[n]))
                    for n, lev in self.target])
            # return {self.channel : self.init_level + 
                # percent * (self.endlevel - self.init_level)}
    def get_end_levels(self):
        return self.target

if __name__ == '__main__':
    f1 = Fade('red', 0, 2, 100)
    f2 = Fade('green', 1, 3, 50)
    f3 = Fade('blue', 0, 4, 0)
    f4 = Fade('clear', 0, 8, 75) 
    c = Cue("Color shift", 0, 10, f1, f2, f3, f4)
    tstart = time()
    # note how green is not mentioned -- it goes to 0
    c.start({'red' : 0, 'blue' : 100, 'clear' : 25}, tstart)
    while time() - tstart < 15:
        curtime = time()
        levs = c.get_levels(curtime)
        s = '\t'.join(["%s: %d" % (k[0], v) for k, v, in levs.items()])
        print "%.1f" % (curtime - tstart), s
