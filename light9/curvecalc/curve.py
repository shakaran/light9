from __future__ import division
import glob, time, logging
from bisect import bisect_left,bisect
import louie as dispatcher

from bcf2000 import BCF2000

log = logging.getLogger()
# todo: move to config, consolidate with ascoltami, musicPad, etc
introPad = 4
postPad = 4

class Curve(object):
    """curve does not know its name. see Curveset"""
    points = None # x-sorted list of (x,y)
    def __init__(self):
        self.points = []
        self._muted = False

    def __repr__(self):
        return "<Curve (%s points)>" % len(self.points)

    def muted():
        doc = "Whether to currently send levels (boolean, obviously)"
        def fget(self):
            return self._muted
        def fset(self, val):
            self._muted = val
            dispatcher.send('mute changed', sender=self)
        return locals()
    muted = property(**muted())

    def toggleMute(self):
        self.muted = not self.muted

    def load(self,filename):
        self.points[:]=[]
        for line in file(filename):
            self.points.append(tuple([float(a) for a in line.split()]))
        self.points.sort()
        dispatcher.send("points changed",sender=self)

    def save(self,filename):
        if filename.endswith('-music') or filename.endswith('_music'):
            print "not saving music track"
            return
        f = file(filename,'w')
        for p in self.points:
            f.write("%s %s\n" % p)
        f.close()

    def eval(self, t, allow_muting=True):
        if self.muted and allow_muting:
            return 0

        i = bisect_left(self.points,(t,None))-1

        if self.points[i][0]>t:
            return self.points[i][1]
        if i>=len(self.points)-1:
            return self.points[i][1]

        p1,p2 = self.points[i],self.points[i+1]
        frac = (t-p1[0])/(p2[0]-p1[0])
        y = p1[1]+(p2[1]-p1[1])*frac
        return y
    __call__=eval

    def insert_pt(self,new_pt):
        i = bisect(self.points,(new_pt[0],None))
        self.points.insert(i,new_pt)

    def indices_between(self, x1, x2, beyond=0):
        leftidx = max(0, bisect(self.points, (x1,None)) - beyond)
        rightidx = min(len(self.points),
                       bisect(self.points, (x2,None)) + beyond)
        return range(leftidx, rightidx)
        
    def points_between(self, x1, x2):
        return [self.points[i] for i in self.indices_between(x1,x2)]

    def point_before(self, x):
        """(x,y) of the point left of x, or None"""
        leftidx = self.index_before(x)
        if leftidx is None:
            return None
        return self.points[leftidx]

    def index_before(self, x):
        leftidx = bisect(self.points, (x,None)) - 1
        if leftidx < 0:
            return None
        return leftidx
        

def slope(p1,p2):
    if p2[0] == p1[0]:
        return 0
    return (p2[1] - p1[1]) / (p2[0] - p1[0])


class Sliders(BCF2000):
    def __init__(self, cb, knobCallback, knobButtonCallback):
        BCF2000.__init__(self)
        self.cb = cb
        self.knobCallback = knobCallback
        self.knobButtonCallback = knobButtonCallback
    def valueIn(self, name, value):
        if name.startswith("slider"):
            self.cb(int(name[6:]), value / 127)
        if name.startswith("knob"):
            self.knobCallback(int(name[4:]), value / 127)
        if name.startswith("button-knob"):
            self.knobButtonCallback(int(name[11:]))

        
class Curveset(object):
    
    curves = None # curvename : curve
    def __init__(self, sliders=False):
        """sliders=True means support the hardware sliders"""
        self.curves = {} # name : Curve
        self.curveName = {} # reverse
        self.sliderCurve = {} # slider number (1 based) : curve name
        self.sliderNum = {} # reverse
        if sliders:
            self.sliders = Sliders(self.hw_slider_in, self.hw_knob_in, 
                                   self.hw_knob_button)
            dispatcher.connect(self.curvesToSliders, "curves to sliders")
            dispatcher.connect(self.knobOut, "knob out")
            self.lastSliderTime = {} # num : time
            self.sliderSuppressOutputUntil = {} # num : time
            self.sliderIgnoreInputUntil = {}
        else:
            self.sliders = None

    def sorter(self, name):
        return not name.endswith('music'), name

    def load(self,basename, skipMusic=False):
        """find all files that look like basename-curvename and add
        curves with their contents

        This fires 'add_curve' dispatcher events to announce the new curves.
        """
        for filename in sorted(glob.glob("%s-*"%basename), key=self.sorter):
            curvename = filename[filename.rfind('-')+1:]
            if skipMusic and curvename in ['music', 'smooth_music']:
                continue
            c=Curve()
            c.load(filename)
            curvename = curvename.replace('-','_')
            self.add_curve(curvename,c)
            
    def save(self,basename):
        """writes a file for each curve with a name
        like basename-curvename"""
        for name,cur in self.curves.items():
            cur.save("%s-%s" % (basename,name))

    def curveNamesInOrder(self):
        return sorted(self.curves.keys(), key=self.sorter)
            
    def add_curve(self,name,curve):
        self.curves[name] = curve
        self.curveName[curve] = name

        if self.sliders and name not in ['smooth_music', 'music']:
            num = len(self.sliderCurve) + 1
            if num <= 8:
                self.sliderCurve[num] = name
                self.sliderNum[name] = num
            else:
                num = None
        else:
            num = None
            
        dispatcher.send("add_curve", slider=num, knobEnabled=num is not None,
                        sender=self, name=name)

    def globalsdict(self):
        return self.curves.copy()
    
    def get_time_range(self):
        return 0, dispatcher.send("get max time")[0][1]

    def new_curve(self,name):
        if name=="":
            print "no name given"
            return
        while name in self.curves:
           name=name+"-1"

        c = Curve()
        s,e = self.get_time_range()
        c.points.extend([(s,0), (e,0)])
        self.add_curve(name,c)

    def hw_slider_in(self, num, value):
        try:
            curve = self.curves[self.sliderCurve[num]]
        except KeyError:
            return

        now = time.time()
        if now < self.sliderIgnoreInputUntil.get(num):
            return
        # don't make points too fast. This is the minimum spacing
        # between slider-generated points.
        self.sliderIgnoreInputUntil[num] = now + .1
        
        # don't push back on the slider for a little while, since the
        # user might be trying to slowly move it. This should be
        # bigger than the ignore time above.
        self.sliderSuppressOutputUntil[num] = now + .2
        
        dispatcher.send("set key", curve=curve, value=value)

    def hw_knob_in(self, num, value):
        try:
            curve = self.curves[self.sliderCurve[num]]
        except KeyError:
            return
        dispatcher.send("knob in", curve=curve, value=value)

    def hw_knob_button(self, num):
        try:
            curve = self.curves[self.sliderCurve[num]]
        except KeyError:
            return

        dispatcher.send("set key", curve=curve)
        

    def curvesToSliders(self, t):
        now = time.time()
        for num, name in self.sliderCurve.items():
            if now < self.sliderSuppressOutputUntil.get(num):
                continue
#            self.lastSliderTime[num] = now
            
            value = self.curves[name].eval(t)
            self.sliders.valueOut("slider%s" % num, value * 127)

    def knobOut(self, curve, value):
        try:
            num = self.sliderNum[self.curveName[curve]]
        except KeyError:
            return
        self.sliders.valueOut("knob%s" % num, value * 127)
