from __future__ import division
import Tkinter as tk
from dispatch import dispatcher

class Zoomcontrol(object,tk.Canvas):

    def maxtime():
        doc = "seconds at the right edge of the bar"
        def fget(self): return self._maxtime
        def fset(self, value):
            self._maxtime = value
            self.updatewidget()
        return locals()
    maxtime = property(**maxtime())
    
    def start():
        def fget(self): return self._start
        def fset(self,v): self._start = max(0,v)
        return locals()
    start = property(**start())

    def end():
        def fget(self): return self._end
        def fset(self,v): self._end = min(self.maxtime,v)
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
        self.updatewidget()
        self.bind("<Configure>",self.updatewidget)

        self.bind("<ButtonPress-1>",lambda ev: setattr(self,'lastx',ev.x))
        self.tag_bind(self.leftbrack,"<B1-Motion>",
                      lambda ev: self.adjust('start',ev))
        self.tag_bind(self.rightbrack,"<B1-Motion>",
                      lambda ev: self.adjust('end',ev))
        self.tag_bind(self.shade,"<B1-Motion>",
                      lambda ev: self.adjust('offset',ev))
        dispatcher.connect(lambda: (self.start,self.end),"zoom area",weak=0)
        dispatcher.connect(self.input_time,"input time")
        dispatcher.connect(lambda maxtime: (setattr(self,'maxtime',maxtime),
                                            self.updatewidget()),"max time",weak=0)
        self.created=1
    def input_time(self,val):
        t=val
        x=self.can_for_t(t)
        self.coords(self.time,x,0,x,self.winfo_height())

    def adjust(self,attr,ev):
        if not hasattr(self,'lastx'):
            return
        new = self.can_for_t(getattr(self,attr)) + (ev.x - self.lastx)
        self.lastx = ev.x
        setattr(self,attr,self.t_for_can(new))
        self.updatewidget()
        dispatcher.send("zoom changed")
        
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
        return t/self.maxtime*(self.winfo_width()-30)+20
    def t_for_can(self,x):
        return (x-20)/(self.winfo_width()-30)*self.maxtime

    def updatewidget(self,*args):
        """redraw pieces based on start/end"""
        if not hasattr(self,'created'): return
        y1,y2=3,self.winfo_height()-3
        lip = 6
        scan = self.can_for_t(self.start)
        ecan = self.can_for_t(self.end)
        self.coords(self.leftbrack,scan+lip,y1,scan,y1,scan,y2,scan+lip,y2)
        self.coords(self.rightbrack,ecan-lip,y1,ecan,y1,ecan,y2,ecan-lip,y2)
        self.coords(self.shade,scan+3,y1+lip,ecan-3,y2-lip)
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
