from __future__ import nested_scopes
import sys
sys.path.append('..')
from Widgets.Fadable import Fadable

from Tix import *
import math
from Timeline import LevelFrame

Submaster = LevelFrame

nudge_keys = {
    'up' : list('qwertyuiop'),
    'down' : list('asdfghjkl')
}
nudge_keys['down'].append('semicolon')

class SubScale(Scale, Fadable):
    def __init__(self, master, *args, **kw):
        self.scale_var = kw.get('variable') or DoubleVar()
        kw.update({'variable' : self.scale_var,
                   'from' : 100, 'to' : 0, 'showvalue' : 0,
                   'sliderlength' : 10})
        Scale.__init__(self, master, *args, **kw)
        Fadable.__init__(self, var=self.scale_var)

class SubmasterTk(Frame):
    def __init__(self, master, name, current_level):
        Frame.__init__(self, master)
        self.slider_var = DoubleVar()
        self.slider_var.set(current_level)
        self.scale = SubScale(self, variable=self.slider_var, width=20)
        textlabel = Label(self, text=name)
        textlabel.pack(side=TOP)
        self.scale.pack(side=BOTTOM, expand=1, fill=BOTH)

class KeyboardComposer(Frame):
    def __init__(self, root, submasters, current_sub_levels=None):
        Frame.__init__(self, root)
        self.submasters = submasters
        self.current_sub_levels = current_sub_levels or {}

        self.rows = [] # this holds Tk Frames for each row
        self.slider_vars = {} # this holds subname:sub Tk vars
        self.slider_table = {} # this holds coords:sub Tk vars
        self.current_row = 0
        
        self.make_key_hints()
        self.draw_sliders()
        self.highlight_row(self.current_row)
        self.rows[self.current_row].focus()
    def make_key_hints(self):
        keyhintrow = Frame(self)

        col = 0
        for upkey, downkey in zip(nudge_keys['up'],
                                  nudge_keys['down']):
            # what a hack!
            downkey = downkey.replace('semicolon', ';')

            # another what a hack!
            keylabel = Label(keyhintrow, text='%s\n%s' % (upkey, downkey), 
                width=3, font=('Arial Bold', 12), bg='red', fg='white')
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

        # page up and page down change the row
        for key in '<Prior> <Next> <Control-n> <Control-p>'.split():
            tkobject.bind(key, self.change_row)

    def change_row(self, event):
        diff = 1
        if event.keysym in ('Prior', '<Control-p>'):
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
        print "got_nudger", number, direction, full
        subtk = self.slider_table[(self.current_row, number)]
        if direction == 'up':
            if full:
                subtk.scale.fade(100)
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
        for sub in self.submasters:
            if col == 0: # make new row
                row = self.make_row()
                rowcount += 1
            current_level = self.current_sub_levels.get(sub.name, 0)
            subtk = self.draw_sub_slider(row, col, sub.name, current_level)
            self.slider_table[(rowcount, col)] = subtk
            col += 1
            col %= 10
    def make_row(self):
        row = Frame(self, bd=2)
        row.pack(expand=1, fill=BOTH)
        self.setup_key_nudgers(row)
        self.rows.append(row)
        return row
    def draw_sub_slider(self, row, col, name, current_level):
        subtk = SubmasterTk(row, name, current_level)
        subtk.place(relx=col * 0.1, rely=0, relwidth=0.1, relheight=1)
        self.setup_key_nudgers(subtk.scale)

        self.slider_vars[name] = subtk.slider_var
        return subtk
    def highlight_row(self, row):
        row = self.rows[row]
        row['bg'] = 'red'
    def unhighlight_row(self, row):
        row = self.rows[row]
        row['bg'] = '#d9d9d9'
    def get_levels(self):
        return dict([(name, slidervar.get()) 
            for name, slidervar in self.slider_vars.items()])

if __name__ == "__main__":
    reds = Submaster('reds', {'red1' : 20, 'red2' : 30, 'red3' : 80})
    blues = Submaster('blues', {'blue1' : 60, 'blue2' : 80, 'blue3' : 20})

    subs = []
    for scenename in 'warmers house god spot explosion booth stageleft stageright donkey elvis sun fiddler satan lola bed treehouse motel6 deadmics suck burninggels firelights sodacan lighting homestar strongbad coachz pompom marzipan bubs thecheat'.split():
        subs.append(Submaster(scenename, {'dummy' : 20}))

    root = Tk()
    root.wm_geometry('400x400')
    kc = KeyboardComposer(root, subs)
    kc.pack(fill=BOTH, expand=1)
    mainloop()
