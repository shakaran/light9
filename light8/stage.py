from Tix import *

def printevent(ev):
    for k in dir(ev):
        if not k.startswith('__'):
            print k,getattr(ev,k)
    print ""

textstyle={'font':'arial 9','fill':'white'}

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

    API:
      __init__(parent,**kw)
        put pass any canvas options you want
        
      setimage(stageimage)
        sets image to given filename (ppm, gif, etc) and resizes the
        canvas to the image size

      addlight(name, location, aim=None)
        location and aim are pixel coord tuples. name will be passed
        back to you in the callback (see below)

      setsubediting(se)
        give a subediting object to receive the 'startlevelchange' and
        'levelchange' messages
      

    """
    def __init__(self,parent,**kw):
        Canvas.__init__(self,parent,**kw)

        self.bind("<ButtonPress>", self.press)
        self.bind("<Motion>", self.motion)
        self.bind("<ButtonRelease>", self.release)
        self.bind("<Control-Key-a>", lambda ev: self.selectall())
        self.bind("<Control-Key-A>", lambda ev: self.clearselection())
#        self.bind("<Control-Shift-Key-a>",self.handlecontrol_a)
        
        self.halo=11 # search radius for clicked items

        self.mode=None # as you perform with the mouse, this goes
                       # from None to 'pressed','rectangle','levelchange', etc

        self.alllights=[]
        self.selectedlights=[]
        self.alllighttags={} # tag: name lookup

        self.subeditor=None

    def setimage(self,stageimage):
        img = Image('photo',file=stageimage)
        self.img=img # can't lose this!
        print img.width()
        self.create_image(0,0,anchor='nw',image=img)
        self.config(width=img.width(),height=img.height())

    def setsubediting(self,subeditor):
        self.subeditor = subeditor
    #
    # selection management
    #
    def updateselectionboxes(self):
        "make selection boxes that match self.selectedlights"
        self.delete("selectbox")
        for l in self.selectedlights:
            for c in self.getlightbboxes(l):
               self.create_rectangle(c[0]-2,c[1]-2,c[2]+2,c[3]+2,
                                     outline='red',tag="selectbox")            

    def selectall(self):
        self.selectedlights= self.alllights[:]
        self.updateselectionboxes()
    def clearselection(self):
        self.selectedlights=[]
        self.updateselectionboxes()

    def markfordynselection(self):
        """call this before calls to replacedynselection"""
        self.origselection = self.selectedlights[:]

    def replacedynselection(self,newlightnames,subtract=0):
        """as a dynamic selection changes, keep calling this function
        with the names of the lights in the dynamic selection. the
        original selection (at the time of markfordynselection) will
        be shown along with any new lights. if subtract=1, the selection will
        be shown MINUS the newlights."""
        if subtract==0:
            # orig selection plus any newlights that weren't in the orig selection
            self.selectedlights = self.origselection[:] + [l for l in newlightnames if l not in self.origselection]
        else:
            # orig selection lights except those that are in the newlightnames list
            self.selectedlights = [l for l in self.origselection if l not in newlightnames]
        self.updateselectionboxes()

    def select(self,lightname,select=1): # select=0 for deselect
        """select or deselect (select=0) a light by name"""
        if select:
            if lightname not in self.selectedlights:
                self.selectedlights.append(lightname)
        elif lightname in self.selectedlights:
            self.selectedlights.remove(lightname)

        self.updateselectionboxes()
                

    #
    # mouse handling
    #
    def press(self,ev):
        
        self.mode='pressed'
        self.mousedownpos=(ev.x,ev.y)
        print "click at",self.mousedownpos

        button=ev.num
        shifted=ev.state & 1
        control=ev.state & 4
        touching=self.findoverlappinglights((ev.x-self.halo,ev.y-self.halo,
                                             ev.x+self.halo,ev.y+self.halo))
        istouching=len(touching)>0

        if button==1:
            if not istouching:
                # clicked in space
                if not shifted and not control and len(self.selectedlights)>0:
                    # either a deselect (if no motion) or a level change (if motion)
                    self.mode = 'deselect-or-rectangle'
                if shifted or control or len(self.selectedlights)==0:
                    # with shift/control, add/subtract lights to selection
                    self.startrectangleselect()

            else:
                # clicked a selectable object
                # toggle selection
                if touching[0] in self.selectedlights:
                    if shifted or control:
                        # deselect
                        self.select(touching[0],0)
                        # and do nothing else
                        self.mode=None
                    if not shifted:
                        # select only this light
                        self.clearselection()
                        self.select(touching[0])
                        # and adjust its level
                        self.startlevelchange()

                else:
                    # clicked a light that wasn't selected
                    if not shifted:
                        self.clearselection()
                    self.select(touching[0])
                    # and adjust levels now
                    self.startlevelchange()

        if button==3:
            self.startlevelchange()

    def motion(self,ev):

        coords=(ev.x,ev.y)

        shifted=ev.state & 1
        control=ev.state & 4

        if self.mode=='deselect-or-rectangle':
            if (coords[0]-self.mousedownpos[0])**2+(coords[1]-self.mousedownpos[1])**2>self.halo**2:
                if not shifted and not control:
                    self.clearselection()
                # they moved enough, it's a level change
                self.startrectangleselect()
                

        if self.mode=='levelchange':
            delta = 1.5 * (self.mousedownpos[1]-ev.y)
            if self.subeditor:
                self.subeditor.levelchange(self.selectedlights,delta)

        if self.mode=='rectangle':
            sr = self.find_withtag('selectrect')
            if not sr:
                # make the selection rectangle
                sr=self.create_rectangle( self.mousedownpos[0],self.mousedownpos[1],coords[0],coords[1],
                                          outlinestipple='gray50',outline='yellow',tag='selectrect')

            # move rectangle with mouse
            self.coords(sr,*(self.mousedownpos+coords))

            # redo the dynselection with the new rectangle
            self.replacedynselection(self.findoverlappinglights((self.mousedownpos+coords),1),
                                     subtract=control)

    def release(self,ev):
        if self.mode:
            if self.mode=='rectangle':
                self.delete('selectrect')

            if self.mode=='deselect-or-rectangle':
                # they didn't move enough to promote the mode to level, so it's a deselect click
                self.clearselection()
            
            self.mode=None

    #
    #
    #
            
    def startlevelchange(self):
        """sets mode to levelchange AND notifies subeditor. this
        should be done exactly once (per mouse drag), when you first
        decide the mode is levelchange"""
        self.mode='levelchange'
        if self.subeditor:
            self.subeditor.startlevelchange()
    def startrectangleselect(self):
        """sets mode to rectangle AND checkpoints the current selection"""
        self.mode='rectangle'
        self.markfordynselection()
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
            self.create_line(location[0],location[1],aim[0],aim[1],fill='lightblue',
                             arrow='last',arrowshape="9 15 6",tag='light')
        # shadow
        self.create_text(location[0]-1,location[1]+6,
                         anchor='n',text=name,fill='black',
                         tag=tags,**dict([(k,v) for k,v in textstyle.items() if k!='fill']))
        # text
        self.create_text(location[0],location[1]+5,anchor='n',text=name,tag=tags,**textstyle)
        
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
        "returns all the different names for lights that are within (or enclosed by) the box"
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


def createlights(s):
    s.setimage('guysanddolls.gif')
    s.addlight('desk1',(46, 659),    aim=(210, 381))
    s.addlight('marry1',(78, 661),   aim=(398, 428))
    s.addlight('b13',(110, 661))   
    s.addlight('hotbox1',(147, 657), aim=(402, 327))
    s.addlight('edge',(179, 651),    aim=(116, 441))
    s.addlight('phone',(214, 652),   aim=(651, 417))
    s.addlight('cuba1',(315, 656),   aim=(559, 407))
    s.addlight('b22',(347, 661),     aim=(247, 458))
    s.addlight('b23',(379, 661))  
    s.addlight('b24',(417, 661))  
    s.addlight('b25',(455, 658),     aim=(520, 466))
    s.addlight('desk2',(490, 655),   aim=(237, 375))
    s.addlight('rock',(571, 655),    aim=(286, 304))
    s.addlight('b32',(606, 650))  
    s.addlight('hotbox2',(637, 650), aim=(433, 337))
    s.addlight('b34',(671, 651))   
    s.addlight('marry2',(703, 651),  aim=(429, 426))
    s.addlight('cuba2',(733, 652),   aim=(602, 408))

    s.addlight('sidefill1',(115, 473),aim=(228, 423))
    s.addlight('sidefill2',(617, 475),aim=(526, 425))

    s.addlight('cycright',(485, 164),(483, 109))
    s.addlight('cycleft',(330, 154),(333, 108))

    s.addlight('upfill1',(275, 325),(262, 237))
    s.addlight('upfill2',(333, 326),(330, 229))
    s.addlight('upfill3',(473, 325),(454, 226))
    s.addlight('upfill4',(541, 325),(528, 223))

    s.addlight('god',(369,549))

    s.addlight('patio1',(42, 560),(12, 512))
    s.addlight('patio2',(675, 553),(793, 514))

    s.addlight('hotback',(413, 476),(414, 396))

    s.addlight('main 2',(120, 563) ,aim=(241, 472))
    s.addlight('main 3',(162, 562) ,aim=(140, 425))
    s.addlight('main 4',(208, 560) ,aim=(342, 423))
    s.addlight('main 5',(259, 558) ,aim=(433, 450))
    s.addlight('main 7',(494, 551) ,aim=(420, 458))
    s.addlight('main 8',(528, 554) ,aim=(503, 477))
    s.addlight('main 9',(559, 554) ,aim=(544, 479))
    s.addlight('main 10',(597, 556),aim=(339, 444))
    s.addlight('main 11',(636, 556),aim=(449, 409))

    s.addlight('sidepost2', (785, 609))
    s.addlight('sidepost1', (8, 613))









if __name__=='__main__':
    root=Tk()
    root.tk_focusFollowsMouse()
    root.wm_geometry("+376+330")
    s=Stage(root)
    s.setimage('guysanddolls.gif')
    s.pack()

    createlights(s)

    class subediting_standin:
        def startlevelchange(self):
            print "start lev change"
        def levelchange(self,lights,delta):
            print "change",lights,delta
    s.setsubediting(subediting_standin())
    
    root.mainloop()

