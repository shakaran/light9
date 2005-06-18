from __future__ import division
import sys,math,glob,random,os
from bisect import bisect_left,bisect,bisect_right
import Tkinter as tk
from dispatch import dispatcher

import run_local
from light9 import Submaster, dmxclient, networking, cursors
from light9.TLUtility import make_attributes_from_args
from light9.dmxchanedit import gradient
from light9.zoomcontrol import RegionZoom

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

class Curveview(tk.Canvas):
    def __init__(self,master,curve,**kw):
        self.curve=curve
        self._time = 0
        tk.Canvas.__init__(self,master,width=10,height=10,
                           relief='sunken',bd=1,
                           closeenough=5,takefocus=1, **kw)
        self.selected_points=[] # idx of points being dragged
        self.update_curve()
        # self.bind("<Enter>",self.focus)
        dispatcher.connect(self.input_time,"input time")
        dispatcher.connect(self.update_curve,"zoom changed")
        dispatcher.connect(self.update_curve,"points changed",sender=self.curve)
        self.bind("<Configure>",self.update_curve)
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
        self.bind("<Key-Escape>", lambda ev:
                  dispatcher.send("see time",
                                  t=self.current_time()))
        self.bind("<Shift-Escape>", lambda ev:
                  dispatcher.send("see time until end",
                                  t=self.current_time()))
        self.bind("<Control-p>", lambda ev:
                  dispatcher.send("music seek",
                                  t=self.world_from_screen(ev.x,0)[0]))

        # this binds on c-a-b1, etc
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
    def update_curve(self,*args):

        self.zoom = dispatcher.send("zoom area")[0][1]
        cp = self.curve.points

        visible_x = (self.world_from_screen(0,0)[0],
                     self.world_from_screen(self.winfo_width(),0)[0])

        visleftidx = max(0,bisect_left(cp,(visible_x[0],None))-1)
        visrightidx = min(len(cp)-1,bisect_left(cp,(visible_x[1],None))+1)
                             
        visible_points = cp[visleftidx:visrightidx+1]
        visible_idxs = range(visleftidx,visrightidx+1)
        
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
        self.update_curve()

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
            self.update_curve()
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
        tk.Label(f, text="new curve named:").pack(side='left')
        
        self.newcurvename = tk.StringVar()

        def new_curve(event):
            self.curveset.new_curve(self.newcurvename.get())
            self.newcurvename.set('')
        
        entry = tk.Entry(f, textvariable=self.newcurvename)
        entry.pack(side='left', fill='x',exp=1)        
        entry.bind("<Key-Return>", new_curve)
        
        dispatcher.connect(self.add_curve,"add_curve",sender=self.curveset)
        
    def add_curve(self,name):
        f = tk.Frame(self,relief='raised',bd=1)
        f.pack(side='top',fill='both',exp=1)


        leftside = tk.Frame(f)
        leftside.pack(side='left')

        collapsed = tk.IntVar()
        txt = "curve %r" % name
        if len(name) > 7:
            txt = repr(name)
        tk.Label(leftside,text=txt,font="6x10",
                 width=15).pack(side='top')
            
        def cmd():
            if collapsed.get():
                f.pack(exp=0)
            else:
                f.pack(exp=1)
        tk.Checkbutton(leftside, text="collapsed", font="6x10",
                       variable=collapsed, command=cmd).pack(side='top')

        cv = Curveview(f,self.curveset.curves[name])
        cv.pack(side='left',fill='both',exp=1)
        self.curves[name] = cv
