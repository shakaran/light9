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
        if 'stageimage' in kw:
            stageimage=kw['stageimage']
            del kw['stageimage']
        else:
            stageimage=None

        Canvas.__init__(self,parent,**kw)

        if stageimage:
            img = Image('photo',stageimage)
            self.create_image(0,0,anchor='nw',image=img)
        self.create_rectangle(5,5,50,50)

        self.bind("<ButtonPress-1>", self.leftpress)
        self.bind("<B1-Motion>", self.leftmotion)
        self.bind("<ButtonRelease-1>", self.leftrelease)
        
        self.halo=11 # search radius for clicked items

        self.lmbstate=None # as you perform with LMB, this goes from None to 'pressed','rectangle','levelchange'

        self.alllights=[]
        self.selectedlights=[]

    #
    # selection management
    #
    def clearselection(self,dyn=0):
        if dyn:
            seltag="dynselection"
        else:
            seltag="selection"       
        for o in self.find_withtag(seltag):
            self.select(o,0,dyn)

    def replacedynselection(self,newlightnames):
        for o in self.find_withtag('dynselection'):
            self.select(o,0,1)
        for o in newlightnames:
            self.select(o,1,1)

    def select(self,obj,select=1,dyn=0): # select=0 for deselect
        if dyn:
            seltag="dynselection"
        else:
            seltag="selection"
        if select:
            print obj,"into selection"
            self.addtag_withtag(seltag,obj)
            for c in self.getlightbboxes(obj):
                self.create_rectangle(c[0]-2,c[1]-2,c[2]+2,c[3]+2,outline='red',tag="selectbox_%s"%obj)
        else:
            print obj,"out of select"
            self.dtag(obj,seltag)
            if 'selection' not in self.gettags(obj) and 'dynselection' not in self.gettags(obj):
                self.delete("selectbox_%s"%obj)
                
    def incorporatedynselection(self):
        "put all dynselected objects in the regular selection"
        for o in self.find_withtag('dynselection'):
            self.dtag(o,'dynselection')
            self.addtag_withtag('selection',o)
            # no change for the graphics

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
            if not shifted and not control:
                # either a deselect (if no motion) or a level change (if motion)
                self.clearselection()
                self.lmbstate='rectangle'
            if shifted or control:
                # with shift/control, add/subtract lights to selection
                self.lmbstate='rectangle'

        else:
            # clicked a selectable object
            # toggle selection
            if 'selection' in self.gettags(touching[0]):
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
                
        
    def leftmotion(self,ev):

        coords=(ev.x,ev.y)

        shifted=ev.state & 1
        control=ev.state & 4

        if self.lmbstate=='levelchange':
            delta = self.lmbstart[1]-ev.y
            print "change by",delta

        if self.lmbstate=='rectangle':
            sr = self.find_withtag('selectrect')
            if not sr:
                sr=self.create_rectangle( self.lmbstart[0],self.lmbstart[1],coords[0],coords[1],tag='selectrect')
#                sr=self.create_rectangle( *(self.lmbstart+coords), tag='selectrect' )

            self.coords(sr,*(self.lmbstart+coords))

            # redo the dynselection with the new rectangle
            self.replacedynselection([o for o in self.findoverlappinglights((self.lmbstart+coords),1)])

            # need to handle ctrl

    def leftrelease(self,ev):
        if self.lmbstate:

            if self.lmbstate=='rectangle':
                self.delete('selectrect')
            
            # all items that were in dynselection join the selection
            self.incorporatedynselection()
            
        self.lmbstate=None

    def nametag(self,name):
        "returns a safe version of the name that won't match other names"
        return name.replace(" ","__")

    def addlight(self,name,location,aim=None):

        tags='light selectable name_%s' % self.nametag(name)
        
        self.create_oval(location[0]-2,location[1]-2,
                         location[0]+2,location[1]+2,
                         fill='red',tag=tags+" hotspot")
        self.create_text(location[0],location[1]+5,anchor='n',text=name,tag=tags)
        self.alllights.append(name)

    def getlightbboxes(self,tag):
        """returns a list of bboxes for a light with a given name_ tag. the selection
        mechanism draws around these bboxes to show that a light is selected"""
        bboxes=[]
        for o in self.find_withtag(tag):
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
                if t.startswith("name_") and t not in lights:
                    lights.append(t)
        return lights

root=Tk()
s=Stage(root,stageimage='guysanddolls.ppm')
s.addlight('drew',(80,80))
s.addlight('house',(150,80))
s.addlight('barn',(200,80))
s.pack()

root.mainloop()
