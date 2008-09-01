# lightsim.py by Drew Perttula, 6/28/2002
from __future__ import division

version="1.01"

import Image, ImageTk, ImageChops,ImageEnhance
from Tkinter import Tk,Label,Scale,DoubleVar,Frame
import time, glob

class Imagemixer(Label):
    """tk widget that can load images (based on a glob pattern: each file should
    be named like 'scene.light') and displays a weighted mix of the images"""
    def __init__(self,parent,*k,**kw):
        Label.__init__(self,parent,*k,**kw)
        self.im={}

        self.itk = ImageTk.PhotoImage(Image.new('RGB',(100,100)))
        self.config(image=self.itk)
        self.loadedscale=0
        self.amounts={}
        
    def loadallimgs(self,basename,scalefactor=1.0):
        """load images from disk, scale them immediately, subtract off
        the image called 'ambient' (if present) from all other
        images. Given basename like path/to/foo, loads images with
        names like path/to/foo.light1, path/to/foo.light2, etc.  The
        filename after the . is considered to be the light name
        throughout the program.  """

        if self.loadedscale==scalefactor: # already loaded at this scale
            return
        
        self.im={}
        ambientimg=None
        sizenotset=1
        for fullname in glob.glob(basename+".*"):
            x=fullname[fullname.find('.')+1:]
            self.im[x]=Image.open(fullname)
            if scalefactor!=1.0:
                self.im[x]=self.im[x].resize([a*scalefactor for a in self.im[x].size])
            if x=='ambient':
                ambientimg=self.im[x]
            if sizenotset:
                self.config(width=self.im[x].size[0],height=self.im[x].size[1])
                self.itk=ImageTk.PhotoImage(Image.new('RGB',self.im[x].size))
                self.config(image=self.itk)
                sizenotset=0

        # subtract off an image called 'ambient' from all the rest
        if ambientimg is not None:
            for k in self.im.keys():
                if k!='ambient':
                    self.im[k] = ImageChops.subtract(self.im[k],ambientimg)

        self.loadedscale=scalefactor
        self._remix() # update the image

    def _remix(self):
        """mix all the images in self.im together according to the
        weights in self.amounts.  Each of those attributes are dicts
        with the light names for keys."""
        global fpslabel
        i=None
        amounts = self.amounts
        layers=0
        start=time.time()
        for k in self.im.keys():
            scale =amounts.get(k,0)
            if scale!=0:
                layers+=1
                acc=ImageEnhance.Brightness(self.im[k]).enhance(scale) # scale the image before adding
    #            acc = ImageChops.add(base,self.im[k],1/scale) ## slower!
                if i==None:
                    i=acc # use first layer directly
                else:
                    i=ImageChops.add(i,acc) # add subsequent layers
        dur = time.time()-start
        fps=1.0/dur
        fpslabel.config(text="%.02f fps, %.02f layers/sec"%(fps,layers/dur))
        if i is not None:
            self.itk.paste(i) # put image i in the PhotoImage

    def setamounts(self,amounts):
        self.amounts = amounts.copy()
        self._remix()

    def lightnames(self):
        return self.im.keys()

basename='room'

root=Tk()

# Imagemixer._remix accesses this label, so it needs a name
fpslabel=Label()
fpslabel.pack()

Label(root,text="Use +/- to change image scale").pack()

mix=Imagemixer(root,relief='raised',bd=3)

scalefactor=.5
mix.loadallimgs(basename,scalefactor)
mix.pack()

#
# +/- keys should reload the images at new scales
#
def changescale(by=0):
    global mix,scalefactor
    scalefactor+=by
    mix.loadallimgs(basename,scalefactor)
root.bind("<Key-plus>",lambda ev: changescale(.15))
root.bind("<Key-minus>",lambda ev: changescale(-.15))
         
amountvars={} # each light name maps to a Tkinter.DoubleVar object which the Scale adjusts

def redraw(*args):
    global l,amountvars,update
    # read the value out of each Scale
    amounts = dict([(k,v.get()) for k,v in amountvars.items()])
    mix.setamounts(amounts)
    
for x in mix.lightnames():
    # the Scale sets this; the redraw() callback reads it
    amountvars[x]=DoubleVar()

    # a new frame for each slider row
    f=Frame(root,bd=1,relief='groove')
    f.pack(fill='x',expand=1)
    # title
    Label(f,text=x,width=10,anchor='e').pack(side='left')
    # slider
    s=Scale(f,from_=0,to=1,res=.01,
            orient='horiz',
            variable=amountvars[x],command=redraw)
    s.pack(side='left',fill='x',expand=1)
    if x=='ambient': # the 'ambient' level (if present) starts at 1
        s.set(1)

root.mainloop()

