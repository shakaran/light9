from Tkinter import *
from time import time

class FlyingFader(Frame):
    def __init__(self, master, variable, label, fadedur=1.5, font=('Arial', 8),
                 **kw):
        Frame.__init__(self, master)
        self.name = label
        self.variable = variable
        self.fadedur = fadedur
        self.curfade = None
        self.fadetimes = 0, 0

        self.config({'bd':1, 'relief':'raised'})
        scaleopts = {'variable' : variable, 'showvalue' : 0, 'from' : 1.0,
                     'to' : 0, 'res' : 0.001, 'width' : 20, 'length' : 200}
        scaleopts.update(kw)
        
        self.scale = Scale(self, scaleopts)
        self.vlabel = Label(self, text="0.0", width=6, font=font)
        self.label = Label(self, text=label, wraplength=40, font=font)

        self.oldtrough = self.scale['troughcolor']

        self.scale.pack(side=TOP, expand=1, fill=BOTH, anchor='c')
        self.vlabel.pack(side=BOTTOM, expand=0, fill=X)
        self.label.pack(side=BOTTOM, expand=0, fill=X)

        for k in range(1, 10):
            self.scale.bind("<Key-%d>" % k, 
                lambda evt, k=k: self.newfade(k / 10.0, evt))

        self.scale.bind("<Key-0>", lambda evt: self.newfade(100, evt))
        self.scale.bind("<grave>", lambda evt: self.newfade(0, evt))

        self.scale.bind("<1>", self.cancelfade)
        self.scale.bind("<2>", self.cancelfade)
        self.scale.bind("<3>", self.mousefade)

        self.variable.trace('w', self.updatelabel)

    def cancelfade(self, evt):
        self.fadetimes = 0, 0
        self.curfade = 0, self.variable.get()
        self.scale['troughcolor'] = self.oldtrough

    def mousefade(self, evt):
        target = float(self.tk.call(self.scale, 'get', evt.x, evt.y))
        self.newfade(target, evt)

    def isfading(self):
        return self.fadetimes[0] or self.fadetimes[1]

    def newfade(self, newlevel, evt=None, length=None):
        if length is None:
            length = self.fadedur
        mult = 1

        if evt.state & 8 and evt.state & 4: mult = 0.25 # both
        elif evt.state & 8: mult = 0.5 # alt
        elif evt.state & 4: mult = 2   # control

        now = time()
        if not self.isfading():
            self.fadetimes = (now, now + (mult * length))
            self.curfade = (self.variable.get(), newlevel)
        else:
            # already fading
            t1,t2=self.fadetimes
            v1,v2=self.curfade
            rate = abs((v2-v1)/(t2-t1))

            vnow=self.variable.get()
            newdist=abs(newlevel-vnow)
            newdur=newdist/rate

            self.fadetimes = (now,now+newdur)
            self.curfade=(vnow,newlevel)
            
            

        self.scale['troughcolor'] = 'red'

        self.gofade()

    def gofade(self):
        now = time()
        start, end = self.fadetimes
        lstart, lend = self.curfade
        if now > end: 
            self.fadetimes = 0, 0
            self.variable.set(lend)
            self.scale['troughcolor'] = self.oldtrough
            return
        percent = (now - start) / (end - start)
        newvalue = (percent * (lend - lstart)) + lstart
        self.variable.set(newvalue)
        colorfade(self.scale, percent)
        self.after(30, self.gofade)

    def updatelabel(self, *args):
        self.vlabel['text'] = "%.3f" % self.variable.get()
        if self.fadetimes[1] == 0: # no fade
            self.vlabel['fg'] = 'black'
        elif self.curfade[1] > self.curfade[0]:
            self.vlabel['fg'] = 'red'
        else:
            self.vlabel['fg'] = 'blue'

    def get(self):
        return self.scale.get()

    def set(self, val):
        self.scale.set(val)


def colorfade(scale, lev):
    low = (255, 255, 255)
    high = (0, 0, 0)
    out = [int(l+lev*(h-l)) for h, l in zip(high,low)]
    col="#%02X%02X%02X" % tuple(out)
    scale.config(troughcolor=col)

if __name__ == '__main__':
    root = Tk()
    root.tk_focusFollowsMouse()

    FlyingFader(root, variable=DoubleVar(), label="suck").pack(side=LEFT, 
        expand=1, fill=BOTH)
    FlyingFader(root, variable=DoubleVar(), label="moof").pack(side=LEFT,
        expand=1, fill=BOTH)
    FlyingFader(root, variable=DoubleVar(), label="zarf").pack(side=LEFT,
        expand=1, fill=BOTH)
    FlyingFader(root, variable=DoubleVar(), 
        label="long name goes here.  got it?").pack(side=LEFT, expand=1, 
        fill=BOTH)

    root.mainloop()
