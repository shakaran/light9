"""all the tiny tk helper functions"""

from Tkinter import *

def make_frame(parent):
    f = Frame(parent, bd=0)
    f.pack(side='left')
    return f

def bindkeys(root,key, func):
    root.bind(key, func)
    for w in root.winfo_children():
        w.bind(key, func)

def toplevelat(x,y,w=None,h=None):
    tl=Toplevel()
    if w and h:
        tl.wm_geometry("%dx%d+%d+%d"%(w,h,x,y))
    else:
        tl.wm_geometry("+%d+%d"%(x,y))
    return tl

def toggle_slider(s):
    if s.get() == 0:
        s.set(100)
    else:
        s.set(0)

# for lambda callbacks    
def printout(t):
    print t
    
def colorlabel(label):
    """color a label based on its own text"""
    txt=label['text'] or "0"
    lev=float(txt)/100
    low=(80,80,180)
    high=(255,55,050)
    out = [int(l+lev*(h-l)) for h,l in zip(high,low)]
    col="#%02X%02X%02X" % tuple(out)
    label.config(bg=col)

class Togglebutton(Button):
    """works like a single radiobutton, but it's a button so the label's on the button face, not to the side"""
    def __init__(self,parent,**kw):
        if kw['variable']:
            self.variable = kw['variable']
            self.variable.trace('w',self.varchanged)
            del kw['variable']
        else:
            self.variable=None
        self.oldcommand = kw.get('command',None)
        kw['command'] = self.invoke
        Button.__init__(self,parent,**kw)

        self.origbkg = self.cget('bg')

        self.state=0
        if self.variable:
            self.state = self.variable.get()

        self.setstate(self.state)

        self.bind("<Enter>",lambda ev: self.setstate)
        self.bind("<Leave>",lambda ev: self.setstate)

    def varchanged(self,*args):
        self.setstate(self.variable.get())
        
    def invoke(self):
        self.setstate(not self.state)
        
        if self.oldcommand:
            self.oldcommand()

    def setstate(self,newstate):
        self.variable.set(newstate)
        if newstate: # set
            self.tk.call('tkButtonDown',self)
            self.config(bg='green')
        else: # unset
            self.tk.call('tkButtonUp',self)
            self.config(bg=self.origbkg)
        return "break"
