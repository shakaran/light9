from __future__ import division, nested_scopes
import Tix as Tk
import time
from TreeDict import TreeDict, allow_class_to_be_pickled
from TLUtility import enumerate
import Submaster, dmxclient

cue_state_indicator_colors = {
             # bg       fg
    'prev' : ('blue',   'white'),
    'cur' :  ('yellow', 'black'),
    'next' : ('red',    'white'),
}

class LabelledScale(Tk.Frame):
    """Scale with two labels: a name and current value"""
    def __init__(self, master, label, **opts):
        Tk.Frame.__init__(self, master, bd=2, relief='raised', bg='black')
        self.labelformatter = opts.get('labelformatter')
        try:
            del opts['labelformatter']
        except KeyError:
            pass

        opts.setdefault('variable', Tk.DoubleVar())
        opts.setdefault('showvalue', 0)

        self.normaltrough = opts.get('troughcolor', 'black')
        self.flashtrough = opts.get('flashtroughcolor', 'red')
        try:
            del opts['flashtroughcolor']
        except KeyError:
            pass

        self.scale_var = opts['variable']
        self.scale = Tk.Scale(self, **opts)
        self.scale.pack(side='top', expand=1, fill='both')
        self.name = Tk.Label(self, text=label, bg='black', fg='white')
        self.name.pack(side='bottom')
        self.scale_value = Tk.Label(self, bg='black', fg='white')
        self.scale_value.pack(side='bottom')
        self.scale_var.trace('w', self.update_value_label)
        self.update_value_label()
        self.disabled = (self.scale['state'] == 'disabled')
    def set_label(self, label):
        self.name['text'] = label
    def update_value_label(self, *args):
        val = self.scale_var.get() * 100
        if self.labelformatter:
            format = self.labelformatter(val)
        else:
            format = "%0.2f" % val
        self.scale_value['text'] = format
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
        Tk.Frame.__init__(self, master, bg='black')
        self.name = name
        self.scale_to_fade = scale_to_fade
        self.button = Tk.Button(self, text=name, command=self.start_fade, **kw)
        self.button.pack(fill='both', expand=1, side='left')

        self.timer_var = Tk.DoubleVar()
        self.timer_entry = Tk.Control(self, step=0.5, min=0, integer=0, 
            variable=self.timer_var, selectmode='immediate')
        for widget in (self.timer_entry, self.timer_entry.entry, 
            self.timer_entry.incr, self.timer_entry.decr, self.button, self):
            widget.bind("<4>", self.wheelscroll)
            widget.bind("<5>", self.wheelscroll)
        self.timer_entry.entry.configure(width=5, bg='black', fg='white')
        self.timer_entry.pack(fill='y', side='left')
        self.timer_var.set(2)
        self.disabled = (self.button['state'] == 'disabled')
        self.fading = 0
    def wheelscroll(self, event):
        """Mouse wheel increments or decrements timer."""
        if event.num == 4: # scroll up
            self.timer_entry.increment()
        else:            # scroll down
            self.timer_entry.decrement()
    def start_fade(self, end_level=1):
        try:
            fade_time = float(self.timer_var.get())
        except ValueError:
            # since we use a control now, i don't think we need to worry about
            # validation any more.
            print ">>> Can't fade -- bad time", self.timer_var.get()
            return

        self.start_time = time.time()
        self.start_level = self.scale_to_fade.scale_var.get()
        self.end_level = end_level
        self.fade_length = fade_time
        self.fading = 1
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
                self.fading = 0
        else:
            self.scale_to_fade.scale_var.set(self.end_level)
            self.fading = 0
    def disable(self):
        if not self.disabled:
            self.button['state'] = 'disabled'
            self.disabled = 1
    def enable(self):
        if self.disabled:
            self.button['state'] = 'normal'
            self.disabled = 0
    def set_time(self, time):
        self.timer_var.set(time)
    def get_time(self):
        return self.timer_var.get()
    def is_fading(self):
        return self.fading

class CueFader(Tk.Frame):
    def __init__(self, master, cuelist):
        Tk.Frame.__init__(self, master, bg='black')
        self.cuelist = cuelist
        self.cuelist.set_fader(self)

        self.last_levels_sent = 0
        self.current_dmx_levels = [0] * 68
        self.after(0, self.send_dmx_levels_loop) # start DMX sending loop

        # this is a mechanism to stop Tk from autoshifting too much.
        # if this variable is true, the mouse button is down.  we don't want
        # to shift until they release it.  when it is released, we will
        # set it to false and then call autoshift.
        self.no_shifts_until_release = 0

        self.scales = {}
        self.shift_buttons = {}
        self.go_buttons = {}
        
        topframe = Tk.Frame(self, bg='black')

        self.set_prev_button = Tk.Button(topframe, text='Set Prev',
            command=lambda: cuelist.set_selection_as_prev(),
            fg='white', bg='blue')
        self.set_prev_button.pack(side='left')

        self.auto_shift = Tk.IntVar()
        self.auto_shift.set(1)

        self.auto_shift_checkbutton = Tk.Checkbutton(topframe, 
            variable=self.auto_shift, text='Autoshift', 
            command=self.toggle_autoshift, bg='black', fg='white',
            highlightbackground='black')
        self.auto_shift_checkbutton.pack(fill='both', side='left')

        self.auto_load_times = Tk.IntVar()
        self.auto_load_times.set(1)

        self.auto_load_times_checkbutton = Tk.Checkbutton(topframe, 
            variable=self.auto_load_times, text='Autoload Times', 
            command=self.toggle_autoshift, bg='black', fg='white', 
            highlightbackground='black')
        self.auto_load_times_checkbutton.pack(fill='both', side='left')

        self.set_next_button = Tk.Button(topframe, text='Set Next',
            command=lambda: cuelist.set_selection_as_next(),
            fg='white', bg='red')
        self.set_next_button.pack(side='left')

        topframe.pack(side='top')

        faderframe = Tk.Frame(self, bg='black')
        self.direction_info = (('Prev', 1, 0, 'left', 'blue'),
                               ('Next', 0, 1, 'right', 'red'))
        for name, start, end, side, color in self.direction_info:
            frame = Tk.Frame(self, bg='black')
            scale = LabelledScale(frame, name, from_=start, to_=end, 
                res=0.0001, orient='horiz', flashtroughcolor=color,
                labelformatter=lambda val, name=name: self.get_scale_desc(val, 
                                                                          name))
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
            go.timer_var.trace('w',
                lambda x, y, z, scale=scale: scale.update_value_label())

            def button_press(event, name=name, scale=scale):
                self.no_shifts_until_release = 1 # prevent shifts until release
            def button_release(event, name=name, scale=scale):
                self.no_shifts_until_release = 0
                self.autoshift(name, scale)

            scale.scale.bind("<ButtonPress>", button_press)
            scale.scale.bind("<ButtonRelease>", button_release)
        faderframe.pack(side='bottom', fill='both', expand=1)

        self.current_dir = 'Next'
        self.cues_as_subs = {}
        self.update_cue_cache()
    def reload_cue_times(self):
        prev, cur, next = self.cuelist.get_current_cues()
        self.go_buttons['Next'].set_time(next.time)
    def update_cue_cache(self):
        """Rebuilds subs from the current cues.  As this is expensive, we don't
        do it unless necessary (i.e. whenever we shift or a cue is edited)"""
        # load the subs to fade between
        for cue, name in zip(self.cuelist.get_current_cues(), 
                             ('Prev', 'Cur', 'Next')):
            self.cues_as_subs[name] = cue.get_levels_as_sub()
        self.compute_dmx_levels()
    def compute_dmx_levels(self):
        """Compute the DMX levels to send.  This should get called whenever the
        DMX levels could change: either during a crossfade or when a cue is
        edited.  Since this is called when we know that a change might occur,
        we will send the new levels too."""
        cur_sub = self.cues_as_subs.get('Cur')
        if cur_sub:
            scale = self.scales[self.current_dir]
            scale_val = scale.scale_var.get() 

            other_sub = self.cues_as_subs[self.current_dir]
            current_levels_as_sub = cur_sub.crossfade(other_sub, scale_val)
            self.current_dmx_levels = current_levels_as_sub.get_dmx_list()
            self.send_dmx_levels()
    def send_dmx_levels(self):
        # print "send_dmx_levels", self.current_dmx_levels
        dmxclient.outputlevels(self.current_dmx_levels)
        self.last_levels_sent = time.time()
    def send_dmx_levels_loop(self):
        diff = time.time() - self.last_levels_sent
        if diff >= 2: # too long since last send
            self.send_dmx_levels()
            self.after(200, self.send_dmx_levels_loop)
        else:
            self.after(int((2 - diff) * 100), self.send_dmx_levels_loop)
    def get_scale_desc(self, val, name):
        """Returns a description to the TimedGoButton"""
        go_button = self.go_buttons.get(name)
        if go_button:
            time = go_button.get_time()
            return "%0.2f%%, %0.1fs left" % (val, time - ((val / 100.0) * time))
        else:
            return "%0.2f%%" % val
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

        self.update_cue_cache()
        if self.auto_load_times.get():
            self.reload_cue_times()
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

        self.current_dir = name
        self.compute_dmx_levels()
    def opposite_direction(self, d):
        if d == 'Next':
            return 'Prev'
        else:
            return 'Next'

class Cue:
    """A Cue has a name, a time, and any number of other attributes."""
    def __init__(self, name, time=3, sub_levels='', **attrs):
        self.name = name
        self.time = time
        self.sub_levels = sub_levels
        self.__dict__.update(attrs)
    def __repr__(self):
        return "<Cue %s, length %s>" % (self.name, self.time)
    def get_levels_as_sub(self):
        """Get this Cue as a combined Submaster, normalized.  This method
        should not be called constantly, since it is somewhat expensive.  It
        will reload the submasters from disk, combine all subs together, and
        then compute the normalized form."""
        subdict = {}
        for line in self.sub_levels.split(','):
            try:
                line = line.strip()
                if not line: 
                    continue
                sub, scale = line.split(':')
                sub = sub.strip()
                scale = float(scale)
                subdict[sub] = scale
            except ValueError:
                print "Parsing error for '%s' in %s" % (self.sub_levels, self)

        s = Submaster.Submasters()
        newsub = Submaster.sub_maxes(*[s[sub] * scale 
            for sub, scale in subdict.items()])
        return newsub.get_normalized_copy()

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
        self.current_cue_index = -1
        self.next_pointer = 0
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
        if not self.cues or index < 0:
            return None
        else:
            return min(index, len(self.cues) - 1)
    def get_current_cue_indices(self):
        """Returns a list of the indices of three cues: the previous cue,
        the current cue, and the next cue."""
        cur = self.current_cue_index
        return [self.bound_index(index) for index in
                    (self.prev_pointer or cur - 1, 
                     cur, 
                     self.next_pointer or cur + 1)]
    def get_current_cues(self):
        """Returns a list of three cues: the previous cue, the current cue,
        and the next cue."""
        return [self.get_cue_by_index(index) 
            for index in self.get_current_cue_indices()]
    def get_cue_by_index(self, index):
        try:
            return self.cues[self.bound_index(index)]
        except TypeError:
            return empty_cue
    def __del__(self):
        self.save()
    def save(self):
        print "Saving cues to", self.filename
        self.treedict.save(self.filename)
    def reload(self):
        # TODO: we probably will need to make sure that indices still make
        # sense, etc.
        self.treedict.load(self.filename)

class TkCueList(CueList, Tk.Frame):
    def __init__(self, master, filename):
        CueList.__init__(self, filename)
        Tk.Frame.__init__(self, master, bg='black')
        self.fader = None
        
        self.edit_tl = Tk.Toplevel()
        self.editor = CueEditron(self.edit_tl, 
            changed_callback=self.cue_changed)
        self.editor.pack(fill='both', expand=1)

        def edit_cue(index):
            index = int(index)
            self.editor.set_cue_to_edit(self.cues[index])
            
        self.columns = ('name', 'time', 'page', 'desc')
        self.scrolled_hlist = Tk.ScrolledHList(self,
            options='hlist.columns %d hlist.header 1' % len(self.columns))
        self.hlist = self.scrolled_hlist.hlist
        self.hlist.configure(fg='white', bg='black', 
            command=self.select_callback, browsecmd=edit_cue)
        self.hlist.bind("<4>", self.wheelscroll)
        self.hlist.bind("<5>", self.wheelscroll)
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
    def set_fader(self, fader):
        self.fader = fader
    def wheelscroll(self, evt):
        """Perform mouse wheel scrolling"""
        if evt.num == 4: # scroll down
            amount = -2
        else:            # scroll up
            amount = 2
        self.hlist.yview('scroll', amount, 'units')
    def cue_changed(self, cue):
        path = self.cues.index(cue)
        for col, header in enumerate(self.columns):
            try:
                text = getattr(cue, header)
            except AttributeError:
                text = ''

            if col == 0:
                self.cue_label_windows[path]['text'] = text
            else:
                self.hlist.item_configure(path, col, text=text)

        if cue in self.get_current_cues() and self.fader:
            self.fader.update_cue_cache()
            self.fader.reload_cue_times()
    def display_cue(self, path, cue):
        for col, header in enumerate(self.columns):
            try:
                text = getattr(cue, header)
            except AttributeError:
                text = ''

            if col == 0:
                lab = Tk.Label(self.hlist, text=text, fg='white', bg='black')
                def select_and_highlight(event):
                    self.select_callback(path)
                    self.hlist.selection_clear()
                    self.hlist.selection_set(path)

                lab.bind("<Double-1>", select_and_highlight)
                self.hlist.add(path, itemtype='window', window=lab)
                self.cue_label_windows[path] = lab
            else:
                self.hlist.item_create(path, col, text=text)
    def reset_cue_indicators(self, cue_indices=None):
        """If cue_indices is None, we'll reset all of them."""
        cue_indices = cue_indices or self.cue_label_windows.keys()
        for key in cue_indices:
            if key is None:
                continue
            window = self.cue_label_windows[key]
            window.configure(fg='white', bg='black')
    def update_cue_indicators(self):
        states = dict(zip(self.get_current_cue_indices(), 
                     ('prev', 'cur', 'next')))

        for count, state in states.items():
            if count is None:
                continue
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
            if index is not None:
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

class CueEditron(Tk.Frame):
    def __init__(self, master, changed_callback=None, cue=None):
        Tk.Frame.__init__(self, master, bg='black')
        self.master = master
        self.cue = cue
        self.changed_callback = changed_callback
        self.enable_callbacks = 1

        self.setup_editing_forms()
        self.set_cue_to_edit(cue)
    def set_cue_to_edit(self, cue):
        if cue != self.cue:
            self.cue = cue
            self.fill_in_cue_info()
            self.set_title()
    def set_title(self):
            try:
                self.master.title("Editing '%s'" % self.cue.name)
            except AttributeError:
                pass
    def setup_editing_forms(self):
        self.variables = {}
        for row, field in enumerate(('name', 'time', 'page', 'desc', 
            'sub_levels')):
            lab = Tk.Label(self, text=field, fg='white', bg='black')
            lab.grid(row=row, column=0, sticky='nsew')

            entryvar = Tk.StringVar()
            entry = Tk.Entry(self, fg='white', bg='black', 
                textvariable=entryvar)
            entry.grid(row=row, column=1, sticky='nsew')

            self.variables[field] = entryvar

            def field_changed(x, y, z, field=field, entryvar=entryvar):
                if self.cue:
                    setattr(self.cue, field, entryvar.get())
                    if self.enable_callbacks and self.changed_callback:
                        self.changed_callback(self.cue)
                if field == 'name':
                    self.set_title()

            entryvar.trace('w', field_changed)
        self.columnconfigure(1, weight=1)
    def fill_in_cue_info(self):
        self.enable_callbacks = 0
        for row, field in enumerate(('name', 'time', 'page', 'desc', 
            'sub_levels')):
            text = ''
            if self.cue:
                try:
                    text = getattr(self.cue, field)
                except AttributeError:
                    pass
            self.variables[field].set(text)
        self.enable_callbacks = 1

if __name__ == "__main__":
    root = Tk.Tk()
    root.title("ShowMaster 9000")
    root.geometry("500x555")
    cl = TkCueList(root, 'cues/cuelist1')
    cl.pack(fill='both', expand=1)

    fader = CueFader(root, cl)
    fader.pack(fill='both', expand=1)
    try:
        Tk.mainloop()
    except KeyboardInterrupt:
        root.destroy()
