from __future__ import division, nested_scopes
import Tix as Tk
import time
from TreeDict import TreeDict, allow_class_to_be_pickled
from TLUtility import enumerate

cue_state_indicator_colors = {
             # bg       fg
    'prev' : ('blue',   'white'),
    'cur' :  ('yellow', 'black'),
    'next' : ('red',    'white'),
}

class LabelledScale(Tk.Frame):
    """Scale with two labels: a name and current value"""
    def __init__(self, master, label, **opts):
        Tk.Frame.__init__(self, master, bd=2, relief='raised')
        opts.setdefault('variable', Tk.DoubleVar())
        opts.setdefault('showvalue', 0)

        self.normaltrough = opts.get('troughcolor', 'black')
        self.flashtrough = opts.get('flashtroughcolor', 'red')
        del opts['flashtroughcolor']

        self.scale_var = opts['variable']
        self.scale = Tk.Scale(self, **opts)
        self.scale.pack(side='top', expand=1, fill='both')
        self.name = Tk.Label(self, text=label)
        self.name.pack(side='bottom')
        self.scale_value = Tk.Label(self, width=6)
        self.scale_value.pack(side='bottom')
        self.scale_var.trace('w', self.update_value_label)
        self.update_value_label()
        self.disabled = (self.scale['state'] == 'disabled')
    def set_label(self, label):
        self.name['text'] = label
    def update_value_label(self, *args):
        val = self.scale_var.get() * 100
        self.scale_value['text'] = "%0.2f" % val
        if val != 0:
            self.scale['troughcolor'] = self.flashtrough
        else:
            self.scale['troughcolor'] = self.normaltrough
    def disable(self):
        if not self.disabled:
            self.scale['state'] = 'disabled'
            self.scale_var.set(0)
            self.disabled = 1
    def enable(self):
        if self.disabled:
            self.scale['state'] = 'normal'
            self.disabled = 0

class TimedGoButton(Tk.Frame):
    """Go button, fade time entry, and time fader"""
    def __init__(self, master, name, scale_to_fade, **kw):
        Tk.Frame.__init__(self, master)
        self.name = name
        self.scale_to_fade = scale_to_fade
        self.button = Tk.Button(self, text=name, command=self.start_fade, **kw)
        self.button.pack(fill='both', expand=1, side='left')
        self.timer_var = Tk.StringVar()
        self.timer_entry = Tk.Entry(self, textvariable=self.timer_var, width=5)
        self.timer_entry.pack(fill='y', side='left')
        self.timer_var.set("2")
        self.disabled = (self.button['state'] == 'disabled')
    def start_fade(self, end_level=1):
        try:
            fade_time = float(self.timer_var.get())
        except ValueError:
            # TODO figure out how to handle this
            print "can't fade -- bad time"
            return

        self.start_time = time.time()
        self.start_level = self.scale_to_fade.scale_var.get()
        self.end_level = end_level
        self.fade_length = fade_time
        self.do_fade()
    def do_fade(self):
        diff = time.time() - self.start_time
        if diff < self.fade_length:
            percent = diff / self.fade_length
            newlevel = self.start_level + \
                (percent * (self.end_level - self.start_level))
            self.scale_to_fade.scale_var.set(newlevel)

            if newlevel != self.end_level:
                self.after(10, self.do_fade)
        else:
            self.scale_to_fade.scale_var.set(self.end_level)
    def disable(self):
        if not self.disabled:
            self.button['state'] = 'disabled'
            self.disabled = 1
    def enable(self):
        if self.disabled:
            self.button['state'] = 'normal'
            self.disabled = 0

class CueFader(Tk.Frame):
    def __init__(self, master, cuelist):
        Tk.Frame.__init__(self, master)
        self.cuelist = cuelist
        self.auto_shift = Tk.IntVar()
        self.auto_shift.set(1)

        # this is a mechanism to stop Tk from autoshifting too much.
        # if this variable is true, the mouse button is down.  we don't want
        # to shift until they release it.  when it is released, we will
        # set it to false and then call autoshift.
        self.no_shifts_until_release = 0

        self.scales = {}
        self.shift_buttons = {}
        self.go_buttons = {}
        
        topframe = Tk.Frame(self)

        self.set_prev_button = Tk.Button(topframe, text='Set Prev',
            command=lambda: cuelist.set_selection_as_prev(),
            fg='white', bg='blue')
        self.set_prev_button.pack(side='left')

        self.auto_shift_checkbutton = Tk.Checkbutton(topframe, 
            variable=self.auto_shift, text='Autoshift', 
            command=self.toggle_autoshift)
        self.auto_shift_checkbutton.pack(side='left')

        self.set_next_button = Tk.Button(topframe, text='Set Next',
            command=lambda: cuelist.set_selection_as_next(),
            fg='white', bg='red')
        self.set_next_button.pack(side='left')

        topframe.pack(side='top')

        faderframe = Tk.Frame(self)
        self.direction_info = (('Prev', 1, 0, 'left', 'blue'),
                               ('Next', 0, 1, 'right', 'red'))
        for name, start, end, side, color in self.direction_info:
            frame = Tk.Frame(self)
            scale = LabelledScale(frame, name, from_=start, to_=end, 
                res=0.0001, orient='horiz', flashtroughcolor=color)
            scale.pack(fill='x', expand=0)
            go = TimedGoButton(frame, 'Go %s' % name, scale, bg=color, 
                fg='white')
            go.pack(fill='both', expand=1)
            frame.pack(side=side, fill='both', expand=1)
        
            shift = Tk.Button(frame, text="Shift %s" % name, state='disabled',
                command=lambda name=name: self.shift(name), fg=color, 
                bg='black')

            self.scales[name] = scale
            self.shift_buttons[name] = shift
            self.go_buttons[name] = go

            scale.scale_var.trace('w', \
                lambda x, y, z, name=name, scale=scale: self.xfade(name, scale))

            def button_press(event, name=name, scale=scale):
                self.no_shifts_until_release = 1 # prevent shifts until release
            def button_release(event, name=name, scale=scale):
                self.no_shifts_until_release = 0
                self.autoshift(name, scale)

            scale.scale.bind("<ButtonPress>", button_press)
            scale.scale.bind("<ButtonRelease>", button_release)
        faderframe.pack(side='bottom', fill='both', expand=1)
    def toggle_autoshift(self):
        for name, button in self.shift_buttons.items():
            if not self.auto_shift.get():
                button.pack(side='bottom', fill='both', expand=1)
            else:
                button.pack_forget()
    def shift(self, name):
        # to prevent overshifting
        if self.no_shifts_until_release:
            return

        for scale_name, scale in self.scales.items():
            scale.scale.set(0)
        self.cuelist.shift((-1, 1)[name == 'Next'])
    def autoshift(self, name, scale):
        scale_val = scale.scale_var.get() 

        if scale_val == 1:
            if self.auto_shift.get():
                self.shift(name)
    def xfade(self, name, scale):
        if self.auto_shift.get():
            self.autoshift(name, scale)
            scale_val = scale.scale_var.get() 
        else:
            scale_val = scale.scale_var.get() 
            if scale_val == 1:
                self.shift_buttons[name]['state'] = 'normal'
            else:
                # disable any dangerous shifting
                self.shift_buttons[name]['state'] = 'disabled'

        d = self.opposite_direction(name)
        if scale_val != 0:
            # disable illegal three part crossfades
            self.scales[d].disable()
            self.go_buttons[d].disable()
        else:
            # undo above work
            self.scales[d].enable()
            self.go_buttons[d].enable()
    def opposite_direction(self, d):
        if d == 'Next':
            return 'Prev'
        else:
            return 'Next'

class Cue:
    """A Cue has a name, a time, and any number of other attributes."""
    def __init__(self, name, time=3, **attrs):
        self.name = name
        self.time = time
        self.__dict__.update(attrs)
    def __repr__(self):
        return "<Cue %s, length %s>" % (self.name, self.time)

empty_cue = Cue('empty')

allow_class_to_be_pickled(Cue)

class CueList:
    """Persistent list of Cues"""
    def __init__(self, filename):
        self.filename = filename
        self.treedict = TreeDict()
        try:
            self.treedict.load(filename)
        except IOError:
            self.treedict.cues = []
        self.cues = self.treedict.cues
        self.current_cue_index = 0
        self.next_pointer = None
        self.prev_pointer = None

        import atexit
        atexit.register(self.save)
    def add_cue(self, cue, index=None):
        """Adds a Cue object to the list.  If no index is specified,
        the cue will be added to the end."""
        index = index or len(self.cues)
        self.cues.insert(index, cue)
    def shift(self, diff):
        """Shift through cue history"""
        old_index = self.current_cue_index
        self.current_cue_index = None
        if diff < 0: # if going backwards
            if self.prev_pointer: # use a prev pointer if we have one
                self.current_cue_index = self.prev_pointer
            self.next_pointer = old_index
            self.prev_pointer = None
        else:
            if self.next_pointer: # use a next pointer if we have one
                self.current_cue_index = self.next_pointer
            self.next_pointer = None
            self.prev_pointer = old_index
        if not self.current_cue_index:
            self.current_cue_index = old_index + diff
    def set_next(self, index):
        self.next_pointer = index
    def set_prev(self, index):
        self.prev_pointer = index
    def bound_index(self, index):
        if not self.cues:
            return None
        else:
            return max(0, min(index, len(self.cues) - 1))
    def get_current_cue_indices(self):
        cur = self.current_cue_index
        return [self.bound_index(index) for index in
                    (self.prev_pointer or cur - 1, 
                     cur, 
                     self.next_pointer or cur + 1)]
    def get_current_cues(self):
        return [self.get_cue_by_index(index) 
            for index in self.get_current_cue_indices()]
    def get_cue_by_index(self, index):
        if index:
            return self.cues[self.bound_index(index)]
        else:
            return empty_cue
    def __del__(self):
        self.save()
    def save(self):
        self.treedict.save(self.filename)
    def reload(self):
        # TODO: we probably will need to make sure that indices still make
        # sense, etc.
        self.treedict.load(self.filename)

class TkCueList(CueList, Tk.Frame):
    def __init__(self, master, filename):
        CueList.__init__(self, filename)
        Tk.Frame.__init__(self, master)
        
        self.columns = ('name', 'time', 'page', 'desc')
            
        self.scrolled_hlist = Tk.ScrolledHList(self,
            options='hlist.columns %d hlist.header 1' % len(self.columns))
        self.hlist = self.scrolled_hlist.hlist
        self.hlist.configure(fg='white', bg='black', 
            command=self.select_callback)
        self.scrolled_hlist.pack(fill='both', expand=1)

        boldfont = self.tk.call('tix', 'option', 'get', 
            'bold_font')
        header_style = Tk.DisplayStyle('text', refwindow=self,
            anchor='center', padx=8, pady=2, font=boldfont)

        for count, header in enumerate(self.columns):
            self.hlist.header_create(count, itemtype='text',
                text=header, style=header_style)

        self.cue_label_windows = {}
        for count, cue in enumerate(self.cues):
            self.display_cue(count, cue)
        self.update_cue_indicators()
    def display_cue(self, cue_count, cue):
        # cue_count is the path in the hlist -- this probably isn't ideal
        for col, header in enumerate(self.columns):
            try:
                text = getattr(cue, header)
            except AttributeError:
                text = ''

            if col == 0:
                lab = Tk.Label(self.hlist, text=text, fg='white', bg='black')
                def select_and_highlight(event):
                    self.select_callback(cue_count)
                    self.hlist.selection_clear()
                    self.hlist.selection_set(cue_count)

                lab.bind("<Double-1>", select_and_highlight)
                self.hlist.add(cue_count, itemtype='window', window=lab)
                self.cue_label_windows[cue_count] = lab
            else:
                self.hlist.item_create(cue_count, col, text=text)
    def reset_cue_indicators(self, cue_indices=None):
        """If cue_indices is None, we'll reset all of them."""
        cue_indices = cue_indices or self.cue_label_windows.keys()
        for key in cue_indices:
            window = self.cue_label_windows[key]
            window.configure(fg='white', bg='black')
    def update_cue_indicators(self):
        states = dict(zip(self.get_current_cue_indices(), 
                     ('prev', 'cur', 'next')))

        for count, state in states.items():
            window = self.cue_label_windows[count]
            bg, fg = cue_state_indicator_colors[state]
            window.configure(bg=bg, fg=fg)
    def shift(self, diff):
        self.reset_cue_indicators(self.get_current_cue_indices())
        CueList.shift(self, diff)
        self.update_cue_indicators()
        # try to see all indices, but next takes priority over all, and cur
        # over prev
        for index in self.get_current_cue_indices():
            self.hlist.see(index)
    def select_callback(self, index):
        new_next = int(index)
        self.set_next(new_next)
    def set_next(self, index):
        prev, cur, next = self.get_current_cue_indices()
        self.reset_cue_indicators((next,))
        CueList.set_next(self, index)
        self.update_cue_indicators()
    def set_prev(self, index):
        prev, cur, next = self.get_current_cue_indices()
        self.reset_cue_indicators((prev,))
        CueList.set_prev(self, index)
        self.update_cue_indicators()
    def set_selection_as_prev(self):
        sel = self.hlist.info_selection()
        if sel:
            self.set_prev(int(sel[0]))
    def set_selection_as_next(self):
        sel = self.hlist.info_selection()
        if sel:
            self.set_next(int(sel[0]))

if __name__ == "__main__":
    root = Tk.Tk()
    cl = TkCueList(root, 'cues/cuelist1')
    cl.pack(fill='both', expand=1)

    # to populate cue list
    if 0:
        for x in range(20):
            cl.add_cue(Cue('cue %d' % x, time=x, some_attribute=3))

    fader = CueFader(root, cl)
    fader.pack(fill='both', expand=1)
    Tk.mainloop()
