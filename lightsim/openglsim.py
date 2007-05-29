# see http://www.sgi.com/software/opengl/advanced97/notes/node57.html for accum notes

import sys, time
import numpy as num
from OpenGL.GL import *
from OpenGL.Tk import *
import Image

def drawWithAlpha(imgString, w, h, alpha):
    """without opengl extensions"""
    t = time.time()
    ar = num.reshape(num.fromstring(imgString, dtype='uint8'),
                     (w * h, 4))
    print "  tonum", time.time() - t
    ar[:,3] *= alpha

    print "  scl", time.time() - t
    glDrawPixels(w, h,
                 GL_RGBA, GL_UNSIGNED_BYTE, ar.tostring())
    print "  draw", time.time() - t
  

class Surface:
  def Display(self, event=None):
    assert 'GL_ARB_imaging' in glGetString(GL_EXTENSIONS).split()
    
    glClearColor(0.0, 0.0, 0.0, 0)
    glClear( GL_COLOR_BUFFER_BIT |GL_ACCUM_BUFFER_BIT)
    glEnable(GL_BLEND)
    #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBlendFunc(GL_SRC_ALPHA, GL_DST_ALPHA)
    l=glGenLists(1)
    glNewList(l,GL_COMPILE)
    glEndList()

#    glDrawBuffer(GL_BACK)
                
    for x, img in enumerate(self.image):
      mag = self.scales[x].get()
      print "pic %i at %f" % (x,mag)
#      glClear(GL_COLOR_BUFFER_BIT)
      #glBlendColor(1, 1, 1, mag) # needs ARB_imaging
      drawWithAlpha(img, self.imageWidth, self.imageHeight, mag)


##       if x==0:
##         glAccum(GL_LOAD,mag)
##       else:
##         glAccum(GL_ACCUM,mag)

      # glAccum(GL_ADD,self.x)
      self.x=(self.x+.1)%2.0
##       glAccum(GL_RETURN,1)

  def SetupWindow(self):
    self.OglFrame = Frame()
    self.OglFrame.pack(side = 'top',fill='both',expand=1)
    self.QuitButton = Button(self.OglFrame, {'text':'Quit'})
    self.QuitButton.bind('<ButtonRelease-1>', sys.exit)
    self.QuitButton.pack({'side':'top'})
  
  
  def SetupOpenGL(self):
    self.ogl = Opengl(master=self.OglFrame, width = 512, height = 270, double = 1, depth = 0)
    self.ogl.pack(side = 'top', expand = 1, fill = 'both')
    self.ogl.set_centerpoint(0, 0, 0)
    self.ogl.redraw = self.Display
  
    for x in range(0,2):
      self.scales[x] = Scale(self.OglFrame,label="s%i"%x,from_=0,to=1,res=.05,orient='horiz',command=self.ogl.tkRedraw)
      self.scales[x].pack()
  
  
  def __init__(self):
    self.x=0
    self.scales=[None,None]
  
    self.SetupWindow()
  
    self.image=[]
    for filename in ('skyline/bg.png', 'skyline/cyc-lo-red.png'):
      im = Image.open(filename)
      im.thumbnail((200, 200))
      self.imageWidth = im.size[0]
      self.imageHeight = im.size[1]
      self.image.append(im.convert("RGBA").tostring())#"raw", "RGB", 0, -1))
      print self.imageWidth, self.imageHeight, self.imageWidth * self.imageHeight*4, len(self.image)
  
    self.SetupOpenGL()
  
    glDisable(GL_CULL_FACE)
    #         glEnable(GL_DEPTH_TEST)
    #         glEnable(GL_NORMALIZE)
    glShadeModel(GL_FLAT)
  
    self.ogl.tkRedraw()
    self.ogl.mainloop()

if __name__ == '__main__':
  Surface()
                
demo = Surface
