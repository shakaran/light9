from __future__ import division
import math, time, logging

from gi.repository import Gtk
from gi.repository import GObject

from gi.repository import GooCanvas
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
        finalPoints = pts[:]

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
            finalPoints.remove(pts[i])

        # the simplified curve may now be too far away from some of
        # the points, so we'll put them back. this has an unfortunate
        # bias toward reinserting the earlier points
        for i in to_remove:
            p = pts[i]
            if abs(self.curveview.curve(p[0]) - p[1]) > .1:
                self.curveview.add_point(p)
                finalPoints.append(p)
            
        self.curveview.update_curve()
        self.curveview.select_points(finalPoints)

class Curveview(object):
    """
    graphical curve widget only. Please pack .widget
    """
    def __init__(self, curve, knobEnabled=False, isMusic=False,
                 zoomControl=None):
        """knobEnabled=True highlights the previous key and ties it to a
        hardware knob"""

        self.rebuild()
        
        self.redrawsEnabled = False
        self.curve = curve
        self.knobEnabled = knobEnabled
        self._isMusic = isMusic
        self.zoomControl = zoomControl
        self._time = -999
        self.last_mouse_world = None
        self.culled = False # have we been putting off updates?
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


        # todo: hold control to get a [+] cursor
        #        def curs(ev):
        #            print ev.state
        #        self.bind("<KeyPress>",curs)
        #        self.bind("<KeyRelease-Control_L>",lambda ev: curs(0))
        
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

    def rebuild(self):
        """
        sometimes after windows get resized, canvas gets stuck with a
        weird offset. I can't find where it is, so for now we support
        rebuilding the canvas widget
        """
        if hasattr(self, 'widget'):
            self.widget.destroy()
            print "rebuilding canvas"

        self.timelineLine = self.curveGroup = None
        self.widget = gtk.EventBox()
        self.widget.set_can_focus(True)
        self.widget.add_events(gtk.gdk.KEY_PRESS_MASK |
                               gtk.gdk.FOCUS_CHANGE_MASK)
        self.onFocusOut()

        box = gtk.VBox()
        box.set_border_width(1)
        self.widget.add(box)
        box.show()
        
        self.canvas = goocanvas.Canvas()
        box.pack_start(self.canvas)
        self.canvas.show()
        
        self.canvas.set_property("background-color", "black")
        self.size = self.canvas.get_allocation()
        self.root = self.canvas.get_root_item()

        self.canvas.connect("size-allocate", self.update_curve)
        self.canvas.connect("expose-event", self.onExpose)

        self.canvas.connect("leave-notify-event", self.onLeave)
        self.canvas.connect("enter-notify-event", self.onEnter)
        self.canvas.connect("motion-notify-event", self.onMotion)
        self.canvas.connect("scroll-event", self.onScroll)
        self.canvas.connect("button-release-event", self.onRelease)
        self.root.connect("button-press-event", self.onCanvasPress)

        self.widget.connect("key-press-event", self.onKeyPress)

        self.widget.connect("focus-in-event", self.onFocusIn)
        self.widget.connect("focus-out-event", self.onFocusOut)
        self.widget.connect("event", self.onAny)

    def onAny(self, w, event):
        print "   %s on %s" % (event, w)
        
    def onFocusIn(self, *args):
        print "focusin", args
        self.widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))

    def onFocusOut(self, widget=None, event=None):
        #if event:
        #    import pdb;pdb.set_trace()
        print "focusout now", event.get_state() if event else 0

    def onKeyPress(self, *args):
        print "canvas key", args

    def onExpose(self, *args):
        if self.culled:
            self.update_curve()

    def onDelete(self):
        if self.selected_points:
            self.remove_point_idx(*self.selected_points)
        
            
    def onCanvasPress(self, item, target_item, event):
        # when we support multiple curves per canvas, this should find
        # the close one and add a point to that. Binding to the line
        # itself is probably too hard to hit. Maybe a background-color
        # really thick line would be a nice way to allow a sloppier
        # click

        print "focus on", self.widget
        self.widget.grab_focus()
        print "done grab"
        
        if event.get_state() & gtk.gdk.CONTROL_MASK:
            self.new_point_at_mouse(event)
        elif event.get_state() & gtk.gdk.SHIFT_MASK:
            self.sketch_press(event)
        else:
            self.select_press(event)

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
        # maybe self.canvas.get_pointer would be ok for this? i didn't try it
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

    def select_points(self, pts):
        """set selection to the given point values (tuples, not indices)"""
        idxs = []
        for p in pts:
            idxs.append(self.curve.points.index(p))
        self.select_indices(idxs)

    def select_indices(self, idxs):
        """set selection to these point indices"""
        self.selected_points = idxs
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
            #cursors.push(self,"gumby")
        
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
        #cursors.pop(self)
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

    def _coords(self):
        z = self.zoomControl
        ht = self.size.height
        marginBottom = 3 if ht > 40 else 0
        marginTop = marginBottom
        return z, ht, marginBottom, marginTop
        
    def screen_from_world(self,p):
        z, ht, marginBottom, marginTop = self._coords()
        return ((p[0] - z.start) / (z.end - z.start) * self.size.width,
                (ht - marginBottom) - p[1] * (ht - (marginBottom + marginTop)))

    def world_from_screen(self,x,y):
        z, ht, marginBottom, marginTop = self._coords()
        return (x / self.size.width * (z.end - z.start) + z.start,
                ((ht - marginBottom) - y) / (ht - (marginBottom + marginTop)))

    def input_time(self, val, forceUpdate=False):
        if self._time == val:
            return
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

    def canvasIsVisible(self):
        if not hasattr(self, "scrollWin"):
            self.scrollWin = self.canvas
            while not isinstance(self.scrollWin, gtk.ScrolledWindow):
                self.scrollWin = self.scrollWin.get_parent()

        sw = self.scrollWin
        top = sw.get_toplevel()
        visy1 = sw.translate_coordinates(top, 0, 0)[1]
        visy2 = visy1 + sw.get_allocation().height

        coords = self.canvas.translate_coordinates(top, 0, 0)
        if not coords: # probably broken after a reload()
            return False
        cany1 = coords[1]
        cany2 = cany1 + self.canvas.get_allocation().height
        return not (cany2 < visy1 or cany1 > visy2)
        
    def update_curve(self, *args):
        if not self.redrawsEnabled:
            return

        if not self.canvasIsVisible():
            self.culled = True
            return
        self.culled = False
        
        self.size = self.canvas.get_allocation()
 
        cp = self.curve.points
        visible_x = (self.world_from_screen(0,0)[0],
                     self.world_from_screen(self.size.width, 0)[0])

        visible_idxs = self.curve.indices_between(visible_x[0], visible_x[1],
                                                  beyond=1)
        visible_points = [cp[i] for i in visible_idxs]

        if getattr(self, 'curveGroup', None):
            self.curveGroup.remove()
        self.curveGroup = goocanvas.Group(parent=self.root)

        # this makes gtk quietly stop working. Getting called too early?
        #self.canvas.set_property("background-color",
        #                         "gray20" if self.curve.muted else "black")

        if self.size.height < 40:
            #self._draw_gradient()
            self._draw_line(visible_points, area=True)
        else:
            self._draw_markers(visible_x)
            self._draw_line(visible_points)

            self.dots = {} # idx : canvas rectangle

            if len(visible_points) < 50 and not self.curve.muted:
                self._draw_handle_points(visible_idxs,visible_points)

    def is_music(self):
        """are we one of the music curves (which might be drawn a bit
        differently)"""
        return self._isMusic
 
    def _draw_gradient(self):
        # not yet ported
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

    def _draw_line(self, visible_points, area=False):
        linepts=[]
        step=1
        linewidth = 1.5
        maxPointsToDraw = self.size.width / 2
        if len(visible_points) > maxPointsToDraw:
            step = int(len(visible_points) / maxPointsToDraw)
            linewidth = .8
        for p in visible_points[::step]:
            x,y = self.screen_from_world(p)
            linepts.append((int(x) + .5, int(y) + .5))

        if self.curve.muted:
            fill = 'grey34'
        else:
            fill = 'white'

        if area:
            base = self.screen_from_world((0, 0))[1]
            base = base + linewidth / 2
            goocanvas.Polyline(parent=self.curveGroup,
                               points=goocanvas.Points(
                                   [(linepts[0][0], base)] +
                                   linepts +
                                   [(linepts[-1][0], base)]),
                               close_path=True,
                               line_width=0,
                               fill_color="green",
                               )

        self.pl = goocanvas.Polyline(parent=self.curveGroup,
                                     points=goocanvas.Points(linepts),
                                     line_width=linewidth,
                                     stroke_color=fill,
                                     )
                
            
    def _draw_handle_points(self,visible_idxs,visible_points):
        for i,p in zip(visible_idxs,visible_points):
            rad=3
            worldp = p
            p = self.screen_from_world(p)
            dot = goocanvas.Rect(parent=self.curveGroup,
                                 x=int(p[0] - rad) + .5,
                                 y=int(p[1] - rad) + .5,
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
        x = p[0]
        y = self.curve.eval(x)
        self.add_point((x, y))

    def add_point(self, p):
        i = self.curve.insert_pt(p)
        self.update_curve()
        self.select_indices([i])
        
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
                d.set_property('fill_color', 'red')
            else:
                d.set_property('fill_color', 'blue')
        
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
        self.select_indices(self.curve.indices_between(start,end))

    def onEnter(self, widget, event):
        self.entered = True

    def onLeave(self, widget, event):
        self.entered = False

    def onMotion(self, widget, event):
        self.lastMouseX = event.x

        if event.state & gtk.gdk.SHIFT_MASK and 1: # and B1
            self.sketch_motion(event)
            return

        self.select_motion(event)
        
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

        if event.state & gtk.gdk.SHIFT_MASK: # relese-B1
            self.sketch_release(event)
            return

        self.select_release(event)
 
        if not self.dragging_dots:
            return
        self.last_mouse_world = None
        self.dragging_dots = False

class CurveRow(object):
    """
    one of the repeating curve rows (including widgets on the left)

    i wish these were in a list-style TreeView so i could set_reorderable on it

    please pack self.box
    """
    def __init__(self, name, curve, slider, knobEnabled, zoomControl):
        self.name = name
        self.box = gtk.VBox()
        self.box.set_border_width(1)

        self.cols = gtk.HBox()
        self.box.add(self.cols)
        
        controls = gtk.Frame()
        controls.set_size_request(115, -1)
        controls.set_shadow_type(gtk.SHADOW_OUT)
        self.cols.pack_start(controls, expand=False)
        self.setupControls(controls, name, curve, slider)

        self.curveView = Curveview(curve, knobEnabled=knobEnabled,
                                   isMusic=name in ['music', 'smooth_music'],
                                   zoomControl=zoomControl)
        self.initCurveView()

    def rebuild(self):
        self.curveView.rebuild()
        self.initCurveView()

    def initCurveView(self):
        self.curveView.widget.show()
        self.curveView.widget.set_size_request(-1, 100)
        self.cols.pack_start(self.curveView.widget, expand=True)       
        
    def setupControls(self, controls, name, curve, slider):
        box = gtk.VBox()
        controls.add(box)
        
        txt = "curve '%s'" % name
        if len(name) > 7:
            txt = name
        curve_name_label = gtk.Label(txt)
        box.pack_start(curve_name_label)

        bools = gtk.HBox()
        box.pack_start(bools)
        self.collapsed = gtk.CheckButton("C")
        bools.pack_start(self.collapsed)
        self.collapsed.connect("toggled", self.update_ui_to_collapsed_state)
        self.hideWhenCollapsed = [bools]
        self.muted = gtk.CheckButton("M")
        
        bools.pack_start(self.muted)
        self.muted.connect("toggled", self.sync_mute_to_curve)
        dispatcher.connect(self.mute_changed, 'mute changed', sender=curve)

        self.sliderLabel = None
        if slider is not None:
            # slider should have a checkbutton, defaults to off for
            # music tracks
            self.sliderLabel = gtk.Label("Slider %s" % slider)
            box.pack_start(self.sliderLabel)

        # widgets that need recoloring when we tint the row:
        #self.widgets = [leftside, self.collapsed, self.muted,
        #                curve_name_label, self]
        #if self.sliderLabel:
        #    self.widgets.append(self.sliderLabel)

    def onDelete(self):
        self.curveView.onDelete()
        
    def update_ui_to_collapsed_state(self, *args):
        if self.collapsed.get_active():
            self.curveView.widget.set_size_request(-1, 25)
            [w.hide() for w in self.hideWhenCollapsed]
        else:
            self.curveView.widget.set_size_request(-1, 100)
            [w.show() for w in self.hideWhenCollapsed]

    def sync_mute_to_curve(self, *args):
        """send value from CheckButton to the master attribute inside Curve"""
        new_mute = self.muted.get_active()
        self.curveView.curve.muted = new_mute

    def update_mute_look(self):
        """set colors on the widgets in the row according to self.muted.get()"""
        # not yet ported for gtk
        return
        if self.curveView.curve.muted:
            new_bg = 'grey20'
        else:
            new_bg = 'normal'

        for widget in self.widgets:
            widget['bg'] = new_bg

    def mute_changed(self):
        """call this if curve.muted changed"""
        self.muted.set_active(self.curveView.curve.muted)
        #self.update_mute_look()


class Curvesetview(object):
    """
    
    """
    def __init__(self, curvesVBox, zoomControlBox, curveset):
        self.live = True
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

        eventBox = self.curvesVBox.get_parent()
        eventBox.connect("key-press-event", self.onKeyPress)
        eventBox.connect("button-press-event", self.takeFocus)

    def __del__(self):
        print "del curvesetview", id(self) 

    def takeFocus(self, *args):
        """the whole curveset's eventbox is what gets the focus, currently, so
        keys like 'c' can work in it"""
        self.curvesVBox.get_parent().grab_focus()

    def onKeyPress(self, widget, event):
        if not self.live: # workaround for old instances living past reload()
            return

        if event.string == 'c':
            r = self.row_under_mouse()
            # calling toggled() had no effect; don't know why
            r.collapsed.set_active(not r.collapsed.get_active())
        if event.string == 'r':
            r = self.row_under_mouse()
            r.rebuild()
 
    def row_under_mouse(self):
        x, y = self.curvesVBox.get_pointer()
        for r in self.allCurveRows:
            inRowX, inRowY = self.curvesVBox.translate_coordinates(r.box, x, y)
            _, _, w, h = r.box.get_allocation()
            if 0 <= inRowX < w and 0 <= inRowY < h:
                return r
        raise ValueError("no curveRow is under the mouse")

    def focus_entry(self):
        self.entry.focus()

    def new_curve(self, event):
        self.curveset.new_curve(self.newcurvename.get())
        self.newcurvename.set('')
        
    def add_curve(self, name, slider=None, knobEnabled=False):
        curve = self.curveset.curves[name]
        f = CurveRow(name, curve, slider, knobEnabled, self.zoomControl)
        self.curvesVBox.pack_start(f.box)
        f.box.show_all()
        self.allCurveRows.add(f)
        f.curveView.goLive()

    def row(self, name):
        return [r for r in self.allCurveRows if r.name == name][0]

    def goLive(self):
        """for startup performance, none of the curves redraw
        themselves until this is called once (and then they're normal)"""
        
        for cr in self.allCurveRows:
            cr.curveView.goLive()

    def onDelete(self):
        for r in self.allCurveRows:
            r.onDelete()

    def collapseAll(self):
        for r in self.allCurveRows:
            r.collapsed.set_active(True)

    def collapseNone(self):
        for r in self.allCurveRows:
            r.collapsed.set_active(False)

        
