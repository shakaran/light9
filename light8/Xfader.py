from Tix import *
from __future__ import division

class Xfader(Canvas):
    def __init__(self, scalelevelsIn):
        global scalelevels
        scalelevels=scalelevelsIn
        self.checkbuttons={}
        self.startcoord=None
    def sub2(self,a,b):
        return ( (a[0]-b[0]), (a[1]-b[1]))
    def down(self,ev):
        global scalelevels
        self.startcoord=(ev.x,-ev.y)
        self.startlevels = dict([(k,v.get()) for k,v in scalelevels.items()])
        # find the channel names of the selected subs
        self.onchannel = {
            'x':[x for x in scalelevels.keys() if self.checkbuttons[x]['x'].get()],
            'y':[x for x in scalelevels.keys() if self.checkbuttons[x]['y'].get()]
            }

        
        #self.create_line(0,0,100,100,tag='transient')
        
    def getoriglevel(self,subname):
        return self.startlevels[subname]
    def up(self,ev):
        self.startcoord=None
        self.delete('transient')
        # self.clearallbuttons()
    def moved(self,ev):
        if self.startcoord is None:
            return
        pos=(ev.x,-ev.y)
        deltas= self.sub2(pos,self.startcoord)
        for axis,delta in zip(('x','y'),deltas):
            onchan=self.onchannel[axis]
            for subn in onchan:
                newlev = self.getoriglevel(subn) + 1.0*delta/75
                newlev = int(newlev*1000)/1000.0
                newlev = min(1.0,max(newlev,0.0))
                scalelevels[subn].set( newlev )
    def width(self):
        return int(self['width'])
    def height(self):
        return int(self['height'])
    def setupwidget(self,parent):
        Canvas.__init__(self,parent,width=150,height=150,bg="#ff0000")
        self.pack(side='bottom')
        self.create_rectangle(5,5,self.width()-5,self.height()-5)
        self.create_line(0,self.height()/2,150,self.height()/2)
        self.create_line(self.width()/2,0,self.width()/2,self.height())
        self.bind("<ButtonPress-1>",self.down)
        self.bind("<ButtonRelease-1>",self.up)
        self.bind("<B1-Motion>",self.moved)

    def registerbutton(self,subname,axis,checkvar):
        if subname not in self.checkbuttons:
            self.checkbuttons[subname]={}
        self.checkbuttons[subname][axis]=checkvar
    def clearallbuttons(self, axis='both'):
        for cb in self.checkbuttons.values():
            if axis == 'both':
                for a in cb.values():
                    a.set(0)
            else:
                cb[axis].set(0)
    def grab(self,axis):
        self.clearallbuttons(axis)
        for n,sv in scalelevels.items():
            if sv.get() and n != 'blacklight':
                self.checkbuttons[n][axis].set(1)


