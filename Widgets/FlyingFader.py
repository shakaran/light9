from Tkinter import *
from time import time,sleep
from __future__ import division

class Mass:
    def __init__(self):
        self.x=0 # position
        self.xgoal=0 # position goal
        
        self.v=0 # velocity
        self.maxspeed = .8 # maximum speed, in position/second
        self.maxaccel = 3 # maximum acceleration, in position/second^2
        self.eps = .03 # epsilon - numbers within this much are considered the same

        self._lastupdate=time()
        self._stopped=1

    def equal(self,a,b):
        return abs(a-b)<self.eps

    def stop(self):
        self.v=0
        self.xgoal=self.x
        self._stopped=1
        
    def update(self):
        t0 = self._lastupdate
        tnow = time()
        self._lastupdate = tnow

        dt = tnow-t0

        self.x += self.v*dt
        # hitting the ends stops the slider
        if self.x>1: self.v=max(self.v,0); self.x=1
        if self.x<0: self.v=min(self.v,0); self.x=0
            
        if self.equal(self.x,self.xgoal):
            self.x=self.xgoal # clean up value
            self.stop()
            return
        
        self._stopped=0
        dir = (-1.0,1,0)[self.xgoal>self.x]

        if abs(self.xgoal-self.x) < abs(self.v*5*dt):
            # apply the brakes on the last 5 steps
            dir *= -.5

        self.v += dir*self.maxaccel*dt # velocity changes with acceleration in the right direction
        self.v = min(max(self.v,-self.maxspeed),self.maxspeed) # clamp velocity

        #print "x=%+.03f v=%+.03f a=%+.03f %f" % (self.x,self.v,self.maxaccel,self.xgoal)

    def goto(self,newx):
        self.xgoal=newx

    def ismoving(self):
        return not self._stopped

class FlyingFader(Frame):
    def __init__(self, master, variable, label, fadedur=1.5, font=('Arial', 8),
                 **kw):
        Frame.__init__(self, master)
        self.name = label
        self.variable = variable

        self.mass = Mass()
        
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

        self.scale.bind("<Key-0>", lambda evt: self.newfade(1.0, evt))
        self.scale.bind("<grave>", lambda evt: self.newfade(0, evt))

        self.scale.bind("<1>", self.cancelfade)
        self.scale.bind("<2>", self.cancelfade)
        self.scale.bind("<3>", self.mousefade)

        self.variable.trace('w', self.updatelabel)

    def cancelfade(self, evt):
        self.fadegoal = self.variable.get()
        self.fadevel = self.fadeacc = 0

        self.scale['troughcolor'] = self.oldtrough

    def mousefade(self, evt):
        target = float(self.tk.call(self.scale, 'get', evt.x, evt.y))
        self.newfade(target, evt)

    def ismoving(self):
        return self.fadevel!=0 or self.fadeacc!=0

    def newfade(self, newlevel, evt=None, length=None):

        # these are currently unused-- Mass needs to accept a speed input
        mult = 1
        if evt.state & 8 and evt.state & 4: mult = 0.25 # both
        elif evt.state & 8: mult = 0.5 # alt
        elif evt.state & 4: mult = 2   # control


        self.mass.x = self.variable.get()
        self.mass.goto(newlevel)

        self.gofade()

    def gofade(self):
        self.mass.update()
        self.variable.set(self.mass.x)

        if not self.mass.ismoving():
            self.scale['troughcolor'] = self.oldtrough
            return
        
        # blink the trough while the thing's moving
        if time()%.4>.2:
            # self.scale.config(troughcolor=self.oldtrough)
            self.scale.config(troughcolor='orange')
        else:
            # self.scale.config(troughcolor='white')
            self.scale.config(troughcolor='yellow')

#        colorfade(self.scale, percent)
        self.after(30, self.gofade)

    def updatelabel(self, *args):
        self.vlabel['text'] = "%.3f" % self.variable.get()
#        if self.fadetimes[1] == 0: # no fade
#            self.vlabel['fg'] = 'black'
#        elif self.curfade[1] > self.curfade[0]:
#            self.vlabel['fg'] = 'red'
#        else:
#            self.vlabel['fg'] = 'blue'

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
