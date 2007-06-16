# taken from SnackMix -- now that's reusable code
from Tix import *
import time

class Fadable:
    """Fading mixin: must mix in with a Tk widget (or something that has
    'after' at least) This is currently used by VolumeBox and MixerTk.
    It's probably too specialized to be used elsewhere, but could possibly
    work with an Entry or a Meter, I guess.  (Actually, this is used by
    KeyboardComposer and KeyboardRecorder now too.)

    var is a Tk variable that should be used to set and get the levels.
    If use_fades is true, it will use fades to move between levels.
    If key_bindings is true, it will install these keybindings:

    Press a number to fade to that amount (e.g. '5' = 50%).  Also,
    '`' (grave) will fade to 0 and '0' will fade to 100%.

    If mouse_bindings is true, the following mouse bindings will be
    installed: Right clicking toggles muting.  The mouse wheel will
    raise or lower the volume.  Shift-mouse wheeling will cause a more
    precise volume adjustment.  Control-mouse wheeling will cause a
    longer fade."""
    def __init__(self, var, wheel_step=5, use_fades=1, key_bindings=1,
                 mouse_bindings=1):
        self.use_fades = use_fades # whether increase and decrease should fade
        self.wheel_step = wheel_step # amount that increase and descrease should
                                     # change volume (by default)
        
        self.fade_start_level = 0
        self.fade_end_level = 0
        self.fade_start_time = 0
        self.fade_length = 1
        self.fade_step_time = 10
        self.fade_var = var
        self.fading = 0 # whether a fade is in progress

        if key_bindings:
            for k in range(1, 10):
                self.bind("<Key-%d>" % k,
                    lambda evt, k=k: self.fade(k / 10.0))
            self.bind("<Key-0>", lambda evt: self.fade(1.0))
            self.bind("<grave>", lambda evt: self.fade(0))

            # up / down arrows
            self.bind("<Key-Up>", lambda evt: self.increase())
            self.bind("<Key-Down>", lambda evt: self.decrease())

        if mouse_bindings:
            # right mouse button toggles muting
            self.bind('<3>', lambda evt: self.toggle_mute())
            # not "NOT ANY MORE!" - homer (i.e. it works again)

            # mouse wheel
            self.bind('<4>', lambda evt: self.increase())
            self.bind('<5>', lambda evt: self.decrease())

            # modified mouse wheel
            self.bind('<Shift-4>', lambda evt: self.increase(multiplier=0.2))
            self.bind('<Shift-5>', lambda evt: self.decrease(multiplier=0.2))
            self.bind('<Control-4>', lambda evt: self.increase(length=1))
            self.bind('<Control-5>', lambda evt: self.decrease(length=1))

        self.last_level = None # used for muting
    def fade(self, value, length=0.5, step_time=10):
        """Fade to value in length seconds with steps every step_time
        milliseconds"""
        if length == 0: # 0 seconds fades happen right away and prevents
                        # and prevents us from entering the fade loop,
                        # which would cause a divide by zero
            self.fade_var.set(value)
            self.fading = 0 # we stop all fades
        else: # the general case
            self.fade_start_time = time.time()
            self.fade_length = length

            self.fade_start_level = self.fade_var.get()
            self.fade_end_level = value
            
            self.fade_step_time = step_time
            if not self.fading:
                self.fading = 1
                self.do_fade()
    def do_fade(self):
        """Actually performs the fade for Fadable.fade.  Shouldn't be called
        directly."""
        now = time.time()
        elapsed = now - self.fade_start_time
        complete = elapsed / self.fade_length
        complete = min(1.0, complete)
        diff = self.fade_end_level - self.fade_start_level
        newlevel = (complete * diff) + self.fade_start_level
        self.fade_var.set(newlevel)
        if complete < 1:
            self.after(self.fade_step_time, self.do_fade)
        else:
            self.fading = 0
    def increase(self, multiplier=1, length=0.3):
        """Increases the volume by multiplier * wheel_step.  If use_fades is
        true, it do this as a fade over length time."""
        amount = self.wheel_step * multiplier
        if self.fading:
            newlevel = self.fade_end_level + amount
        else:
            newlevel = self.fade_var.get() + amount
        newlevel = min(100, newlevel)
        self.set_volume(newlevel, length)
    def decrease(self, multiplier=1, length=0.3):
        """Descreases the volume by multiplier * wheel_step.  If use_fades
        is true, it do this as a fade over length time."""
        amount = self.wheel_step * multiplier
        if self.fading:
            newlevel = self.fade_end_level - amount
        else:
            newlevel = self.fade_var.get() - amount
        newlevel = max(0, newlevel)
        self.set_volume(newlevel, length)
    def set_volume(self, newlevel, length=0.3):
        """Sets the volume to newlevel, performing a fade of length if
        use_fades is true."""
        if self.use_fades:
            self.fade(newlevel, length=length)
        else:
            self.fade_var.set(newlevel)
    def toggle_mute(self):
        """Toggles whether the volume is being muted."""
        if self.last_level is None:
            self.last_level = self.fade_var.get()
            if self.last_level == 0: # we don't want last_level to be zero,
                                     # since it will make us toggle between 0
                                     # and 0
                newlevel = 1
            else:
                newlevel = 0
        else:
            newlevel = self.last_level
            self.last_level = None

        self.fade_var.set(newlevel)

if __name__ == "__main__":
    class SubScale(Scale, Fadable):
        def __init__(self, master, *args, **kw):
            self.scale_var = DoubleVar()
            kw['variable'] = self.scale_var
            Scale.__init__(self, master, *args, **kw)
            Fadable.__init__(self, var=self.scale_var)

    root = Tk()
    root.tk_focusFollowsMouse()
    ss = SubScale(root, from_=1, to_=0, res=0.01)
    ss.pack()
    mainloop()
