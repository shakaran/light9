from __future__ import division
import sys,math,glob,random,os
from bisect import bisect_left,bisect,bisect_right
import Tkinter as tk
from dispatch import dispatcher

import run_local
from light9 import Submaster, dmxclient, networking, cursors
from light9.TLUtility import make_attributes_from_args
from light9.dmxchanedit import gradient

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

    def insert_pt(self,new_pt):
        i = bisect(self.points,(new_pt[0],None))
        self.points.insert(i,new_pt)
    __call__=eval

class RegionZoom:
    """rigs c-a-b1 to drag out an area to zoom to."""
    def __init__(self, canvas, world_from_screen, screen_from_world):
        self.canvas, self.world_from_screen = canvas, world_from_screen
        self.screen_from_world = screen_from_world

        for evtype, method in [("ButtonPress-1",self.press),
                               ("Motion",self.motion),
                               ("ButtonRelease-1",self.release)]:
            canvas.bind("<Control-Alt-%s>" % evtype, method)
            if evtype != "ButtonPress-1":
                canvas.bind("<%s>" % evtype, method)
        canvas.bind("<Leave>", self.finish)
        self.start_t = self.old_cursor = None
        self.state = None

    def press(self,ev):
        if self.state is not None:
            self.finish()
        self.state = "buttonpress"
            
        self.start_t = self.end_t = self.world_from_screen(ev.x,0)[0]
        self.start_x = ev.x
        can = self.canvas

        for pos in ('start_t','end_t','hi','lo'):
            can.create_line(0,0,50,50, width=3, fill='black',
                            tags=("regionzoom",pos))
        # if updatelines isn't called here, subsequent updatelines
        # will fail for reasons i don't understand
        self.updatelines()

        cursors.push(can, "@/home/drewp/projects/light9/cursor1.xbm")
        
    def updatelines(self):

        # better would be a gray25 rectangle over the region
        
        can = self.canvas
        pos_x = {}
        height = can.winfo_height()
        for pos in ('start_t', 'end_t'):
            pos_x[pos] = x = self.screen_from_world((getattr(self,pos),0))[0]
            cid = can.find_withtag("regionzoom && %s" % pos)
            can.coords(cid, x, 0, x, height)
            
        for tag,frac in [('hi',.1),('lo',.9)]:
            cid = can.find_withtag("regionzoom && %s" % tag)
            can.coords(cid, pos_x['start_t'], frac * height,
                       pos_x['end_t'], frac * height)

    def motion(self,ev):
        if self.state != "buttonpress":
            return

        self.end_t = self.world_from_screen(ev.x,0)[0]
        self.updatelines()

    def release(self,ev):
        if self.state != "buttonpress":
            return
        
        if abs(self.start_x - ev.x) < 10:
            # clicked
            factor = 1/1.5
            if ev.state & 1:
                factor = 1.5 # c-s-a-b1 zooms out
            dispatcher.send("zoom about mouse",
                            t=self.start_t,
                            factor=factor)

            self.finish()
            return
            
        dispatcher.send("zoom to range",
                        start=min(self.start_t, self.end_t),
                        end=max(self.start_t, self.end_t))
        self.finish()
        
    def finish(self, *ev):
        if self.state is not None:
            self.state = None
            self.canvas.delete("regionzoom")
            self.start_t = None
            cursors.pop(self.canvas)

class Curveview(tk.Canvas):
    def __init__(self,master,curve,**kw):
        self.curve=curve
        self._time = 0
        tk.Canvas.__init__(self,master,width=10,height=10,
                           relief='sunken',bd=1,
                           closeenough=5,takefocus=1, **kw)
        self.selected_points=[] # idx of points being dragged
        self.update()
        # self.bind("<Enter>",self.focus)
        dispatcher.connect(self.input_time,"input time")
        dispatcher.connect(self.update,"zoom changed")
        dispatcher.connect(self.update,"points changed",sender=self.curve)
        self.bind("<Configure>",self.update)
        for x in range(1, 6):
            def add_kb_marker_point(evt, x=x):
                print "add_kb_marker_point", evt
                self.add_point((self.current_time(), (x - 1) / 4.0))

            self.bind("<Key-%s>" % x, add_kb_marker_point)


        for butnum,factor in (5, 1.5),(4, 1/1.5):
            self.bind("<ButtonPress-%s>"%butnum,
                      lambda ev,factor=factor:
                      dispatcher.send("zoom about mouse",
                                      t=self.world_from_screen(ev.x,0)[0],
                                      factor=factor))
        self.bind("<Key-Escape>",lambda ev:
                  dispatcher.send("see time",
                                  t=self.current_time()))
        RegionZoom(self, self.world_from_screen, self.screen_from_world)

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
    
    def input_time(self,val):
        t=val
        pts = self.screen_from_world((val,0))+self.screen_from_world((val,1))
        self.delete('timecursor')
        self.create_line(*pts,**dict(width=2,fill='red',tags=('timecursor',)))
        self._time = t
    def update(self,*args):

        self.zoom = dispatcher.send("zoom area")[0][1]
        cp = self.curve.points

        visible_x = (self.world_from_screen(0,0)[0],
                     self.world_from_screen(self.winfo_width(),0)[0])

        visleftidx = max(0,bisect_left(cp,(visible_x[0],None))-1)
        visrightidx = min(len(cp)-1,bisect_left(cp,(visible_x[1],None))+1)
                             
        visible_points = cp[visleftidx:visrightidx+1]
        visible_idxs = range(visleftidx,visrightidx+1)
        
        self.delete('curve')

        if self.winfo_height() < 30:
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
            self.create_line(x,0, x,70,
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
        self.create_line(x,self.winfo_height(),x,self.winfo_height()-20,
                         tags=('curve',))
        self.create_text(x,self.winfo_height()-20,text=label,anchor='s',
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
        self.tag_bind(line,"<Control-ButtonPress-1>",self.newpointatmouse)


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
            self.bind("<Motion>",
                      lambda ev,i=i: self.dotmotion(ev,i))
            self.bind("<ButtonRelease-1>",
                      lambda ev,i=i: self.dotrelease(ev,i))
            self.dots[i]=dot

        self.highlight_selected_dots()
        

    def newpointatmouse(self, ev):
        p = self.world_from_screen(ev.x,ev.y)
        x, y = p
        y = max(0, y)
        y = min(1, y)
        p = x, y
        self.add_point(p)

    def add_point(self, p):
        self.unselect()
        self.curve.insert_pt(p)
        self.update()

    def highlight_selected_dots(self):
        for i,d in self.dots.items():
            if i in self.selected_points:
                self.itemconfigure(d,fill='red')
            else:
                self.itemconfigure(d,fill='blue')
        
    def dotpress(self,ev,dotidx):
        self.selected_points=[dotidx]
        self.highlight_selected_dots()

    def dotmotion(self,ev,dotidx):
        cp = self.curve.points
        moved=0
        for idx in self.selected_points:
            x,y = self.world_from_screen(ev.x,ev.y)
            y = max(0,min(1,y))
            if idx>0 and x<=cp[idx-1][0]:
                continue
            if idx<len(cp)-1 and x>=cp[idx+1][0]:
                continue
            moved=1
            cp[idx] = (x,y)
        if moved:
            self.update()
    def unselect(self):
        self.selected_points=[]
        self.highlight_selected_dots()
        
    def dotrelease(self,ev,dotidx):
        self.unselect()
        
class Curveset:
    curves = None # curvename : curve
    def __init__(self):
        self.curves = {}
    def load(self,basename):
        """find all files that look like basename-curvename and add
        curves with their contents"""
        for filename in glob.glob("%s-*"%basename):
            curvename = filename[filename.rfind('-')+1:]
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
        dispatcher.send("add_curve",sender=self,name=name)

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


class Curvesetview(tk.Frame):
    curves = None # curvename : Curveview
    def __init__(self,master,curveset,**kw):
        self.curves = {}
        self.curveset = curveset
        tk.Frame.__init__(self,master,**kw)
        
        f = tk.Frame(self,relief='raised',bd=1)
        f.pack(side='top',fill='x')
        tk.Button(f,text="new curve named:",
                  command=lambda: self.curveset.new_curve(self.newcurvename.get())).pack(side='left')
        self.newcurvename = tk.StringVar()
        tk.Entry(f,textvariable=self.newcurvename).pack(side='left',
                                                        fill='x',exp=1)
        
        
        dispatcher.connect(self.add_curve,"add_curve",sender=self.curveset)
        
    def add_curve(self,name):
        f = tk.Frame(self,relief='raised',bd=1)
        f.pack(side='top',fill='both',exp=1)
        tk.Label(f,text="curve %r"%name,width=15).pack(side='left')
        cv = Curveview(f,self.curveset.curves[name])
        cv.pack(side='right',fill='both',exp=1)
        self.curves[name] = cv
