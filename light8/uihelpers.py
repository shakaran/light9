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
