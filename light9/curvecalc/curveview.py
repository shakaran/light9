from __future__ import division
import math, time, logging
import gtk, goocanvas
import louie as dispatcher
from light9.curvecalc.zoomcontrol import RegionZoom
from light9.curvecalc import cursors
from light9.curvecalc.curve import introPad, postPad
from light9.dmxchanedit import gradient

log = logging.getLogger()
print "curveview.py toplevel"
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

class Curveview(object):
    """
    graphical curve widget only. Please pack .widget
    """
    def __init__(self, curve, knobEnabled=False, isMusic=False, zoomControl=None, **kw):
        """knobEnabled=True highlights the previous key and ties it to a
        hardware knob"""
        self.widget = goocanvas.Canvas()
        self.widget.set_property("background-color", "black")
        self.widget.set_size_request(-1, 100)
        self.size = self.widget.get_allocation()
        self.root = self.widget.get_root_item()

        self.redrawsEnabled = False
        self.curve = curve
        self.knobEnabled = knobEnabled
        self._isMusic = isMusic
        self.zoomControl = zoomControl
        self._time = 0
        self.last_mouse_world = None
        self.entered = False # is the mouse currently over this widget
        self.selected_points=[] # idx of points being dragged
        # self.bind("<Enter>",self.focus)
        dispatcher.connect(self.playPause, "onPlayPause")
        dispatcher.connect(self.input_time, "input time")
        dispatcher.connect(self.update_curve, "zoom changed")
        dispatcher.connect(self.update_curve, "points changed",
                           sender=self.curve)
        dispatcher.connect(self.update_curve, "mute changed", 
                           sender=self.curve)
        dispatcher.connect(self.select_between, "select between")
        if self.knobEnabled:
            dispatcher.connect(self.knob_in, "knob in")
            dispatcher.connect(self.slider_in, "set key")

        self.widget.connect("size-allocate", self.update_curve)

        self.widget.connect("leave-notify-event", self.onLeave)
        self.widget.connect("enter-notify-event", self.onEnter)
        self.widget.connect("motion-notify-event", self.onMotion)
        self.widget.connect("scroll-event", self.onScroll)
        self.widget.connect("button-release-event", self.onRelease)
        
        if 0:

            for x in range(1, 6):
                def add_kb_marker_point(evt, x=x):
                    self.add_point((self.current_time(), (x - 1) / 4.0))

                self.bind("<Key-%s>" % x, add_kb_marker_point)

        # this binds on c-a-b1, etc
        if 0:
            self.regionzoom = RegionZoom(self, self.world_from_screen,
                                         self.screen_from_world)

        self.sketch = None # an in-progress sketch
        if 0:
            self.bind("<Shift-ButtonPress-1>", self.sketch_press)
            self.bind("<Shift-B1-Motion>", self.sketch_motion)
            self.bind("<Shift-ButtonRelease-1>", self.sketch_release)


        self.dragging_dots = False
        self.selecting = False
        if 0:
            self.bind("<ButtonPress-1>",#"<Alt-Key>",
                      self.select_press, add=True)
            self.bind("<Motion>", self.select_motion, add=True)
            self.bind("<ButtonRelease-1>", #"<Alt-KeyRelease>",
                      self.select_release, add=True)

            self.bind("<ButtonPress-1>", self.check_deselect, add=True)

            self.bind("<Key-m>", lambda *args: self.curve.toggleMute())
            self.bind("<Key-c>", lambda *args: dispatcher.send('toggle collapse',
                                                               sender=self.curve))

    def playPause(self):
        """
        user has pressed ctrl-p over a curve view, possibly this
        one. Returns the time under the mouse if we know it, or else
        None

        todo: there should be a faint timecursor line under the mouse
        so it's more obvious that we use that time for some
        events. Rt-click should include Ctrl+P as 'play/pause from
        here'
        """
        # maybe self.widget.get_pointer would be ok for this? i didn't try it
        if self.entered:
            t = self.world_from_screen(self.lastMouseX, 0)[0]
            return t
        return None

    def goLive(self):
        """this is for startup performance only, since the curves were
        getting redrawn many times. """
        self.redrawsEnabled = True
        self.update_curve()

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

    def slider_in(self, curve, value=None):
        """user pushed on a slider. make a new key.  if value is None,
        the value will be the same as the last."""
        if curve != self.curve:
            return

        if value is None:
            value = self.curve.eval(self.current_time())

        self.curve.insert_pt((self.current_time(), value))
        self.update_curve()

    def print_state(self, msg=""):
        if 1:
            print "%s: dragging_dots=%s selecting=%s" % (
                msg, self.dragging_dots, self.selecting)

    def check_deselect(self,ev):
        try:
            self.find_index_near(ev.x, ev.y)
        except ValueError:
            self.selected_points[:] = []
            self.highlight_selected_dots()

    def select_press(self,ev):
        # todo: these select_ handlers are getting called on c-a-drag
        # zooms too. the dispatching should be more selective than
        # just calling both handlers all the time
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
        z = self.zoomControl
        ht = self.size.height
        return (p[0]-z.start)/(z.end-z.start)*self.size.width, (ht-5)-p[1]*(ht-10)

    def world_from_screen(self,x,y):
        z = self.zoomControl
        ht = self.size.height
        return x/self.size.width*(z.end-z.start)+z.start, ((ht-5)-y)/(ht-10)

    def input_time(self, val, forceUpdate=False):
        # i tried various things to make this not update like crazy,
        # but the timeline was always missing at startup, so i got
        # scared that things were getting built in a funny order.        
        #if self._time == val:
        #    return
        t=val

        if not getattr(self, 'timelineLine', None):
            self.timelineGroup = goocanvas.Group(parent=self.root)
            self.timelineLine = goocanvas.Polyline(
                parent=self.timelineGroup,
                points=goocanvas.Points([(0,0), (0,0)]),
                line_width=2, stroke_color='red')

        self.timelineLine.set_property('points', goocanvas.Points([
            self.screen_from_world((val,0)),
            self.screen_from_world((val,1))]))
        
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
        
    def update_curve(self, _widget=None, _rect=None):
        if not self.redrawsEnabled:
            return
        self.size = self.widget.get_allocation()
 
        cp = self.curve.points
        visible_x = (self.world_from_screen(0,0)[0],
                     self.world_from_screen(self.size.width, 0)[0])

        visible_idxs = self.curve.indices_between(visible_x[0], visible_x[1],
                                                  beyond=1)
        visible_points = [cp[i] for i in visible_idxs]

        if getattr(self, 'curveGroup', None):
            self.curveGroup.remove()
        self.curveGroup = goocanvas.Group(parent=self.root)

        if 0:
            if self.curve.muted:
                self['bg'] = 'grey20'
            else:
                self['bg'] = 'black'

        if self.size.height < .40:
            self._draw_gradient()
        else:
            self._draw_markers(visible_x)
            self._draw_line(visible_points)

            self.dots = {} # idx : canvas rectangle

            if len(visible_points)<50:
                self._draw_handle_points(visible_idxs,visible_points)

    def is_music(self):
        """are we one of the music curves (which might be drawn a bit
        differently)"""
        return self._isMusic
 
    def _draw_gradient(self):
        print "no grad"
        return
        t1 = time.time()
        gradient_res = 6 if self.is_music() else 3
        startX = startColor = None
        rects = 0
        for x in range(0, self.size.width, gradient_res):
            wx = self.world_from_screen(x,0)[0]
            mag = self.curve.eval(wx, allow_muting=False)
            if self.curve.muted:
                low = (8, 8, 8)
                high = (60, 60, 60)
            else:
                low = (20, 10, 50)
                high = (255, 187, 255)
            color = gradient(mag, low=low, high=high)
            if color != startColor:
                if startColor is not None:
                    self._draw_gradient_slice(startX, x, startColor)
                    rects += 1
                startX = x
                startColor = color

        if startColor is not None:
            self._draw_gradient_slice(startX, self.size.width, startColor)
            rects += 1
        log.debug("redraw %s rects in %.02f ms", rects, 1000 * (time.time()-t1))

    def _draw_gradient_slice(self, x1, x2, color):
        self.create_rectangle(x1, 0, x2, 40,
                              fill=color, width=0, tags='curve')        

    def _draw_markers(self,visible_x):
        mark = self._draw_one_marker

        mark(0, "0")
        t1,t2=visible_x
        if t2-t1<30:
            for t in range(int(t1),int(t2)+1):
                mark(t,str(t))
        mark(introPad, str(introPad))

        endtimes = dispatcher.send("get max time")
        if endtimes:
            endtime = endtimes[0][1]
            mark(endtime, "end %.1f"%endtime)
            mark(endtime - postPad, "post %.1f" % (endtime - postPad))
        
    def _draw_one_marker(self,t,label):
        x = self.screen_from_world((t,0))[0]
        ht = self.size.height
        if not 0 <= x < self.size.width:
            return
        x = max(5, x) # cheat left-edge stuff onscreen
        goocanvas.polyline_new_line(self.curveGroup,
                                    x, ht,
                                    x, ht - 20,
                                    line_width=.5,
                                    stroke_color='gray70')
        goocanvas.Text(parent=self.curveGroup,
                       fill_color="white",
                       anchor=gtk.ANCHOR_SOUTH,
                       font="ubuntu 7",
                       x=x+3, y=ht-20,
                       text=label)

    def _draw_line(self,visible_points):
        linepts=[]
        step=1
        linewidth = 1.5
        maxPointsToDraw = self.size.width / 2
        if len(visible_points) > maxPointsToDraw:
            step = int(len(visible_points) / maxPointsToDraw)
            linewidth = .8
        for p in visible_points[::step]:
            linepts.append(self.screen_from_world(p))

        if self.curve.muted:
            fill = 'grey34'
        else:
            fill = 'white'

        self.pl = goocanvas.Polyline(parent=self.curveGroup,
                                     points=goocanvas.Points(linepts),
                                     line_width=linewidth,
                                     stroke_color=fill,
                                     )
            
        # canvas doesnt have keyboard focus, so i can't easily change the
        # cursor when ctrl is pressed
        #        def curs(ev):
        #            print ev.state
        #        self.bind("<KeyPress>",curs)
        #        self.bind("<KeyRelease-Control_L>",lambda ev: curs(0))
        if 0:
            self.tag_bind(line,"<Control-ButtonPress-1>",self.new_point_at_mouse)


    def _draw_handle_points(self,visible_idxs,visible_points):
        for i,p in zip(visible_idxs,visible_points):
            rad=3
            worldp = p
            p = self.screen_from_world(p)
            dot = goocanvas.Rect(parent=self.curveGroup,
                                 x=p[0] - rad, y=p[1] - rad,
                                 width=rad * 2, height=rad * 2,
                                 stroke_color='gray90',
                                 fill_color='blue',
                                 line_width=1,
                                 #tags=('curve','point', 'handle%d' % i)
                                 )
            if worldp[1] == 0:
                rad += 3
                goocanvas.Ellipse(parent=self.curveGroup,
                                  center_x=p[0],
                                  center_y=p[1],
                                  radius_x=rad,
                                  radius_y=rad,
                                  line_width=2,
                                  stroke_color='#00a000',
                                  #tags=('curve','point', 'handle%d' % i)
                                  )
            dot.connect("button-press-event", self.dotpress, i)
            #self.tag_bind('handle%d' % i,"<ButtonPress-1>",
            #              lambda ev,i=i: self.dotpress(ev,i))
            #self.tag_bind('handle%d' % i, "<Key-d>",
            #              lambda ev, i=i: self.remove_point_idx(i))
                      
            self.dots[i]=dot

        def delpoint(ev):
            # had a hard time tag_binding to the points, so i trap at
            # the widget level (which might be nice anyway when there
            # are multiple pts selected)
            if self.selected_points:
                self.remove_point_idx(*self.selected_points)
        #self.bind("<Key-Delete>", delpoint)

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
        return
        for i,d in self.dots.items():
            if i in self.selected_points:
                self.itemconfigure(d,fill='red')
            else:
                self.itemconfigure(d,fill='blue')
        
    def dotpress(self, r1, r2, ev, dotidx):
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

    def onEnter(self, widget, event):
        self.entered = True

    def onLeave(self, widget, event):
        self.entered = False

    def onMotion(self, widget, event):
        self.lastMouseX = event.x
        
        if not self.dragging_dots:
            return
        if not event.state & 256:
            return # not lmb-down
        cp = self.curve.points
        moved=0

        cur = self.world_from_screen(event.x, event.y)
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

    def onScroll(self, widget, event):
        t = self.world_from_screen(event.x, 0)[0]
        self.zoomControl.zoom_about_mouse(
            t, factor=1.5 if event.direction == gtk.gdk.SCROLL_DOWN else 1/1.5)
        
    def onRelease(self, widget, event):
        self.print_state("dotrelease")
        if not self.dragging_dots:
            return
        self.last_mouse_world = None
        self.dragging_dots = False

class CurveRow(object):
    """
    one of the repeating curve rows (including widgets on the left)

    please pack self.box
    """
    def __init__(self, name, curve, slider, knobEnabled, zoomControl):
        self.box = gtk.HandleBox()
        self.box.set_border_width(1)

        cols = gtk.HBox()
        self.box.add(cols)
        
        controls = gtk.Frame()
        controls.set_size_request(115, -1)
        controls.set_shadow_type(gtk.SHADOW_OUT)
        cols.pack_start(controls, expand=False)
        self.setupControls(controls, name, curve, slider)

        self.curveView = Curveview(curve, knobEnabled=knobEnabled,
                                   isMusic=name in ['music', 'smooth_music'],
                                   zoomControl=zoomControl)
        cols.pack_start(self.curveView.widget, expand=True)
        
    def setupControls(self, controls, name, curve, slider):
        box = gtk.VBox()
        controls.add(box)
        
        txt = "curve '%s'" % name
        if len(name) > 7:
            txt = name
        curve_name_label = gtk.Label(txt)
        box.pack_start(curve_name_label)


#        self.collapsed = tk.IntVar()
#        self.muted = tk.IntVar()

        bools = gtk.HBox()
        box.pack_start(bools)
        collapsed_cb = gtk.CheckButton("C")
        bools.pack_start(collapsed_cb)
        #self.collapsed.trace('w', self.update_ui_to_collapsed_state)
        dispatcher.connect(self.toggleCollapsed, "toggle collapse",
                           sender=curve)

        muted_cb = gtk.CheckButton("M")
        
        bools.pack_start(muted_cb)
        #self.muted.trace('w', self.sync_mute_to_curve)
        dispatcher.connect(self.mute_changed, 'mute changed', sender=curve)

        self.sliderLabel = None
        if slider is not None:
            # slider should have a checkbutton, defaults to off for
            # music tracks
            self.sliderLabel = gtk.Label("Slider %s" % slider)
            box.pack_start(self.sliderLabel)

        # widgets that need recoloring when we tint the row:
        #self.widgets = [leftside, collapsed_cb, muted_cb,
        #                curve_name_label, self]
        #if self.sliderLabel:
        #    self.widgets.append(self.sliderLabel)

    def toggleCollapsed(self):
        self.collapsed.set(not self.collapsed.get())

    def update_ui_to_collapsed_state(self, *args):
        if self.collapsed.get():
            if self.sliderLabel:
                self.sliderLabel.pack_forget()
            self.curveView.config(height=25)
        else:
            if self.sliderLabel:
                self.sliderLabel.pack(side='left')
            self.curveView.config(height=100)

    def sync_mute_to_curve(self, *args):
        """send value from Tk var to the master attribute inside Curve"""
        new_mute = self.muted.get()
        old_mute = self.curveView.curve.muted
        if new_mute == old_mute:
            return

        self.curveView.curve.muted = new_mute

    def update_mute_look(self):
        """set colors on the widgets in the row according to self.muted.get()"""
        if self.muted.get():
            new_bg = 'grey20'
        else:
            new_bg = self.default_bg

        for widget in self.widgets:
            widget['bg'] = new_bg

    def mute_changed(self):
        """call this if curve.muted changed"""
        self.muted.set(self.curveView.curve.muted)
        self.update_mute_look()


class Curvesetview(object):
    """
    
    """
    def __init__(self, curvesVBox, zoomControlBox, curveset):
        self.curvesVBox = curvesVBox
        self.curveset = curveset
        self.allCurveRows = set()

        import light9.curvecalc.zoomcontrol
        reload(light9.curvecalc.zoomcontrol)
        self.zoomControl = light9.curvecalc.zoomcontrol.ZoomControl()
        zoomControlBox.add(self.zoomControl.widget)
        self.zoomControl.widget.show_all()

        for c in curveset.curveNamesInOrder():
            self.add_curve(c) 

        dispatcher.connect(self.add_curve, "add_curve", sender=self.curveset)
        
        self.newcurvename = gtk.EntryBuffer("", 0)
        
        return

        entry = tk.Entry(f, textvariable=self.newcurvename)
        entry.pack(side='left', fill='x',exp=1)        
        entry.bind("<Key-Return>", self.new_curve)
        self.entry = entry
        
        dispatcher.connect(self.focus_entry, "focus new curve")

    def focus_entry(self):
        self.entry.focus()

    def new_curve(self, event):
        self.curveset.new_curve(self.newcurvename.get())
        self.newcurvename.set('')
        
    def add_curve(self, name, slider=None, knobEnabled=False):
        curve = self.curveset.curves[name]
        f = CurveRow(name, curve, slider, knobEnabled, self.zoomControl)
        self.curvesVBox.pack_end(f.box)
        f.box.show_all()
        self.allCurveRows.add(f)
        #f.curveView.goLive()


    def goLive(self):
        """for startup performance, none of the curves redraw
        themselves until this is called once (and then they're normal)"""
        
        for cr in self.allCurveRows:
            cr.curveView.goLive()

