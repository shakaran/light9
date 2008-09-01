#!/usr/bin/python2.4
# see http://www.sgi.com/software/opengl/advanced97/notes/node57.html for accum notes

from __future__ import division
import sys, time
import numarray as num
import Tkinter as tk
import Image
from louie import dispatcher

from PyQt4.QtCore import QSize
from PyQt4.QtOpenGL import QGLWidget
from OpenGL.GL import *

def xxxdrawWithAlpha(imgString, w, h, alpha):
    # this one should be faster because GL does the alpha adjust, but
    # i don't think it works yet
    
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glClear(GL_COLOR_BUFFER_BIT)
    #glBlendColor(1, 1, 1, mag) # needs ARB_imaging
    glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, imgString)

class Surface(QGLWidget):
    """widget that adds multiple image files together with adjustable scales"""
    def __init__(self, parent, filenames, imgRescaleTo=None):
        """
        imgRescaleTo can be a length of pixels to reduce all the input
        images into. Try 64 for a low res drawing.
        """
        QGLWidget.__init__(self, parent)

        self.levels = {} # filename : brightness
  
        self.image = {} # filename : imgstr
        for filename in filenames:
            print "open", filename
            im = Image.open(filename)
            self.origImageSize = im.size[0], im.size[1]
            if imgRescaleTo:
                im.thumbnail((imgRescaleTo, imgRescaleTo))
            im = im.transpose(Image.FLIP_TOP_BOTTOM)
            self.imageWidth = im.size[0]
            self.imageHeight = im.size[1]
            self.image[filename] = im.convert("RGBA").tostring()
  
    def initializeGL(self): 
        glDisable(GL_CULL_FACE)
        glShadeModel(GL_FLAT)
        print 'GL_ARB_imaging', 'GL_ARB_imaging' in glGetString(GL_EXTENSIONS)
        import OpenGL
        print OpenGL.__version__
       
    def sizeHint(self):
        return QSize(*self.origImageSize)

    def paintGL(self):
        """you set self.levels to dict and call tkRedraw"""
        assert 'GL_ARB_imaging' in glGetString(GL_EXTENSIONS).split()
        start = time.time()
        
        glClearColor(0.0, 0.0, 0.0, 0)
        glClear( GL_COLOR_BUFFER_BIT |GL_ACCUM_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE) # add
        
#        l=glGenLists(1)
#        glNewList(l,GL_COMPILE)
#        glEndList()

        # drawing to glAccum might be good
        layerTimes = []
        layers = 0
        for filename, mag in self.levels.items():
            t = time.time()
            layers += self.drawWithAlpha(self.image[filename],
                                         self.imageWidth, self.imageHeight, mag)
            layerTimes.append(time.time() - t)

        dispatcher.send("status", key="visibleLayers", value=str(layers))

        dispatcher.send("status", key="redraw",
                        value="%.1fms" % ((time.time() - start) * 1000))
        

    def drawWithAlpha(self, imgString, w, h, alpha):
        """without opengl extensions. Returns number of layers drawn"""
        if alpha == 0:
            return 0
        t = time.time()
        ar = num.reshape(num.fromstring(imgString, dtype='uint8'),
                         (w * h, 4))
        #print "  tonum", time.time() - t
        if alpha != 1:
            ar[:,3] *= alpha

        #print "  scl", time.time() - t

        # this might be a good way to scale the color channels too,
        # but the blend might take two steps. Anyway,
        # GL_CONSTANT_COLOR seems not to work, so i'm not exploring
        # this right now.
        #glBlendFunc(GL_CONSTANT_COLOR, GL_ONE)
        #glBlendColor(.8, .5, .5, .5)

        glPixelZoom(self.width() / w, self.height() / h)
        glDrawPixels(w, h,
                     GL_RGBA, GL_UNSIGNED_BYTE, ar.tostring())
        #print "  draw", time.time() - t
        return 1

    def newLevels(self, event=None, levels=None):
        if levels != self.levels:
            self.levels = levels
            self.updateGL()


##     def mousePressEvent(self, event):
##         self.lastPos = QtCore.QPoint(event.pos())

##     def mouseMoveEvent(self, event):
##         dx = event.x() - self.lastPos.x()
##         dy = event.y() - self.lastPos.y()
##         rot = (.25*dy, .25*dx, 0)
##         if event.buttons() & QtCore.Qt.LeftButton:
##             self.emit(QtCore.SIGNAL("rotationChanged"), rot)
##         elif event.buttons() & QtCore.Qt.MidButton:
##             self.emit(QtCore.SIGNAL("camDistChanged"), .01*dy)            

##         self.lastPos = QtCore.QPoint(event.pos())

def main():
    root = tk.Frame()
    root.pack(expand=True, fill='both')
    QuitButton = tk.Button(root, {'text':'Quit'})
    QuitButton.bind('<ButtonRelease-1>', sys.exit)
    QuitButton.pack()

    filenames=['skyline/bg.png',
               'skyline/cyc-lo-red.png',
               'skyline/cyc-lo-grn.png',
               ]
    
    scales = {} # filename : scale
    for f in filenames:
        scales[f] = tk.Scale(
            root, label=f, from_=0, to=1, res=.05, orient='horiz',
            command=lambda *args: ogl.newLevels(
              levels=dict([(f, s.get()) for f,s in scales.items()])))
        scales[f].pack()
    ogl = Surface(root, filenames)
    ogl.pack(side='top', expand=True, fill='both')

    ogl.mainloop()

if __name__ == '__main__':
    main()
                
demo = Surface
