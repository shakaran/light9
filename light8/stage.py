from Tkinter import *


def printevent(ev):
    for k in dir(ev):
        if not k.startswith('__'):
            print k,getattr(ev,k)
    print ""


class Stage(Canvas):
    
    """a fancy widget that shows light locations (and optionally their
    aim locations on an image of the stage. you can select or
    multiselect lights and drag them up or down to change their
    brightness.

    ctrl-a is select all,
    ctrl-shift-a or clicking on no light deselects all,
    re-clicking a light with shift key down toggles whether it's in the selection.
    ctrl-drag-rectangle deselects the lights in the rectangle,
    shift-drag-rectangle selects the lights in the rectangle,
    drag-rectangle selects only the lights in the rectangle.

    a light can be selected on its location point, its aim point
    (which may or may not be present), or its name.

    lights should be able to be interactively 'locked', which blocks
    them from being selected. 

    """
    def __init__(self,parent,**kw):
        Canvas.__init__(self,parent,**kw)

        self.bind("<ButtonPress-1>", self.leftpress)
        self.bind("<B1-Motion>", self.leftmotion)
        self.bind("<ButtonRelease-1>", self.leftrelease)
        
        self.halo=11 # search radius for clicked items

        self.lmbstate=None # as you perform with LMB, this goes from None to 'pressed','rectangle','levelchange'

        self.alllights=[]
        self.selectedlights=[]
        self.alllighttags={} # tag: name lookup


    def setimage(self,stageimage):
        img = Image('photo',file=stageimage)
        self.img=img # can't lose this!
        print img.width()
        self.create_image(0,0,anchor='nw',image=img)
        self.config(width=img.width(),height=img.height())
        
    #
    # selection management
    #
    def updateselectionboxes(self):
        "make selection boxes that match self.selectedlights"
        self.delete("selectbox")
        for l in self.selectedlights:
            for c in self.getlightbboxes(l):
               self.create_rectangle(c[0]-2,c[1]-2,c[2]+2,c[3]+2,outline='red',tag="selectbox")            
    
    def clearselection(self,dyn=0):
        self.selectedlights=[]
        self.updateselectionboxes()

    def markfordynselection(self):
        """call this before calls to replacedynselection"""
        self.origselection = self.selectedlights

    def replacedynselection(self,newlightnames):
        """as a dynamic selection changes, keep calling this function with the
        names of the lights in the dynamic selection. the original selection (at the time
        of markfordynselection) will be shown along with any new lights"""
        self.selectedlights = self.origselection + [l for l in newlightnames if l not in self.origselection]
        self.updateselectionboxes()

    def select(self,lightname,select=1,dyn=0): # select=0 for deselect
        if select:
            if lightname not in self.selectedlights:
                self.selectedlights.append(lightname)
        elif lightname in self.selectedlights:
            self.selectedlights.remove(lightname)

        self.updateselectionboxes()
                

    #
    # LMB click or drag
    #
    def leftpress(self,ev):
        
        self.lmbstate='pressed'
        self.lmbstart=(ev.x,ev.y)

        shifted=ev.state & 1
        control=ev.state & 4
        touching=self.findoverlappinglights((ev.x-self.halo,ev.y-self.halo,ev.x+self.halo,ev.y+self.halo))
        istouching=len(touching)>0

        if not istouching:
            # clicked in space
            if not shifted and not control and len(self.selectedlights)>0:
                # either a deselect (if no motion) or a level change (if motion)
                self.lmbstate = 'deselect-or-level'
            if shifted or control or len(self.selectedlights)==0:
                # with shift/control, add/subtract lights to selection
                self.lmbstate='rectangle'

        else:
            # clicked a selectable object
            # toggle selection
            if touching[0] in self.selectedlights:
                if shifted:
                    # deselect
                    self.select(touching[0],0)
                    # and do nothing else
                    self.lmbstate=None
                else:
                    # select only this light
                    self.clearselection()
                    self.select(touching[0])
                    # and adjust its level
                    self.lmbstate='levelchange'
                    
            else:
                if not shifted:
                    self.clearselection()
                self.select(touching[0])
                # and adjust levels now
                self.lmbstate='levelchange'
                
        if self.lmbstate=='rectangle':
            self.markfordynselection()
    def leftmotion(self,ev):

        coords=(ev.x,ev.y)

        shifted=ev.state & 1
        control=ev.state & 4

        if self.lmbstate=='deselect-or-level':
            if (coords[0]-self.lmbstart[0])**2+(coords[1]-self.lmbstart[1])**2>self.halo**2:
                # they moved enough, it's a level change
                self.lmbstate='levelchange'

        if self.lmbstate=='levelchange':
            delta = self.lmbstart[1]-ev.y
            print "change by",delta

        if self.lmbstate=='rectangle':
            sr = self.find_withtag('selectrect')
            if not sr:
                sr=self.create_rectangle( self.lmbstart[0],self.lmbstart[1],coords[0],coords[1],
                                          outlinestipple='gray50',
                                          tag='selectrect')

            # move rectangle with mouse
            self.coords(sr,*(self.lmbstart+coords))

            # redo the dynselection with the new rectangle
            self.replacedynselection([o for o in self.findoverlappinglights((self.lmbstart+coords),1)])

            # need to handle ctrl

    def leftrelease(self,ev):
        if self.lmbstate:

            if self.lmbstate=='rectangle':
                self.delete('selectrect')

            if self.lmbstate=='deselect-or-level':
                # they didn't move enough to promote the mode to level, so it's a deselect click
                self.clearselection()
            
            # all items that were in dynselection join the selection
#            self.incorporatedynselection()
            
        self.lmbstate=None

    #
    # light names vs. canvas object tags
    #
    def nametag(self,name):
        "returns a safe version of the name that won't match other names"
        return name.replace(" ","__")

    def tagtoname(self,tag):
        "finds the real light name for a tag written by nametag()"
        return self.alllighttags[tag]

    #
    # light methods
    #
    def addlight(self,name,location,aim=None):
        tags='light selectable name_%s' % self.nametag(name)
        
        self.create_oval(location[0]-2,location[1]-2,
                         location[0]+2,location[1]+2,
                         fill='red',tag=tags+" hotspot")
        if aim:
            self.create_oval(aim[0]-2,aim[1]-2,
                             aim[0]+2,aim[1]+2,
                             fill='red',tag=tags+" hotspot")
            self.create_line(location[0],location[1],aim[0],aim[1],stipple='gray50',
                             arrow='last',arrowshape="9 15 6",tag='light')
        self.create_text(location[0],location[1]+5,anchor='n',text=name,tag=tags)
        self.alllights.append(name)
        self.alllighttags[self.nametag(name)]=name

    def getlightbboxes(self,tag):
        """returns a list of bboxes for a light with a given name_ tag. the selection
        mechanism draws around these bboxes to show that a light is selected"""
        bboxes=[]
        for o in self.find_withtag("name_%s" % self.nametag(tag)):
            if 'hotspot' in self.gettags(o):
                bboxes.append(self.bbox(o))
        return bboxes

    def findoverlappinglights(self,box,enclosed=0):
        "returns all the different name_ tags for lights that are within (or enclosed by) the box"
        lights=[]
        if enclosed:
            candidates = self.find_enclosed(*box)
        else:
            candidates = self.find_overlapping(*box)
            
        for o in candidates:
            for t in self.gettags(o):
                if t.startswith("name_"):
                    n = self.tagtoname(t[5:])
                    if n and (n not in lights):
                        lights.append(n)
        return lights

root=Tk()
root.wm_geometry("+376+330")
s=Stage(root)
s.setimage('guysanddolls.gif')
s.pack()
s.addlight('drew',(330,640),(90,20))
s.addlight('house',(360,640))
s.addlight('barn',(390,640))

root.mainloop()
