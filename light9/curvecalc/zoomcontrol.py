from __future__ import division

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GooCanvas

import louie as dispatcher
from light9.curvecalc import cursors 

class ZoomControl(object):
    """
    please pack .widget
    """

    mintime = 0

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
            # don't protect for start<end since zooming sometimes sets
            # start temporarily after end
            self._start = v
        return locals()
    start = property(**start())

    def end():
        def fget(self): return self._end
        def fset(self,v):
            v = min(self.maxtime,v)
            self._end = v
        return locals()
    end = property(**end())

    def offset():
        doc = "virtual attr that adjusts start and end together"
        def fget(self):
            # work off the midpoint so that "crushing works equally
            # well in both directions
            return (self.start + self.end) / 2
        def fset(self, value):
            d = self.end-self.start
            self.start = value - d / 2
            self.end = value + d / 2
        return locals()
    offset = property(**offset())

    def __init__(self, **kw):
        self.widget = GooCanvas.Canvas(bounds_padding=5)
        self.widget.set_property("background-color", "gray60")
        self.widget.set_size_request(-1, 30)

        endtimes = dispatcher.send("get max time")
        if endtimes:
            self.maxtime = endtimes[0][1]
        else:
            self.maxtime = 0

        self.start=0
        self.end=20

        self.root = self.widget.get_root_item()
        self.leftbrack = GooCanvas.Polyline(parent=self.root,
                                            line_width=5, stroke_color='black')
        self.rightbrack = GooCanvas.Polyline(parent=self.root,
                                             line_width=5, stroke_color='black')
        self.shade = GooCanvas.Rect(parent=self.root,
                                    fill_color='gray70',
                                    line_width=.5)
        self.time = GooCanvas.Polyline(parent=self.root,
                                       line_width=2,
                                       stroke_color='red')
        self.redrawzoom()
        self.widget.connect("size-allocate", self.redrawzoom)

        self.widget.connect("motion-notify-event", self.adjust)
        self.widget.connect("button-release-event", self.release)
        self.leftbrack.connect("button-press-event",
                               lambda i, t, ev: self.press(ev, 'start'))
        self.rightbrack.connect("button-press-event",
                                lambda i, t, ev: self.press(ev, 'end'))
        self.shade.connect("button-press-event",
                           lambda i, t, ev: self.press(ev, 'offset'))
        
        dispatcher.connect(self.input_time,"input time")
        dispatcher.connect(self.max_time, "max time")
        dispatcher.connect(self.zoom_about_mouse, "zoom about mouse")
        dispatcher.connect(self.see_time, "see time")
        dispatcher.connect(self.see_time_until_end, "see time until end")
        dispatcher.connect(self.show_all, "show all")
        dispatcher.connect(self.zoom_to_range, "zoom to range")
        self.created=1
        self.lastTime = 0

    def max_time(self, maxtime):
        self.maxtime = maxtime
        self.redrawzoom()
    
    def zoom_to_range(self,start,end):
        self.start = start
        self.end = end
        self.redrawzoom()

    def show_all(self):
        self.start = self.mintime
        self.end = self.maxtime
        self.redrawzoom()

    def zoom_about_mouse(self,t,factor):
        self.start = t - factor*(t-self.start)
        self.end = t + factor*(self.end-t)
        self.redrawzoom()

    def see_time(self, t=None):
        """defaults to current time"""
        if t is None:
            t = self.lastTime
        vis_seconds = self.end - self.start
        margin = vis_seconds * .1
        if t < self.start or t > (self.end - vis_seconds * .3):
            self.offset = t - margin

        self.redrawzoom()

    def see_time_until_end(self, t=None):
        """defaults to current time"""
        if t is None:
            t = self.lastTime
        self.start = t - 2
        self.end = self.maxtime

        self.redrawzoom()
            
    def input_time(self,val):
        self.lastTime = val
        x = self.can_for_t(self.lastTime)
        self.time.set_property("points",
                               GooCanvas.Points([(x, 0),
                                                 (x, self.size.height)]))
        
    def press(self,ev,attr):
        self.adjustingattr = attr
        
    def release(self, widget, ev):
        if hasattr(self,'adjustingattr'):
            del self.adjustingattr
        if hasattr(self,'lastx'):
            del self.lastx
        
    def adjust(self, widget, ev):

        if not hasattr(self,'adjustingattr'):
            return
        attr = self.adjustingattr
        
        if not hasattr(self,'lastx'):
            self.lastx = ev.x
        new = self.can_for_t(getattr(self,attr)) + (ev.x - self.lastx)
        self.lastx = ev.x
        setattr(self,attr,self.t_for_can(new))
        self.redrawzoom()

    def can_for_t(self,t):
        a, b = self.mintime, self.maxtime
        return (t - a) / (b - a) * (self.size.width - 30) + 20
    def t_for_can(self,x):
        a, b = self.mintime, self.maxtime
        return (x - 20) / (self.size.width - 30) * (b - a) + a

    def redrawzoom(self,*args):
        """redraw pieces based on start/end"""
        self.size = self.widget.get_allocation()
        dispatcher.send("zoom changed")
        if not hasattr(self,'created'):
            return
        y1, y2 = 3, self.size.height - 3
        lip = 6
        scan = self.can_for_t(self.start)
        ecan = self.can_for_t(self.end)

        self.leftbrack.set_property("points", GooCanvas.Points([
            (scan + lip, y1),
            (scan, y1),
            (scan, y2),
            (scan + lip, y2)]))
        self.rightbrack.set_property("points", GooCanvas.Points([
            (ecan - lip, y1),
            (ecan, y1),
            (ecan, y2),
            (ecan - lip, y2)]))
        self.shade.set_properties(
            x=scan + 5,
            y=y1 + lip,
            width=max(0, ecan - 5 - (scan + 5)),
            height=max(0, y2 - lip - (y1 + lip)))

        self.redrawTics()
        
    def redrawTics(self):
        if hasattr(self, 'ticsGroup'):
            self.ticsGroup.remove()
        self.ticsGroup = GooCanvas.Group(parent=self.root)

        lastx =- 1000

        for t in range(0,int(self.maxtime)):
            x = self.can_for_t(t)
            if 0 < x < self.size.width and x - lastx > 30:
                txt = str(t)
                if lastx == -1000:
                    txt = txt + "sec"
                GooCanvas.Polyline(parent=self.ticsGroup,
                                   points=GooCanvas.Points([(x, 0), (x, 15)]),
                                   line_width=.8,
                                   stroke_color='black')
                GooCanvas.Text(parent=self.ticsGroup,
                               x=x, y=self.size.height-1,
                               anchor=Gtk.ANCHOR_SOUTH,
                               text=txt,
                               font='ubuntu 7')
                lastx = x


class RegionZoom:
    """rigs c-a-b1 to drag out an area to zoom to. also catches other types of drag events, like b1 drag for selecting points

    this is used with Curveview
    """
    def __init__(self, canvas, world_from_screen, screen_from_world):
        self.canvas, self.world_from_screen = canvas, world_from_screen
        self.screen_from_world = screen_from_world

        for evtype, method in [("ButtonPress-1",self.press),
                               ("Motion",self.motion),
                               ("ButtonRelease-1",self.release)]:
            #canvas.bind("<Control-Alt-%s>" % evtype, method, add=True)
            if 1 or evtype != "ButtonPress-1":
                canvas.bind("<%s>" % evtype, method,add=True)

        canvas.bind("<Leave>", self.finish)
        self.start_t = self.old_cursor = None
        self.state = self.mods = None

    def press(self,ev):
        if self.state is not None:
            self.finish()

        if ev.state == 12:
            self.mods = "c-a"
        elif ev.state == 13:
            # todo: right now this never happens because only the
            # sketching handler gets the event
            self.mods = "c-s-a"
        elif ev.state == 0:
            return # no 
            self.mods = "none"
        else:
            return
        self.state = "buttonpress"
            
        self.start_t = self.end_t = self.world_from_screen(ev.x,0)[0]
        self.start_x = ev.x
        can = self.canvas

        for pos in ('start_t','end_t','hi','lo'):
            can.create_line(0,0,50,50, width=3, fill='yellow',
                            tags=("regionzoom",pos))
        # if updatelines isn't called here, subsequent updatelines
        # will fail for reasons i don't understand
        self.updatelines()

        # todo: just holding the modifiers ought to turn on the zoom
        # cursor (which is not finished)
        cursors.push(can, "@light9/cursor1.xbm")
        
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
            if self.mods in ("c-a", "c-s-a"):
                factor = 1/1.5
                if self.mods == "c-s-a":
                    factor = 1.5 # c-s-a-b1 zooms out
                dispatcher.send("zoom about mouse",
                                t=self.start_t,
                                factor=factor)

            self.finish()
            return

        start,end = min(self.start_t, self.end_t),max(self.start_t, self.end_t)
        if self.mods == "c-a":
            dispatcher.send("zoom to range", start=start, end=end)
        elif self.mods == "none":
            dispatcher.send("select between", start=start, end=end)
        self.finish()
        
    def finish(self, *ev):
        if self.state is not None:
            self.state = None
            self.canvas.delete("regionzoom")
            self.start_t = None
            cursors.pop(self.canvas)
