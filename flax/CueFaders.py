from __future__ import division, nested_scopes
import Tix as Tk
import time
from TreeDict import TreeDict, allow_class_to_be_pickled

class LabelledScale(Tk.Frame):
    """Scale with two labels: a name and current value"""
    def __init__(self, master, label, **opts):
        Tk.Frame.__init__(self, master, bd=2, relief='raised')
        opts.setdefault('variable', Tk.DoubleVar())
        opts.setdefault('showvalue', 0)
        self.scale_var = opts['variable']
        self.scale = Tk.Scale(self, **opts)
        self.scale.pack(side='top', expand=1, fill='both')
        self.name = Tk.Label(self, text=label)
        self.name.pack(side='bottom')
        self.scale_value = Tk.Label(self, width=6)
        self.scale_value.pack(side='bottom')
        self.scale_var.trace('w', self.update_value_label)
        self.update_value_label()
    def set_label(self, label):
        self.name['text'] = label
    def update_value_label(self, *args):
        val = self.scale_var.get() * 100
        self.scale_value['text'] = "%0.2f" % val

class TimedGoButton(Tk.Frame):
    """Go button, fade time entry, and time fader"""
    def __init__(self, master, name, scale_to_fade):
        Tk.Frame.__init__(self, master)
        self.name = name
        self.scale_to_fade = scale_to_fade
        self.button = Tk.Button(self, text=name, command=self.start_fade)
        self.button.pack(fill='both', expand=1, side='left')
        self.timer_var = Tk.StringVar()
        self.timer_entry = Tk.Entry(self, textvariable=self.timer_var, width=5)
        self.timer_entry.pack(fill='y', side='left')
        self.timer_var.set("2")
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

class CueFader(Tk.Frame):
    def __init__(self, master, cuelist):
        Tk.Frame.__init__(self, master)
        self.cuelist = cuelist
        self.auto_shift = Tk.IntVar()
        self.auto_shift.set(1)

        self.scales = {}
        self.shift_buttons = {}

        topframe = Tk.Frame(self)
        self.current_cues = Tk.Label(topframe)
        self.current_cues.pack()
        self.update_cue_display()
        topframe.pack()
        
        bottomframe = Tk.Frame(self)
        self.auto_shift_checkbutton = Tk.Checkbutton(self, 
            variable=self.auto_shift, text='Autoshift', 
            command=self.toggle_autoshift)
        self.auto_shift_checkbutton.pack()
        bottomframe.pack(side='bottom')

        middleframe = Tk.Frame(self)
        for name, start, end, side in (('Prev', 1, 0, 'left'),
                                       ('Next', 0, 1, 'right')):
            frame = Tk.Frame(self)
            scale = LabelledScale(frame, name, from_=start, to_=end, 
                res=0.01, orient='horiz')
            scale.pack(fill='both', expand=1)
            go = TimedGoButton(frame, 'Go %s' % name, scale)
            go.pack(fill='both', expand=1)
            frame.pack(side=side, fill='both', expand=1)
        
            shift = Tk.Button(frame, text="Shift %s" % name, state='disabled',
                command=lambda name=name: self.shift(name))

            self.scales[name] = scale
            self.shift_buttons[name] = shift

            scale.scale_var.trace('w', \
                lambda x, y, z, name=name, scale=scale: self.xfade(name, scale))
        middleframe.pack(side='bottom', fill='both', expand=1)
    def toggle_autoshift(self):
        for name, button in self.shift_buttons.items():
            if not self.auto_shift.get():
                button.pack(side='bottom', fill='both', expand=1)
            else:
                button.pack_forget()

    def shift(self, name):
        for scale in self.scales.values():
            scale.scale_var.set(0)
            scale.scale.update()
        print "shift", name
        self.cuelist.shift((-1, 1)[name == 'Next'])
        self.update_cue_display()
    def update_cue_display(self):
        current_cues = [cue.name for cue in self.cuelist.get_current_cues()]
        self.current_cues['text'] = ', '.join(current_cues)
    def xfade(self, name, scale):
        scale_val = scale.scale_var.get() 

        if scale_val == 1:
            if self.auto_shift.get():
                self.shift(name)
            else:
                self.shift_buttons[name]['state'] = 'normal'
        else:
            # disable any dangerous shifting
            self.shift_buttons[name]['state'] = 'disabled'

        if scale_val != 0:
            # disable illegal three part crossfades
            # TODO:
            # if name == 'Next':
            #   disable go_prev button and slider, lock slider at 0
            pass
        else:
            # undo above changes

            # Actually, TimedGoButton and LabelledScale can have enable/disable
            # methods which will only do the Tk calls if necessary
            pass

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
            return max(0, min(index, len(self.cues)))
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

if __name__ == "__main__":
    cl = CueList('cues/cuelist1')

    # to populate cue list
    if 0:
        for x in range(20):
            cl.add_cue(Cue('cue %d' % x, time=x, some_attribute=3))

    root = Tk.Tk()
    fader = CueFader(root, cl)
    fader.pack(fill='both', expand=1)
    Tk.mainloop()
