from Patch import *
from time import time
from Tkinter import *
from types import TupleType

stdfont = ('Arial', 8)

class Param: # abstract
    def get_value(self):
        pass
    def set_value(self):
        pass
    def draw_tk(self, frame):
        pass

class CheckboxParam(Param):
    def __init__(self, initial=0):
        self.value = IntVar()
        self.value.set(initial)
    def get_value(self):
        return self.value.get()
    def draw_tk(self, frame):
        self.c = Checkbutton(frame, variable=self.value)
        self.c.pack()

class SliderParam(Param):
    def __init__(self, range=(0, 1), res=0.01, initial=0, orient='v', 
                 **options):
        self.value = DoubleVar()
        self.value.set(initial)
        self.options = {'res' : res, 'to' : range[0], 'from' : range[1],
                        'orient' : orient,
                        'font' : stdfont, 'length' : 50, 'sliderlength' : 10,
                        'width' : 10}
        self.options.update(options)
    def get_value(self):
        return self.value.get()
    def draw_tk(self, frame):
        s = Scale(frame, variable=self.value, **self.options)
        s.pack()

class TextParam(Param):
    def __init__(self, initial=''):
        self.value = StringVar()
        self.value.set(initial)
    def get_value(self):
        return self.value.get()
    def select_all(self, evt):
        self.e.select_range(0, END)
    def unfocus(self, evt):
        self.frame.focus()
    def draw_tk(self, frame):
        self.frame = frame
        self.e = Entry(frame, textvariable=self.value)
        self.e.bind("<Return>", self.unfocus)
        self.e.pack()

class ListParam(Param):
    def __init__(self, options=(), multiple=0, initial=''):
        self.value = StringVar()
        self.value.set(initial)
        self.options = options
        if multiple:
            self.selectmode = 'MULTIPLE'
        else:
            self.selectmode = 'SINGLE'
    def get_value(self):
        try:
            return self.l.get(self.l.curselection())
        except:
            return ''
    def draw_tk(self, frame):
        self.l = Listbox(frame, selectmode=self.selectmode, font=stdfont,
                         width=max([len(o) for o in self.options]),
                         height=len(self.options))
        for o in self.options:
            self.l.insert(END, o)
        self.l.pack()

class LabelParam(Param):
    def __init__(self, initial=''):
        self.value = StringVar()
        self.value.set(initial)
    def get_value(self):
        return self.value.get()
    def set_value(self, v):
        self.value.set(v)
    def draw_tk(self, frame):
        l = Label(frame, textvariable=self.value, font=stdfont)
        l.pack()

class ButtonParam(Param):
    def __init__(self, text, **options):
        self.options = {'text' : text}
        self.options.update(options)
        self.pressed = 0
        self.unread = 0 # unread button presses
    def draw_tk(self, frame):
        b = Button(frame, **self.options)
        b.pack()
        b.bind('<ButtonPress>', self.activate)
        b.bind('<ButtonRelease>', self.deactivate)
    def get_value(self):
        if self.unread:
            self.unread = 0
            return 1
        
        return self.pressed
    def activate(self, evt):
        self.pressed = 1
        self.unread = 1
    def deactivate(self, evt):
        self.pressed = 0

class Params:
    def __init__(self):
        self.params = {}
    def add_param(self, name, param):
        self.params[name] = param
    def get_param_value(self, name):
        return self.params[name].get_value()
    def __getitem__(self, name):
        return self.params[name].get_value()
    def __setitem__(self, name, value):
        self.params[name].set_value(value)
    def draw_tk(self, frame):
        for name,param in self.params.items():
            f = Frame(frame)
            l = Label(f, text=name, font=stdfont)
            l.pack(side='left')
            pframe = Frame(f)
            param.draw_tk(pframe)
            pframe.pack(side='right')
            f.pack()

class SliderAdjuster:
    def __init__(self):
        self.var = None
        self.atzero = 0
    def set(self, level):
        if self.var is not None:
            self.var.set(level)
    def get(self, level):
        if self.var is not None:
            return self.var.get()

        return None
    def justturnedon(self):
        return self.atzero

class Sub:
    def __init__(self, levels, dimmers=68, color=None):
        self.levels = levels
        self.dimmers = dimmers
        self.is_effect = callable(self.levels)
        self.slideradjuster = SliderAdjuster()
        if self.is_effect:
            self.params = Params()
            self.generator = self.levels(self.params, self.slideradjuster)
            self.generator.next()
        self.color = color
    def set_slider_var(self, slidervar):
        if self.is_effect:
            self.slideradjuster.var = slidervar
    def draw_tk(self, frame):
        if self.is_effect:
            self.params.draw_tk(frame)
    def get_state(self):
        pass
    def get_levels(self, level):
        d = {}
        if level == 0: 
            self.slideradjuster.atzero = 1
            return d
        if self.is_effect:
            d = self.generator.next()
            self.slideradjuster.atzero = 0
        else: # dictionary (standard)
            d = self.levels
        return dict([(get_dmx_channel(ch), float(lev) * float(level)) 
            for ch, lev in d.items()])

def reload_data(dummy):
    global subs
    if dummy:
        import ConfigDummy as Config
    else:
        import Config

    reload(Config)

    subs = {}
    for name, levels in Config.subs.items():
        if type(name) == TupleType:
            name, color = name
        else:
            color=None

        subs[name] = Sub(levels, color=color)

    # subs = dict([(name, Sub(levels)) for name, levels in Config.subs.items()])
