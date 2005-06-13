from __future__ import division
import Tkinter as tk
from dispatch import dispatcher

class Zoomcontrol(object,tk.Canvas):

    mintime=-5

    def maxtime():
        doc = "seconds at the right edge of the bar"
        def fget(self): return self._maxtime
        def fset(self, value):
            self._maxtime = value
            self.redrawzoom()
        return locals()
    maxtime = property(**maxtime())

    _end = _start = 0
    def start():
        def fget(self): return self._start
        def fset(self,v):
            v = max(self.mintime,v)
            if v < self._end:
                self._start = v
        return locals()
    start = property(**start())

    def end():
        def fget(self): return self._end
        def fset(self,v):
            v = min(self.maxtime,v)
            if v > self._start:
                self._end = v
        return locals()
    end = property(**end())
        

    def __init__(self,master,**kw):
        self.maxtime=370
        self.start=0
        self.end=20
        tk.Canvas.__init__(self,master,width=250,height=30,
                           relief='raised',bd=1,bg='gray60',**kw)
        self.leftbrack = self.create_line(0,0,0,0,0,0,0,0,width=5)
        self.rightbrack = self.create_line(0,0,0,0,0,0,0,0,width=5)
        self.shade = self.create_rectangle(0,0,0,0,fill='gray70',outline=None)
        self.time = self.create_line(0,0,0,0,fill='red',width=2)
        self.redrawzoom()
        self.bind("<Configure>",self.redrawzoom)

        if 0:
            # works, but you have to stay in the widget while you drag
            self.bind("<ButtonPress-1>",self.press)
            self.tag_bind(self.leftbrack,"<B1-Motion>",
                          lambda ev: self.adjust(ev,'start'))
            self.tag_bind(self.rightbrack,"<B1-Motion>",
                          lambda ev: self.adjust(ev,'end'))
            self.tag_bind(self.shade,"<B1-Motion>",
                          lambda ev: self.adjust(ev,'offset'))
        else:
            # works better
            # bind to buttonpress wasnt working, but Enter is good enough
            self.tag_bind(self.leftbrack,"<Enter>",
                          lambda ev: self.press(ev,'start'))
            self.tag_bind(self.shade,"<Enter>",
                          lambda ev: self.press(ev,'offset'))
            self.tag_bind(self.rightbrack,"<Enter>",
                          lambda ev: self.press(ev,'end'))
            self.bind("<B1-Motion>",self.adjust)
            self.bind("<ButtonRelease-1>",self.release)
        
        dispatcher.connect(lambda: (self.start,self.end),"zoom area",weak=0)
        dispatcher.connect(self.input_time,"input time")
        dispatcher.connect(lambda maxtime: (setattr(self,'maxtime',maxtime+15),
                                            self.redrawzoom()),
                           "max time",weak=0)
        dispatcher.connect(self.zoom_about_mouse,"zoom about mouse")
        dispatcher.connect(self.see_time,"see time")
        dispatcher.connect(self.zoom_to_range,"zoom to range")
        self.created=1
    def zoom_to_range(self,start,end):
        self.start = start
        self.end = end
        self.redrawzoom()

    def zoom_about_mouse(self,t,factor):
        self.start = t - factor*(t-self.start)
        self.end = t + factor*(self.end-t)
        self.redrawzoom()

    def see_time(self,t):
        vis_seconds = self.end - self.start
        margin = vis_seconds * .9 # left side is nicest
        if t < self.start:
            self.offset -= (self.start - t) + margin
        # t doesn't have to be ALL the way off-screen
        if t > (self.end - vis_seconds * .3): 
            self.offset += (t - self.end) + margin
        self.redrawzoom()
            
    def input_time(self,val):
        t=val
        x=self.can_for_t(t)
        self.coords(self.time,x,0,x,self.winfo_height())
    def press(self,ev,attr):
        self.adjustingattr = attr
        
    def release(self,ev):
        if hasattr(self,'adjustingattr'): del self.adjustingattr
        if hasattr(self,'lastx'): del self.lastx
    def adjust(self,ev,attr=None):

        if not hasattr(self,'adjustingattr'):
            return
        attr = self.adjustingattr
        
        if not hasattr(self,'lastx'):
            self.lastx = ev.x
        new = self.can_for_t(getattr(self,attr)) + (ev.x - self.lastx)
        self.lastx = ev.x
        setattr(self,attr,self.t_for_can(new))
        self.redrawzoom()
        
    def offset():
        doc = "virtual attr that adjusts start and end together"
        def fget(self):
            return self.start
        def fset(self, value):
            d = self.end-self.start
            self.start = value
            self.end = self.start+d
        return locals()
    offset = property(**offset())

    def can_for_t(self,t):
        return (t-self.mintime)/(self.maxtime-self.mintime)*(self.winfo_width()-30)+20
    def t_for_can(self,x):
        return (x-20)/(self.winfo_width()-30)*(self.maxtime-self.mintime)+self.mintime

    def redrawzoom(self,*args):
        """redraw pieces based on start/end"""
        dispatcher.send("zoom changed")
        if not hasattr(self,'created'): return
        y1,y2=3,self.winfo_height()-3
        lip = 6
        scan = self.can_for_t(self.start)
        ecan = self.can_for_t(self.end)
        self.coords(self.leftbrack,scan+lip,y1,scan,y1,scan,y2,scan+lip,y2)
        self.coords(self.rightbrack,ecan-lip,y1,ecan,y1,ecan,y2,ecan-lip,y2)
        self.coords(self.shade,scan+5,y1+lip,ecan-5,y2-lip)
        self.delete("tics")
        lastx=-1000
        for t in range(0,int(self.maxtime)):
            x = self.can_for_t(t)
            if 0<x<self.winfo_width() and x-lastx>30:
                txt=str(t)
                if lastx==-1000:
                    txt=txt+"sec"
                self.create_line(x,0,x,15,
                                 tags=('tics',))
                self.create_text(x,self.winfo_height()-1,anchor='s',
                                 text=txt,tags=('tics',),font='6x13')
                lastx = x

