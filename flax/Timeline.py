from TLUtility import make_attributes_from_args, dict_scale, dict_max, \
    DummyClass, last_less_than, first_greater_than
from time import time
from __future__ import division # "I'm sending you back to future!"

"""
Changelog:
Fri May 16 15:17:34 PDT 2003
    Project started (roughly).

Mon May 19 17:56:24 PDT 2003
    Timeline is more or less working.  Still bugs with skipping
    FunctionFrames at random times.

Timeline idea
=============
 time    | 0   1   2   3   4   5   6
---------+-----------------------------
frame    | F       F           F
blenders |  \  b /  \- b ----/

Update: this is more or less what happened.  However, there are 
TimelineTracks as well.  FunctionFrames go on their own track.
LevelFrames must have unique times, FunctionFrames do not.

Level propagation
=================
Cue1 is a CueNode.  CueNodes consist of a timeline with any number
of LevelFrame nodes and LinearBlenders connecting all the frames.
At time 0, Cue1's timeline has LevelFrame1.  At time 5, the timeline
has NodeFrame1.  NodeFrame1 points to Node1, which has it's own sets
of levels.  It could be a Cue, for all Cue1 cares.  No matter what,
we always get down to LevelFrames holding the levels at the bottom,
then getting combined by Blenders.

             /------\
             | Cue1 |                                       
             |---------------\
             |  Timeline:    |                                     
             |  0   ... 5    |                                     
     /--------- LF1     NF1 -------\                               
     |       |   \      /    |     |                          
     |       | LinearBlender |     |                                 
     |       \---------------/     |                        
     |                          points to                  
   /---------------\            a port in Cue1,
   | blueleft : 20 |            which connects to a Node
   | redwash  : 12 |                                                       
   |   .           |                                        
   |   :           |    
   |               |
   \---------------/
                                                            
PS. blueleft and redwash are other nodes at the bottom of the tree.
The include their real channel number for the DimmerNode to process.

When Cue1 requests levels, the timeline looks at the current position.
If it is directly over a Frame (or Frames), that frame is handled.
If it is LevelFrame, those are the levels that it returns.  If there is
a FunctionFrame, that function is activated.  Thus, the order of Frames
at a specific time is very significant, since the FunctionFrame could
set the time to 5s in the future.  If we are not currently over any 
LevelFrames, we call upon a Blender to determine the value between.
Say that we are at 2.3s.  We use the LinearBlender with 2.3/5.0s = 0.46%
and it determines that the levels are 1 - 0.46% = 0.54% of LF1 and
0.46% of NF1.  NF1 asks Node9 for its levels and this process starts
all over.

Graph theory issues (node related issues, should be moved elsewhere)
====================================================================
1.  We need to determine dependencies for updating (topological order).
2.  We need to do cyclicity tests.

Guess who wishes they had brought their theory book home?
I think we can do both with augmented DFS.  An incremental version of both
would be very nice, though hopefully unnecessary.

"""

class InvalidFrameOperation(Exception):
    """You get these when you try to perform some operation on a frame
    that doesn't make sense.  The interface is advised to tell the user,
    and indicate that a Blender or FunctionFramea should be disconnected
    or fixed."""
    pass

class MissingBlender(Exception):
    """Raised when a TimedEvent is missing a blender."""
    def __init__(self, timedevent):
        make_attributes_from_args('timedevent')
        Exception.__init__(self, "%r is missing a blender." % \
            self.timedevent)

# these are chosen so we can multiply by -1 to reverse the direction,
# and multiply direction by the time difference to determine new times.
FORWARD = 1
BACKWARD = -1

class Frame:
    """Frame is an event that happens at a specific time.  There are two
    types of frames: LevelFrames and FunctionFrames.  LevelFrames provide
    levels via their get_levels() function.  FunctionFrames alter the 
    timeline (e.g. bouncing, looping, speed changes, etc.).  They call
    __call__'ed instead."""
    def __init__(self, name):
        self.name = name
        self.timeline = DummyClass(use_warnings=0, raise_exceptions=0)
    def set_timeline(self, timeline):
        """Tell the Frame who the controlling Timeline is"""
        self.timeline = timeline
    def __mul__(self, percent):
        """Generate a new Frame by multiplying the 'effect' of this frame by
        a percent."""
        raise InvalidFrameOperation, "Can't use multiply this Frame"
    def __add__(self, otherframe):
        """Combines this frame with another frame, generating a new one."""
        raise InvalidFrameOperation, "Can't use add on this Frame"

class LevelFrame(Frame):
    """LevelFrames provide levels.  They can also be combined with other
    LevelFrames."""
    def __init__(self, name, levels):
        Frame.__init__(self, name)
        self.levels = levels
    def __mul__(self, percent):
        """Returns a new LevelFrame made by multiplying all levels by a 
        percentage.  Percent is a float greater than 0.0"""
        newlevels = dict_scale(self.get_levels(), percent)
        return LevelFrame('(%s * %f)' % (self.name, percent), newlevels)
    def __add__(self, otherframe):
        """Combines this LevelFrame with another LevelFrame, generating a new 
        one.  Values are max() together."""
        theselevels, otherlevels = self.get_levels(), otherframe.get_levels()
        return LevelFrame('(%s + %s)' % (self.name, otherframe.name),
                          dict_max(theselevels, otherlevels))
    def get_levels(self):
        """This function returns the levels held by this frame."""
        return self.levels
    def __repr__(self):
        return "<%s %r %r>" % (str(self.__class__), self.name, self.levels)

class EmptyFrame(LevelFrame):
    """An empty LevelFrame, for the purposes of extending the timeline."""
    def __init__(self, name='Empty Frame'):
        EmptyFrame.__init__(self, name, {})

class NodeFrame(LevelFrame):
    """A LevelFrame that gets its levels from another Node.  This must be
    used from a Timeline that is enclosed in TimelineNode.  Node is a string
    describing the node requested."""
    def __init__(self, name, node):
        LevelFrame.__init__(self, name, {})
        self.node = node
    def get_levels(self):
        """Ask the node that we point to for its levels"""
        node = self.timeline.get_node(self.node)
        self.levels = node.get_levels()
        return self.levels

class FunctionFrame(Frame):
    def __init__(self, name):
        Frame.__init__(self, name)
    def __call__(self, timeline, timedevent, node):
        """Called when the FunctionFrame is activated.  It is given a pointer
        to it's master timeline, the TimedEvent containing it, and Node that
        the timeline is contained in, if available."""
        pass

# this is kinda broken
class BounceFunction(FunctionFrame):
    def __call__(self, timeline, timedevent, node):
        """Reverses the direction of play."""
        timeline.reverse_direction()
        print "boing! new dir:", timeline.direction

# this too
class LoopFunction(FunctionFrame):
    def __call__(self, timeline, timedevent, node):
        timeline.set_time(0)
        print 'looped!'

class DoubleTimeFunction(FunctionFrame):
    def __call__(self, timeline, timedevent, node):
        timeline.set_rate(2 * timeline.rate)

class HalfTimeFunction(FunctionFrame):
    def __call__(self, timeline, timedevent, node):
        timeline.set_rate(0.5 * timeline.rate)

class TimedEvent:
    """Container for a Frame which includes a time that it occurs at,
    and which blender occurs after it."""
    def __init__(self, time, frame, blender=None):
        make_attributes_from_args('time', 'frame')
        self.next_blender = blender
    def __float__(self):
        return self.time
    def __cmp__(self, other):
        if type(other) in (float, int):
            return cmp(self.time, other)
        else:
            return cmp(self.time, other.time)
    def __repr__(self):
        return "<TimedEvent %s at %.2f, next blender=%s>" % \
            (self.frame, self.time, self.next_blender)
    def get_levels(self):
        """Return the Frame's levels.  Hopefully frame is a LevelFrame or
        descendent."""
        return self.frame.get_levels()

class Blender:
    """Blenders are functions that merge the effects of two LevelFrames."""
    def __init__(self):
        pass
    def __call__(self, startframe, endframe, blendtime):
        """Return a LevelFrame combining two LevelFrames (startframe and 
        endframe).  blendtime is how much of the blend should be performed
        and will be expressed as a percentage divided by 100, i.e. a float
        between 0.0 and 1.0.  
        
        Very important note: Blenders will *not* be asked for values
        at end points (i.e. blendtime=0.0 and blendtime=1.0).
        The LevelFrames will be allowed to specify the values at
        those times.  This is unfortunately for implemementation and
        simplicity purposes.  In other words, if we didn't do this,
        we could have two blenders covering the same point in time and
        not know which one to ask for the value.  Thus, this saves us
        a lot of messiness with minimal or no sacrifice."""
        pass
    def __str__(self):
        """As a default, we'll just return the name of the class.  Subclasses
        can add parameters on if they want."""
        return str(self.__class__)
    def linear_blend(self, startframe, endframe, blendtime):
        """Utility function to help you produce linear combinations of two
        blends.  blendtime is the percent/100 that the blend should 
        completed.  In other words, 0.25 means it should be 0.75 * startframe +
        0.25 * endframe.  This function is included since many blenders are
        just functions on the percentage and still combine start and end frames
        in this way."""
        return (startframe * (1.0 - blendtime)) + (endframe * blendtime)

class InstantEnd(Blender):
    """Instant change from startframe to endframe at the end.  In other words,
    the value returned will be the startframe all the way until the very end
    of the blend."""
    def __call__(self, startframe, endframe, blendtime):
        # "What!?" you say, "Why don't you care about blendtime?"
        # This is because Blenders never be asked for blenders at the endpoints
        # (after all, they wouldn't be blenders if they were). Please see
        # 'Very important note' in Blender.__doc__
        return startframe

class InstantStart(Blender):
    """Instant change from startframe to endframe at the beginning.  In other
    words, the value returned will be the startframe at the very beginning
    and then be endframe at all times afterwards."""
    def __call__(self, startframe, endframe, blendtime):
        # "What!?" you say, "Why don't you care about blendtime?"
        # This is because Blenders never be asked for blenders at the endpoints
        # (after all, they wouldn't be blenders if they were). Please see
        # 'Very important note' in Blender.__doc__
        return endframe

class LinearBlender(Blender):
    """Linear fade from one frame to another"""
    def __call__(self, startframe, endframe, blendtime):
        return self.linear_blend(startframe, endframe, blendtime)
        # return (startframe * (1.0 - blendtime)) + (endframe * blendtime)

class ExponentialBlender(Blender):
    """Exponential fade fron one frame to another.  You get to specify
    the exponent.  If my math is correct, exponent=1 means the same thing
    as LinearBlender."""
    def __init__(self, exponent):
        self.exponent = exponent
    def __call__(self, startframe, endframe, blendtime):
        blendtime = blendtime ** self.exponent
        return self.linear_blend(startframe, endframe, blendtime)

# 17:02:53 drewp: this makes a big difference for the SmoothBlender 
#                 (-x*x*(x-1.5)*2) function
class SmoothBlender(Blender):
    """Drew's "Smoove" Blender function.  Hopefully he'll document and
    parametrize it."""
    def __call__(self, startframe, endframe, blendtime):
        blendtime = (-1 * blendtime) * blendtime * (blendtime - 1.5) * 2
        return self.linear_blend(startframe, endframe, blendtime)

class TimelineTrack:
    """TimelineTrack is a single track in a Timeline.  It consists of a
    list of TimedEvents and a name.  Length is automatically the location
    of the last TimedEvent.  To extend the Timeline past that, add an
    EmptyTimedEvent."""
    def __init__(self, name, *timedevents):
        self.name = name
        self.events = list(timedevents)
        self.events.sort()
    def __str__(self):
        return "<TimelineTrack with events: %r>" % self.events
    def has_events(self):
        """Whether the TimelineTrack has anything in it.  In general,
        empty level Tracks should be avoided.  However, empty function tracks
        might be common."""
        return len(self.events)
    def length(self):
        """Returns the length of this track in pseudosecond time units.
        This is done by finding the position of the last TimedEvent."""
        return float(self.events[-1])
    def get(self, key, direction=FORWARD):
        """Returns the event at a specific time key.  If there is no event
        at that time, a search will be performed in direction.  Also note
        that if there are multiple events at one time, only the first will
        be returned.  (Probably first in order of adding.)  This is not
        a problem at the present since this method is intended for LevelFrames,
        which must exist at unique times."""
        if direction == BACKWARD:
            func = last_less_than
        else:
            func = first_greater_than

        return func(self.events, key)
    def get_range(self, i, j, direction=FORWARD):
        """Returns all events between i and j, exclusively.  If direction
        is FORWARD, j will be included.  If direction is BACKWARD, i will
        be included.  This is because this is used to find FunctionFrames
        and we assume that any function frames at the start point (which
        could be i or j) have been processed."""
        if direction == FORWARD:
            return [e for e in self.events if e > i and e <= j]
        else:
            return [e for e in self.events if e >= i and e < j]
    def __getitem__(self, key):
        """Returns the event at or after a specific time key.
        For example: timeline[3] will get the first event at time 3.

        If you want to get all events at time 3, you are in trouble, but
        you could achieve it with something like: 
        timeline.get_range(2.99, 3.01, FORWARD) 
        This is hopefully a bogus problem, since you can't have multiple
        LevelFrames at the same time."""
        return self.get(key, direction=FORWARD)
    def get_surrounding_frames(self, time):
        """Returns frames before and after a specific time.  This returns
        a 2-tuple: (previousframe, nextframe).  If you have chosen the exact 
        time of a frame, it will be both previousframe and nextframe."""
        return self.get(time, direction=BACKWARD), \
               self.get(time, direction=FORWARD)
    def get_levels_at_time(self, time):
        """Returns a LevelFrame with the levels of this track at that time."""
        before, after = self.get_surrounding_frames(time)
        
        if before == after:
            return before.frame
        else: # we have a blended value
            diff = after.time - before.time
            elapsed = time - before.time
            percent = elapsed / diff
            if not before.next_blender:
                raise MissingBlender, before
            return before.next_blender(before.frame, after.frame, percent)

class Timeline:
    def __init__(self, tracks, functions, rate=1, direction=FORWARD):
        """
        Most of this is old:

        You can have multiple FunctionFrames at the same time.  Their
        order is important though, since FunctionFrames will be applied
        in the order seen in this list.  blenders is a list of Blenders.
        rate is the rate of playback.  If set to 1, 1 unit inside the
        Timeline will be 1 second.  direction is the initial direction.
        If you want to do have looping, place a LoopFunction at the end of
        the Timeline.  Timelines don't have a set length.  Their length
        is bounded by their last frame.  You can put an EmptyFrame at
        some time if you want to extend a Timeline."""
        
        make_attributes_from_args('tracks', 'rate', 'direction')
        # the function track is a special track
        self.fn_track = TimelineTrack('functions', *functions)
        
        self.current_time = 0
        self.last_clock_time = None
        self.stopped = 1
    def length(self):
        """Length of the timeline in pseudoseconds.  This is determined by
        finding the length of the longest track."""
        track_lengths = [track.length() for track in self.tracks]
        track_lengths.append(self.fn_track.length())
        return max(track_lengths)
    def play(self):
        """Activates the timeline.  Future calls to tick() will advance the 
        timeline in the appropriate direction."""
        self.stopped = 0
    def stop(self):
        """The timeline will no longer continue in either direction, no
        FunctionFrames will be activated."""
        self.stopped = 1
        self.last_clock_time = None
    def reset(self):
        """Resets the timeline to 0.  Does not change the stoppedness of the 
        timeline."""
        self.current_time = 0
    def tick(self):
        """Updates the current_time and runs any FunctionFrames that the cursor
        passed over.  This call is ignored if the timeline is stopped."""
        if self.stopped:
            return
        
        last_time = self.current_time
        last_clock = self.last_clock_time
        
        # first, determine new time
        clock_time = time()
        if last_clock is None:
            last_clock = clock_time
        diff = clock_time - last_clock
        new_time = (self.direction * self.rate * diff) + last_time
        new_time = max(new_time, 0)
        new_time = min(new_time, self.length())
        
        # update the time
        self.last_clock_time = clock_time
        self.current_time = new_time
        
        # now, find out if we missed any functions
        if self.fn_track.has_events():
            lower_time, higher_time = last_time, new_time
            if lower_time > higher_time:
                lower_time, higher_time = higher_time, lower_time
            
            events_to_process = self.fn_track.get_range(lower_time, 
                higher_time, self.direction)
            
            for event in events_to_process:
                # they better be FunctionFrames
                event.frame(self, event, None) # the None should be a Node, 
                                               # but that part is coming later
    def reverse_direction(self):
        """Reverses the direction of play for this node"""
        self.direction = self.direction * -1
    def set_direction(self, direction):
        """Sets the direction of playback."""
        self.direction = direction
    def set_rate(self, new_rate):
        """Sets the rate of playback"""
        self.rate = new_rate
    def set_time(self, new_time):
        """Set the time to a new time."""
        self.current_time = new_time
    def get_levels(self):
        """Return the current levels from this timeline.  This is done by
        adding all the non-functional tracks together."""
        current_level_frame = LevelFrame('timeline sum', {})
        for t in self.tracks:
            current_level_frame += t.get_levels_at_time(self.current_time)

        return current_level_frame.get_levels()

if __name__ == '__main__':
    scene1 = LevelFrame('scene1', {'red' : 50, 'blue' : 25})
    scene2 = LevelFrame('scene2', {'red' : 10, 'blue' : 5, 'green' : 70})
    scene3 = LevelFrame('scene3', {'yellow' : 10, 'blue' : 80, 'purple' : 70})

    T = TimedEvent

    linear = LinearBlender()
    quad = ExponentialBlender(2)
    invquad = ExponentialBlender(0.5)
    smoove = SmoothBlender()

    track1 = TimelineTrack('lights',
        T(0, scene1, blender=linear),
        T(5, scene2, blender=quad),
        T(10, scene3, blender=smoove),
        T(15, scene2)) # last TimedEvent doesn't need a blender

    if 1:
        # bounce is semiworking
        bouncer = BounceFunction('boing')
        halver = HalfTimeFunction('1/2x')
        doubler = DoubleTimeFunction('2x')
        tl = Timeline([track1], [T(0, bouncer), 
                                 T(0, halver),
                                 T(15, bouncer),
                                 T(15, doubler)])
    else:
        looper = LoopFunction('loop1')
        tl = Timeline([track1], [T(14, looper)])
    tl.play()

    import Tix
    root = Tix.Tk()
    colorscalesframe = Tix.Frame(root)
    scalevars = {}
    # wow, this works out so well, it's almost like I planned it!
    # (actually, it's probably just Tk being as cool as it usually is)
    # ps. if this code ever turns into mainstream code for flax, I'll be
    # pissed (reason: we need to use classes, not this hacked crap!)
    colors = 'red', 'blue', 'green', 'yellow', 'purple'
    for color in colors:
        sv = Tix.DoubleVar()
        scalevars[color] = sv
        scale = Tix.Scale(colorscalesframe, from_=100, to_=0, bg=color,
            variable=sv)
        scale.pack(side=Tix.LEFT)

    def set_timeline_time(time):
        tl.set_time(float(time))
        # print 'set_timeline_time', time

    def update_scales():
        levels = tl.get_levels()
        for color in colors:
            scalevars[color].set(levels.get(color, 0))
    
    colorscalesframe.pack()
    time_scale = Tix.Scale(root, from_=0, to_=track1.length(), 
        orient=Tix.HORIZONTAL, res=0.01, command=set_timeline_time)
    time_scale.pack(side=Tix.BOTTOM, fill=Tix.X, expand=1)

    def play_tl():
        tl.tick()
        update_scales()
        time_scale.set(tl.current_time)
        # print 'time_scale.set', tl.current_time
        root.after(10, play_tl)
    
    controlwindow = Tix.Toplevel()
    Tix.Button(controlwindow, text='Stop', 
        command=lambda: tl.stop()).pack(side=Tix.LEFT)
    Tix.Button(controlwindow, text='Play', 
        command=lambda: tl.play()).pack(side=Tix.LEFT)
    Tix.Button(controlwindow, text='Reset', 
        command=lambda: time_scale.set(0)).pack(side=Tix.LEFT)
    Tix.Button(controlwindow, text='Flip directions', 
        command=lambda: tl.reverse_direction()).pack(side=Tix.LEFT)
    Tix.Button(controlwindow, text='1/2x', 
        command=lambda: tl.set_rate(0.5 * tl.rate)).pack(side=Tix.LEFT)
    Tix.Button(controlwindow, text='2x', 
        command=lambda: tl.set_rate(2 * tl.rate)).pack(side=Tix.LEFT)
    
    root.after(100, play_tl)

    # Timeline.set_time = trace(Timeline.set_time)
        
    Tix.mainloop()
