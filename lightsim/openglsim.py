# see http://www.sgi.com/software/opengl/advanced97/notes/node57.html for accum notes

import sys
from Image import *
from OpenGL.GL import *
from OpenGL.Tk import *

class Surface:
  def Display(self, event=None):

    glClearColor(0.0, 0.0, 0.0, 0)
    glClear( GL_COLOR_BUFFER_BIT |GL_ACCUM_BUFFER_BIT)

    l=glGenLists(1)
    glNewList(l,GL_COMPILE)
    glEndList()

#    glDrawBuffer(GL_BACK)
                
    for x in range(1,2):

      mag = self.scales[x].get()
      print "pic %i at %f" % (x,mag)
      glClear(GL_COLOR_BUFFER_BIT)
      glDrawPixels(self.imageWidth, self.imageHeight, GL_RGB, GL_UNSIGNED_BYTE, self.image[x])

      if x==0:
        glAccum(GL_LOAD,mag)
      else:
        glAccum(GL_ACCUM,mag)

      # glAccum(GL_ADD,self.x)
      self.x=(self.x+.1)%2.0
      print "return"
      glAccum(GL_RETURN,1)

  def SetupWindow(self):
    self.OglFrame = Frame()
    self.OglFrame.pack(side = 'top',fill='both',expand=1)
    self.QuitButton = Button(self.OglFrame, {'text':'Quit'})
    self.QuitButton.bind('<ButtonRelease-1>', sys.exit)
    self.QuitButton.pack({'side':'top'})
  
  
  def SetupOpenGL(self):
    self.ogl = Opengl(master=self.OglFrame, width = 270, height = 270, double = 1, depth = 0)
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
    for filename in ('pic1.ppm','pic2.ppm'):
      im = open(filename)
      self.imageWidth = im.size[0]
      self.imageHeight = im.size[1]
      self.image.append(im.tostring("raw", "RGB", 0, -1))
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
