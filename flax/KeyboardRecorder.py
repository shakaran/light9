from __future__ import nested_scopes
import sys, time
sys.path.append('..')
from Widgets.Fadable import Fadable

from Tix import *
import math, atexit, pickle
from sets import Set
from Submaster import Submasters, sub_maxes
import dmxclient
from uihelpers import toplevelat

# idea is that one system handles all the level logging persistence
# (it also needs to know which song we're currently working on)
# SubLevelLogger is not yet written
from SubLevelLogger import SubLevelLogger

nudge_keys = {
    'up' : list('qwertyuiop'),
    'down' : list('asdfghjkl')
}
nudge_keys['down'].append('semicolon')

class SubScale(Scale, Fadable):
    def __init__(self, master, *args, **kw):
        self.scale_var = kw.get('variable') or DoubleVar()
        kw.update({'variable' : self.scale_var,
                   'from' : 1, 'to' : 0, 'showvalue' : 0,
                   'sliderlength' : 15, 'res' : 0.01,
                   'width' : 40, 'troughcolor' : 'black', 'bg' : 'grey40',
                   'highlightthickness' : 1, 'bd' : 1,
                   'highlightcolor' : 'red', 'highlightbackground' : 'black',
                   'activebackground' : 'red'})
        Scale.__init__(self, master, *args, **kw)
        Fadable.__init__(self, var=self.scale_var, wheel_step=0.05)
        self.draw_indicator_colors()
    def draw_indicator_colors(self):
        if self.scale_var.get() == 0:
            self['troughcolor'] = 'black'
        else:
            self['troughcolor'] = 'blue'

class SubmasterTk(Frame):
    def __init__(self, master, name, current_level, kbrecorder=None):
        """kbrecorder is a KeyboardRecorder instance -- take that, Java"""
        Frame.__init__(self, master, bd=1, relief='raised', bg='black')
        self.slider_var = DoubleVar()
        self.slider_var.set(current_level)
        self.scale = SubScale(self, variable=self.slider_var, width=20)
        self.namelabel = Label(self, text=name, font="Arial 8", bg='black',
            fg='white')
        self.namelabel.pack(side=TOP)
        self.levellabel = Label(self, 
            font="Arial 8", bg='black', fg='white')
        self.levellabel.pack(side=TOP)
        self.scale.pack(side=BOTTOM, expand=1, fill=BOTH)

        # recording bits
        self.kbrecorder = kbrecorder
        self.recording = 0
        self.name = name
        self._last_recorded_value = None
        for obj in (self, self.levellabel, self.namelabel, self.scale):
            obj.bind('<3>', self.toggle_record)

        self.slider_var.trace('w', self.draw_level)
        self.draw_level()
    def draw_level(self, *args):
        self.levellabel['text'] = "%d" % (self.slider_var.get() * 100)
    def toggle_record(self, evt):
        self.kbrecorder.toggle_sub_recording(self.name)
        self.recording = not self.recording
        if self.recording:
            conf = {'bg' : 'red'}
        else:
            conf = {'bg' : 'black'}

        for obj in (self, self.levellabel, self.namelabel):
            obj.config(**conf)
    def record(self, timestamp):
        """This is called whenever we get a timestamp and we're recording."""
        new_value = self.scale.scale_var.get()
        if new_value != self._last_recorded_value:
            s = SubLevelLogger()
            s.save_level(name, timestamp, new_value)

        self._last_recorded_value = new_value
    def get_recorded_level(self, timestamp):
        """This is called whenever we get a timestamp and we're not 
        recording.
        
        TODO: independent subs don't playback from recorded levels"""
        s = SubLevelLogger()
        new_value = s.load_level(name, timestamp)
        self.scale.scale_var.set(new_value)

class KeyboardRecorder(Frame):
    def __init__(self, root, submasters, current_sub_levels=None, dmxdummy=0):
        Frame.__init__(self, root, bg='black')
        self.submasters = submasters
        self.dmxdummy = dmxdummy

        self.current_sub_levels = {}
        if current_sub_levels:
            self.current_sub_levels = current_sub_levels
        else:
            try:
                self.current_sub_levels = \
                    pickle.load(file('.keyboardcomposer.savedlevels'))
            except IOError:
                pass

        self.subs_being_recorded = Set() # yay, this is the first time I've
                                         # used Set!

        self.draw_ui()
        self.send_levels_loop()
    def draw_ui(self):
        self.rows = [] # this holds Tk Frames for each row
        self.slider_vars = {} # this holds subname:sub Tk vars
        self.slider_table = {} # this holds coords:sub Tk vars
        self.name_to_subtk = {} # subname : SubmasterTk instance
        self.current_row = 0
        
        self.make_key_hints()
        self.draw_sliders()
        self.highlight_row(self.current_row)
        self.rows[self.current_row].focus()

        self.buttonframe = Frame(self, bg='black')
        self.buttonframe.pack(side=BOTTOM)
        self.refreshbutton = Button(self.buttonframe, text="Refresh", 
            command=self.refresh, bg='black', fg='white')
        self.refreshbutton.pack(side=LEFT)
        self.save_stage_button = Button(self.buttonframe, text="Save", 
            command=lambda: self.save_current_stage(self.sub_name.get()), 
            bg='black', fg='white')
        self.save_stage_button.pack(side=LEFT)
        self.sub_name = Entry(self.buttonframe, bg='black', fg='white')
        self.sub_name.pack(side=LEFT)
        self.stop_frequent_update_time = 0
    def make_key_hints(self):
        keyhintrow = Frame(self)

        col = 0
        for upkey, downkey in zip(nudge_keys['up'],
                                  nudge_keys['down']):
            # what a hack!
            downkey = downkey.replace('semicolon', ';')
            upkey, downkey = (upkey.upper(), downkey.upper())

            # another what a hack!
            keylabel = Label(keyhintrow, text='%s\n%s' % (upkey, downkey), 
                width=1, font=('Arial', 10), bg='red', fg='white', anchor='c')
            keylabel.pack(side=LEFT, expand=1, fill=X)
            col += 1

        keyhintrow.pack(fill=X, expand=0)
        self.keyhints = keyhintrow
    def setup_key_nudgers(self, tkobject):
        for d, keys in nudge_keys.items():
            for key in keys:
                # lowercase makes full=0
                keysym = "<KeyPress-%s>" % key
                tkobject.bind(keysym, \
                    lambda evt, num=keys.index(key), d=d: \
                        self.got_nudger(num, d))

                # uppercase makes full=1
                keysym = "<KeyPress-%s>" % key.upper()
                keysym = keysym.replace('SEMICOLON', 'colon')
                tkobject.bind(keysym, \
                    lambda evt, num=keys.index(key), d=d: \
                        self.got_nudger(num, d, full=1))

        # Row changing:
        # Page dn, C-n, and ] do down
        # Page up, C-p, and ' do up
        for key in '<Prior> <Next> <Control-n> <Control-p> ' \
                   '<Key-bracketright> <Key-apostrophe>'.split():
            tkobject.bind(key, self.change_row)

    def change_row(self, event):
        diff = 1
        if event.keysym in ('Prior', 'p', 'bracketright'):
            diff = -1
        old_row = self.current_row
        self.current_row += diff
        self.current_row = max(0, self.current_row)
        self.current_row = min(len(self.rows) - 1, self.current_row)
        self.unhighlight_row(old_row)
        self.highlight_row(self.current_row)
        row = self.rows[self.current_row]
        self.keyhints.pack_configure(before=row)
    def got_nudger(self, number, direction, full=0):
        subtk = self.slider_table[(self.current_row, number)]
        if direction == 'up':
            if full:
                subtk.scale.fade(1)
            else:
                subtk.scale.increase()
        else:
            if full:
                subtk.scale.fade(0)
            else:
                subtk.scale.decrease()
    def draw_sliders(self):
        self.tk_focusFollowsMouse()

        rowcount = -1
        col = 0
        for sub in self.submasters.get_all_subs():
            if col == 0: # make new row
                row = self.make_row()
                rowcount += 1
            current_level = self.current_sub_levels.get(sub.name, 0)
            subtk = self.draw_sub_slider(row, col, sub.name, current_level)
            self.slider_table[(rowcount, col)] = subtk
            self.name_to_subtk[sub.name] = subtk
            col += 1
            col %= 10

            def slider_changed(x, y, z, subtk=subtk):
                subtk.scale.draw_indicator_colors()
                self.send_levels()

            subtk.slider_var.trace('w', slider_changed)
    def make_row(self):
        row = Frame(self, bd=2, bg='black')
        row.pack(expand=1, fill=BOTH)
        self.setup_key_nudgers(row)
        self.rows.append(row)
        return row
    def draw_sub_slider(self, row, col, name, current_level):
        subtk = SubmasterTk(row, name, current_level, self)
        subtk.place(relx=col * 0.1, rely=0, relwidth=0.1, relheight=1)
        self.setup_key_nudgers(subtk.scale)

        self.slider_vars[name] = subtk.slider_var
        return subtk
    def highlight_row(self, row):
        row = self.rows[row]
        row['bg'] = 'red'
    def unhighlight_row(self, row):
        row = self.rows[row]
        row['bg'] = 'black'
    def get_levels(self):
        return dict([(name, slidervar.get()) 
            for name, slidervar in self.slider_vars.items()])
    def get_levels_as_sub(self):
        scaledsubs = [self.submasters.get_sub_by_name(sub) * level \
            for sub, level in self.get_levels().items()]

        maxes = sub_maxes(*scaledsubs)
        return maxes
    def save_current_stage(self, subname):
        print "saving current levels as", subname
        sub = self.get_levels_as_sub()
        sub.name = subname
        sub.save()

    def save(self):
        pickle.dump(self.get_levels(), 
                    file('.keyboardcomposer.savedlevels', 'w'))
    def send_frequent_updates(self):
        """called when we get a fade -- send events as quickly as possible"""
        if time.time() <= self.stop_frequent_update_time:
            self.send_levels()
            self.after(10, self.send_frequent_updates)

    def get_dmx_list(self):
        maxes = self.get_levels_as_sub()
        return maxes.get_dmx_list()
    def send_levels(self):
        if not self.dmxdummy:
            levels = self.get_dmx_list()
            dmxclient.outputlevels(levels)
        # print "sending levels", levels
    def send_levels_loop(self):
        self.send_levels()
        self.after(1000, self.send_levels_loop)
    def refresh(self):
        self.save()
        self.submasters = Submasters()
        self.current_sub_levels = \
            pickle.load(file('.keyboardcomposer.savedlevels'))
        for r in self.rows:
            r.destroy()
        self.keyhints.destroy()
        self.buttonframe.destroy()
        self.draw_ui()
    def toggle_sub_recording(self, subname):
        # xor the set with the subname
        self.subs_being_recorded = self.subs_being_recorded ^ Set([subname])
    def got_timestamp(self, timestamp):
        """Music player should ultimately call this (over XML-RPC).  
        
        For subs not being recorded, we bring up their values (unless
        they're independent maybe? -- independence not implemented yet).

        For subs being recorded, we record their values to disk.
        
        Each SubmasterTk talks to the SubLevelLogger to record and playback
        levels."""
        for sub in self.submasters.get_all_subs():
            name = sub.name
            subtk = self.name_to_subtk[name]
            if name in self.subs_being_recorded:
                subtk.record(timestamp)
            else:
                subtk.get_recorded_level(timestamp)

if __name__ == "__main__":
    s = Submasters()

    root = Tk()
    tl = toplevelat("Keyboard Recorder XP MX 2004 Gold", existingtoplevel=root)
    kc = KeyboardRecorder(tl, s, dmxdummy=0)
    kc.pack(fill=BOTH, expand=1)
    atexit.register(kc.save)
    try:
        mainloop()
    except KeyboardInterrupt:
        tl.destroy()
        sys.exit()
