from __future__ import division
import sys,math,glob,random,os, time
from bisect import bisect_left,bisect,bisect_right
import Tkinter as tk
try:
    from dispatch import dispatcher
except ImportError:
    import louie as dispatcher

import run_local
from light9 import Submaster, dmxclient, networking, cursors
from light9.TLUtility import make_attributes_from_args
from light9.dmxchanedit import gradient
from light9.zoomcontrol import RegionZoom
from bcf2000 import BCF2000

class Curve:
    """curve does not know its name. see Curveset"""
    points = None # x-sorted list of (x,y)
    def __init__(self):
        self.points = []

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

    def eval(self,t):
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
        

def vlen(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1])

def angle_between(base, p0, p1):
    p0 = p0[0] - base[0], p0[1] - base[1]
    p1 = p1[0] - base[0], p1[1] - base[1]
    p0 = [x/vlen(p0) for x in p0]
    p1 = [x/vlen(p1) for x in p1]
    dot = p0[0]*p1[0]+p0[1]*p1[1]
    dot = max(-1,min(1,dot))
    return math.degrees(math.acos(dot))

def slope(p1,p2):
    if p2[0] == p1[0]:
        return 0
    return (p2[1] - p1[1]) / (p2[0] - p1[0])

class Sketch:
    """a sketch motion on a curveview, with temporary points while you
    draw, and simplification when you release"""
    
    def __init__(self,curveview,ev):
        self.curveview = curveview
        self.pts = []
        self.last_x = None

    def motion(self,ev):
        p = self.curveview.world_from_screen(ev.x, ev.y)
        p = p[0], max(0,min(1,p[1]))
        if self.last_x is not None and abs(ev.x - self.last_x) < 4:
            return
        self.last_x = ev.x
        self.pts.append(p)
        self.curveview.add_point(p)

    def release(self,ev):
        pts = self.pts
        pts.sort()

        dx = .01
        to_remove = []
        for i in range(1,len(pts)-1):
            x = pts[i][0]

            p_left = (x - dx, self.curveview.curve(x - dx))
            p_right = (x + dx, self.curveview.curve(x + dx))

            if angle_between(pts[i], p_left, p_right) > 160:
                to_remove.append(i)

        for i in to_remove:
            self.curveview.curve.points.remove(pts[i])

        # the simplified curve may now be too far away from some of
        # the points, so we'll put them back. this has an unfortunate
        # bias toward reinserting the earlier points
        for i in to_remove:
            p = pts[i]
            if abs(self.curveview.curve(p[0]) - p[1]) > .1:
                self.curveview.add_point(p)
            
        self.curveview.update_curve()


class Curveview(tk.Canvas):
    def __init__(self, master, curve, knobEnabled=False, **kw):
        """knobEnabled=True highlights the previous key and ties it to a
        hardware knob"""
        self.curve=curve
        self.knobEnabled = knobEnabled
        self._time = 0
        self.last_mouse_world = None
        tk.Canvas.__init__(self,master,width=10,height=10,
                           relief='sunken',bd=1,
                           closeenough=5,takefocus=1, **kw)
        self.selected_points=[] # idx of points being dragged
        self.update_curve()
        # self.bind("<Enter>",self.focus)
        dispatcher.connect(self.input_time,"input time")
        dispatcher.connect(self.update_curve,"zoom changed")
        dispatcher.connect(self.update_curve,"points changed",
                           sender=self.curve)
        dispatcher.connect(self.select_between,"select between")
        if self.knobEnabled:
            dispatcher.connect(self.knob_in, "knob in")
            dispatcher.connect(self.slider_in, "slider in")
        self.bind("<Configure>",self.update_curve)
        for x in range(1, 6):
            def add_kb_marker_point(evt, x=x):
                self.add_point((self.current_time(), (x - 1) / 4.0))

            self.bind("<Key-%s>" % x, add_kb_marker_point)


        for butnum,factor in (5, 1.5),(4, 1/1.5):
            self.bind("<ButtonPress-%s>"%butnum,
                      lambda ev,factor=factor:
                      dispatcher.send("zoom about mouse",
                                      t=self.world_from_screen(ev.x,0)[0],
                                      factor=factor))
        self.bind("<Key-Escape>", lambda ev:
                  dispatcher.send("see time",
                                  t=self.current_time()))
        self.bind("<Shift-Escape>", lambda ev:
                  dispatcher.send("see time until end",
                                  t=self.current_time()))
        self.bind("<Control-p>", lambda ev:
                  dispatcher.send("music seek",
                                  t=self.world_from_screen(ev.x,0)[0]))

        self.bind("<Motion>",
                  self.dotmotion, add=True)
        self.bind("<ButtonRelease-1>",
                  self.dotrelease, add=True)


        # this binds on c-a-b1, etc
        self.regionzoom = RegionZoom(self, self.world_from_screen,
                                     self.screen_from_world)

        self.sketch = None # an in-progress sketch
        self.bind("<Shift-ButtonPress-1>", self.sketch_press)
        self.bind("<Shift-B1-Motion>", self.sketch_motion)
        self.bind("<Shift-ButtonRelease-1>", self.sketch_release)


        self.dragging_dots = False
        self.selecting = False
        self.bind("<ButtonPress-1>",#"<Alt-Key>",
                  self.select_press)
        self.bind("<Motion>", self.select_motion, add=True)
        self.bind("<ButtonRelease-1>", #"<Alt-KeyRelease>",
                  self.select_release)

        self.bind("<ButtonPress-1>", self.check_deselect, add=True)

    def knob_in(self, curve, value):
        """user turned a hardware knob, which edits the point to the
        left of the current time"""
        if curve != self.curve:
            return
        idx = self.curve.index_before(self.current_time())
        if idx is not None:
            pos = self.curve.points[idx]
            self.curve.points[idx] = (pos[0], value)
            self.update_curve()

    def slider_in(self, curve, value):
        """user pushed on a slider. make a new key"""
        if curve != self.curve:
            return

        self.curve.insert_pt((self.current_time(), value))
        self.update_curve()

    def print_state(self, msg=""):
        if 0:
            print "%s: dragging_dots=%s selecting=%s" % (
                msg, self.dragging_dots, self.selecting)

    def check_deselect(self,ev):
        try:
            self.find_index_near(ev.x, ev.y)
        except ValueError:
            self.selected_points[:] = []
            self.highlight_selected_dots()

    def select_press(self,ev):
        self.print_state("select_press")
        if self.dragging_dots:
            return
        if not self.selecting:
            self.selecting = True
            self.select_start = self.world_from_screen(ev.x,0)[0]
            cursors.push(self,"gumby")
        
    def select_motion(self,ev):
        if not self.selecting:
            return
        start = self.select_start
        cur = self.world_from_screen(ev.x, 0)[0]
        self.select_between(start, cur)
        
    def select_release(self,ev):
        self.print_state("select_release")

        # dotrelease never gets called, but I can clear that state here
        self.dragging_dots = False
        
        if not self.selecting:
            return
        cursors.pop(self)
        self.selecting = False
        self.select_between(self.select_start,
                            self.world_from_screen(ev.x,0)[0])

    def sketch_press(self,ev):
        self.sketch = Sketch(self,ev)

    def sketch_motion(self,ev):
        if self.sketch:
            self.sketch.motion(ev)

    def sketch_release(self,ev):
        if self.sketch:
            self.sketch.release(ev)
            self.sketch = None

    def current_time(self):
        return self._time

    def screen_from_world(self,p):
        start,end = self.zoom
        ht = self.winfo_height()
        return (p[0]-start)/(end-start)*self.winfo_width(), (ht-5)-p[1]*(ht-10)

    def world_from_screen(self,x,y):
        start,end = self.zoom
        ht = self.winfo_height()
        return x/self.winfo_width()*(end-start)+start, ((ht-5)-y)/(ht-10)
    
    def input_time(self, val, forceUpdate=False):
        # i tried various things to make this not update like crazy,
        # but the timeline was always missing at startup, so i got
        # scared that things were getting built in a funny order.        
        #if self._time == val:
        #    return
        
        t=val
        pts = self.screen_from_world((val,0))+self.screen_from_world((val,1))
        self.delete('timecursor')
        self.create_line(*pts,**dict(width=2,fill='red',tags=('timecursor',)))
        self.have_time_line = True
        self._time = t
        if self.knobEnabled:
            self.delete('knob')
            prevKey = self.curve.point_before(t)
            if prevKey is not None:
                pos = self.screen_from_world(prevKey)
                self.create_oval(pos[0] - 8, pos[1] - 8,
                                 pos[0] + 8, pos[1] + 8,
                                 outline='#800000',
                                 tags=('knob',))
                dispatcher.send("knob out", value=prevKey[1], curve=self.curve)
        
    def update_curve(self,*args):

        self.zoom = dispatcher.send("zoom area")[0][1]
        cp = self.curve.points

        visible_x = (self.world_from_screen(0,0)[0],
                     self.world_from_screen(self.winfo_width(),0)[0])

        visible_idxs = self.curve.indices_between(visible_x[0], visible_x[1],
                                                  beyond=1)
        visible_points = [cp[i] for i in visible_idxs]
        
        self.delete('curve')

        if self.winfo_height() < 40:
            self._draw_gradient()
        else:
            self._draw_markers(visible_x)
            self._draw_line(visible_points)

            self.dots = {} # idx : canvas rectangle

            if len(visible_points)<50:
                self._draw_handle_points(visible_idxs,visible_points)

    def _draw_gradient(self):
        gradient_res = 3
        for x in range(0,self.winfo_width(),gradient_res):
            wx = self.world_from_screen(x,0)[0]
            mag = self.curve.eval(wx)
            self.create_line(x,0, x,40,
                             fill=gradient(mag,
                                           low=(20,10,50),
                                           high=(255,187,255)),
                             width=gradient_res, tags='curve')

    def _draw_markers(self,visible_x):
        mark = self._draw_one_marker

        mark(0,"0")
        t1,t2=visible_x
        if t2-t1<30:
            for t in range(int(t1),int(t2)+1):
                mark(t,str(t))
        mark(-4,"-4")

        endtimes = dispatcher.send("get max time")
        if endtimes:
            endtime = endtimes[0][1]
            mark(endtime,"end %.1f"%endtime)
            mark(endtime+10,"post %.1f"%(endtime+10))
        
    def _draw_one_marker(self,t,label):
        x = self.screen_from_world((t,0))[0]
        ht = self.winfo_height()
        self.create_line(x,ht,x,ht-20,
                         tags=('curve',))
        self.create_text(x,ht-20,text=label,anchor='s',
                         tags=('curve',))


    def _draw_line(self,visible_points):
        linepts=[]
        step=1
        linewidth=2
        if len(visible_points)>800:
            step = int(len(visible_points)/800)
            linewidth=1
        for p in visible_points[::step]:
            linepts.extend(self.screen_from_world(p))
        if len(linepts)<4:
            return
        line = self.create_line(*linepts,**dict(width=linewidth,tags='curve'))

        # canvas doesnt have keyboard focus, so i can't easily change the
        # cursor when ctrl is pressed
        #        def curs(ev):
        #            print ev.state
        #        self.bind("<KeyPress>",curs)
        #        self.bind("<KeyRelease-Control_L>",lambda ev: curs(0))
        self.tag_bind(line,"<Control-ButtonPress-1>",self.new_point_at_mouse)


    def _draw_handle_points(self,visible_idxs,visible_points):
        for i,p in zip(visible_idxs,visible_points):
            rad=3
            worldp = p
            p = self.screen_from_world(p)
            dot = self.create_rectangle(p[0]-rad,p[1]-rad,p[0]+rad,p[1]+rad,
                                        outline='black',fill='blue',
                                        tags=('curve','point', 'handle%d' % i))
            if worldp[1] == 0:
                rad += 3
                dot2 = self.create_oval(p[0]-rad,p[1]-rad,
                                             p[0]+rad,p[1]+rad,
                                             outline='darkgreen',
                                       tags=('curve','point', 'handle%d' % i))
            self.tag_bind('handle%d' % i,"<ButtonPress-1>",
                          lambda ev,i=i: self.dotpress(ev,i))
            #self.tag_bind('handle%d' % i, "<Key-d>",
            #              lambda ev, i=i: self.remove_point_idx(i))
                      
            self.dots[i]=dot

        def delpoint(ev):
            # had a hard time tag_binding to the points, so i trap at
            # the widget level (which might be nice anyway when there
            # are multiple pts selected)
            if self.selected_points:
                self.remove_point_idx(*self.selected_points)
        self.bind("<Key-Delete>", delpoint)

        self.highlight_selected_dots()

    def find_index_near(self,x,y):
        tags = self.gettags(self.find_closest(x, y))
        try:
            handletags = [t for t in tags if t.startswith('handle')]
            return int(handletags[0][6:])
        except IndexError:
            raise ValueError("no point found")
        
    def new_point_at_mouse(self, ev):
        p = self.world_from_screen(ev.x,ev.y)
        x, y = p
        y = max(0, y)
        y = min(1, y)
        p = x, y
        self.add_point(p)

    def add_point(self, p):
        self.unselect()
        self.curve.insert_pt(p)
        self.update_curve()
        
    def remove_point_idx(self, *idxs):
        idxs = list(idxs)
        while idxs:
            i = idxs.pop()

            self.curve.points.pop(i)
            newsel = []
            newidxs = []
            for si in range(len(self.selected_points)):
                sp = self.selected_points[si]
                if sp == i:
                    continue
                if sp > i:
                    sp -= 1
                newsel.append(sp)
            for ii in range(len(idxs)):
                if ii > i:
                    ii -= 1
                newidxs.append(idxs[ii])

            self.selected_points[:] = newsel
            idxs[:] = newidxs
            
        self.update_curve()

    def highlight_selected_dots(self):
        for i,d in self.dots.items():
            if i in self.selected_points:
                self.itemconfigure(d,fill='red')
            else:
                self.itemconfigure(d,fill='blue')
        
    def dotpress(self,ev,dotidx):
        self.print_state("dotpress")
        if dotidx not in self.selected_points:
            self.selected_points=[dotidx]
        self.highlight_selected_dots()
        self.last_mouse_world = self.world_from_screen(ev.x, ev.y)
        self.dragging_dots = True

    def select_between(self,start,end):
        if start > end:
            start, end = end, start
        self.selected_points = self.curve.indices_between(start,end)
        self.highlight_selected_dots()

    def dotmotion(self,ev):
        if not self.dragging_dots:
            return
        if not ev.state & 256:
            return # not lmb-down
        cp = self.curve.points
        moved=0

        cur = self.world_from_screen(ev.x, ev.y)
        if self.last_mouse_world:
            delta = (cur[0] - self.last_mouse_world[0],
                     cur[1] - self.last_mouse_world[1])
        else:
            delta = 0,0
        self.last_mouse_world = cur
        
        for idx in self.selected_points:

            newp = [cp[idx][0] + delta[0], cp[idx][1] + delta[1]]
            
            newp[1] = max(0,min(1,newp[1]))
            
            if idx>0 and newp[0] <= cp[idx-1][0]:
                continue
            if idx<len(cp)-1 and newp[0] >= cp[idx+1][0]:
                continue
            moved=1
            cp[idx] = tuple(newp)
        if moved:
            self.update_curve()

    def unselect(self):
        self.selected_points=[]
        self.highlight_selected_dots()
        
    def dotrelease(self,ev):
        self.print_state("dotrelease")
        if not self.dragging_dots:
            return
        self.last_mouse_world = None
        self.dragging_dots = False

class Sliders(BCF2000):
    def __init__(self, cb, knobCallback):
        BCF2000.__init__(self)
        self.cb = cb
        self.knobCallback = knobCallback
    def valueIn(self, name, value):
        if name.startswith("slider"):
            self.cb(int(name[6:]), value / 127)
        if name.startswith("knob"):
            self.knobCallback(int(name[4:]), value / 127)

        
class Curveset:
    curves = None # curvename : curve
    def __init__(self, sliders=False):
        """sliders=True means support the hardware sliders"""
        self.curves = {} # name : Curve
        self.curveName = {} # reverse
        self.sliderCurve = {} # slider number (1 based) : curve name
        self.sliderNum = {} # reverse
        if sliders:
            self.sliders = Sliders(self.hw_slider_in, self.hw_knob_in)
            dispatcher.connect(self.curvesToSliders, "curves to sliders")
            dispatcher.connect(self.knobOut, "knob out")
            self.lastSliderTime = {} # num : time
            self.sliderSuppressOutputUntil = {} # num : time
            self.sliderIgnoreInputUntil = {}
        else:
            self.sliders = None
        
    def load(self,basename, skipMusic=False):
        """find all files that look like basename-curvename and add
        curves with their contents"""
        for filename in glob.glob("%s-*"%basename):
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
            
    def add_curve(self,name,curve):
        self.curves[name] = curve
        self.curveName[curve] = name

        if self.sliders and name not in ['smooth_music', 'music']:
            num = len(self.sliderCurve) + 1
            self.sliderCurve[num] = name
            self.sliderNum[name] = num
        else:
            num = None
            
        dispatcher.send("add_curve", slider=num, knobEnabled=num is not None,
                        sender=self,name=name)

    def globalsdict(self):
        return self.curves.copy()
    
    def get_time_range(self):
        return -4, dispatcher.send("get max time")[0][1]+15

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
        
        dispatcher.send("slider in", curve=curve, value=value)

    def hw_knob_in(self, num, value):
        try:
            curve = self.curves[self.sliderCurve[num]]
        except KeyError:
            return
        dispatcher.send("knob in", curve=curve, value=value)

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

class Curvesetview(tk.Frame):
    curves = None # curvename : Curveview
    def __init__(self, master, curveset, **kw):
        self.curves = {}
        self.curveset = curveset
        tk.Frame.__init__(self,master,**kw)
        
        f = tk.Frame(self,relief='raised',bd=1)
        f.pack(side='top',fill='x')
        tk.Label(f, text="new curve named:").pack(side='left')
        
        self.newcurvename = tk.StringVar()

        def new_curve(event):
            self.curveset.new_curve(self.newcurvename.get())
            self.newcurvename.set('')
        
        entry = tk.Entry(f, textvariable=self.newcurvename)
        entry.pack(side='left', fill='x',exp=1)        
        entry.bind("<Key-Return>", new_curve)
        
        dispatcher.connect(self.add_curve,"add_curve",sender=self.curveset)
        
    def add_curve(self,name, slider=None, knobEnabled=False):
        f = tk.Frame(self,relief='raised',bd=1)
        f.pack(side='top',fill='both',exp=1)


        leftside = tk.Frame(f)
        leftside.pack(side='left')

        collapsed = tk.IntVar()
        txt = "curve '%s'" % name
        if len(name) > 7:
            txt = name
        tk.Label(leftside,text=txt,font="6x10",
                 width=15).pack(side='top')

        sliderLabel = None
        def cmd():
            if collapsed.get():
                if sliderLabel:
                    sliderLabel.pack_forget()
                f.pack(exp=0)
            else:
                if sliderLabel:
                    sliderLabel.pack(side='top')
                f.pack(exp=1)
        tk.Checkbutton(leftside, text="collapsed", font="6x10",
                       variable=collapsed, command=cmd).pack(side='top')

        if slider is not None:
            # slider should have a checkbutton, defaults to off for
            # music tracks
            sliderLabel = tk.Label(leftside, text="Slider %s" % slider,
                                   fg='#800000', font='arial 12 bold')
            sliderLabel.pack(side='top')

        cv = Curveview(f, self.curveset.curves[name],
                       knobEnabled=knobEnabled)
        cv.pack(side='left',fill='both',exp=1)
        self.curves[name] = cv
