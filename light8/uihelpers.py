"""all the tiny tk helper functions"""

from __future__ import nested_scopes
from Tkinter import *
from Tix import *
from types import StringType

windowlocations = {
    'sub' : '425x738+00+00',
    'console' : '168x24+848+000',
    'leveldisplay' : '144x340+870+400',
    'cuefader' : '314x212+546+741',
    'effect' : '24x24+0963+338',
    'stage' : '823x683+37+030',
    'scenes' : '504x198+462+12',
}

def make_frame(parent):
    f = Frame(parent, bd=0, bg='black')
    f.pack(side='left')
    return f

def bindkeys(root,key, func):
    root.bind(key, func)
    for w in root.winfo_children():
        w.bind(key, func)


def toplevel_savegeometry(tl,name):
    try:
        geo = tl.geometry()
        if not geo.startswith("1x1"):
            f=open(".light9-window-geometry-%s" % name.replace(' ','_'),'w')
            f.write(tl.geometry())
        # else the window never got mapped
    except:
        # it's ok if there's no saved geometry
        pass

    # this would get called repeatedly for each child of the window (i
    # dont know why) so we unbind after the first Destroy event
    tl.unbind("<Destroy>",tl._toplevelat_funcid)

def toplevelat(name):
    tl = Toplevel()

    try:
        f=open(".light9-window-geometry-%s" % name.replace(' ','_'))
        windowlocations[name]=f.read() # file has no newline
    except:
        # it's ok if there's no saved geometry
        pass

    if name in windowlocations:
        tl.geometry(windowlocations[name])

    tl._toplevelat_funcid=tl.bind("<Destroy>",lambda ev,tl=tl,name=name: toplevel_savegeometry(tl,name))

    return tl

def toggle_slider(s):
    if s.get() == 0:
        s.set(100)
    else:
        s.set(0)

# for lambda callbacks    
def printout(t):
    print t

def printevent(ev):
    for k in dir(ev):
        if not k.startswith('__'):
            print k,getattr(ev,k)
    print ""
    
def eventtoparent(ev,sequence):
    "passes an event to the parent, screws up TixComboBoxes"

    wid_class = str(ev.widget.__class__)
    if wid_class == 'Tix.ComboBox' or wid_class == 'Tix.TixSubWidget':
        return

    evdict={}
    for x in ['state', 'time', 'y', 'x', 'serial']:
        evdict[x]=getattr(ev,x)
#    evdict['button']=ev.num
    par=ev.widget.winfo_parent()
    if par!=".":
        ev.widget.nametowidget(par).event_generate(sequence,**evdict)
    #else the event made it all the way to the top, unhandled

def colorlabel(label):
    """color a label based on its own text"""
    txt=label['text'] or "0"
    lev=float(txt)/100
    low=(80,80,180)
    high=(255,55,050)
    out = [int(l+lev*(h-l)) for h,l in zip(high,low)]
    col="#%02X%02X%02X" % tuple(out)
    label.config(bg=col)

# TODO: get everyone to use this
def colorfade(low, high, percent):
    '''not foolproof.  make sure 0 < percent < 1'''
    out = [int(l+percent*(h-l)) for h,l in zip(high,low)]
    col="#%02X%02X%02X" % tuple(out)
    return col

def colortotuple(anytkobj, colorname):
    'pass any tk object and a color name, like "yellow"'
    rgb = anytkobj.winfo_rgb(colorname)
    return [v / 256 for v in rgb]

class Togglebutton(Button):
    """works like a single radiobutton, but it's a button so the
    label's on the button face, not to the side. the optional command
    callback is called on button set, not on unset. takes a variable
    just like a checkbutton"""
    def __init__(self,parent,variable=None,command=None,downcolor='red',**kw):

        self.oldcommand = command
        Button.__init__(self,parent,command=self.invoke,**kw)

        self._origbkg = self.cget('bg')
        self.downcolor = downcolor

        self._variable = variable
        if self._variable:
            self._variable.trace('w',self._varchanged)
            self._setstate(self._variable.get())
        else:
            self._setstate(0)

        self.bind("<Return>",self.invoke)
        self.bind("<1>",self.invoke)
        self.bind("<space>",self.invoke)

    def _varchanged(self,*args):
        self._setstate(self._variable.get())
        
    def invoke(self,*ev):
        if self._variable:
            self._variable.set(not self.state)
        else:
            self._setstate(not self.state)
        
        if self.oldcommand and self.state: # call command only when state goes to 1
            self.oldcommand()
        return "break"

    def _setstate(self,newstate):
        self.state = newstate
        if newstate: # set
            self.config(bg=self.downcolor,relief='sunken')
        else: # unset
            self.config(bg=self._origbkg,relief='raised')
        return "break"


class FancyDoubleVar(DoubleVar):
    def __init__(self,master=None):
        DoubleVar.__init__(self,master)
        self.callbacklist = {} # cbname : mode
        self.namedtraces = {} # name : cbname
    def trace_variable(self,mode,callback):
        """Define a trace callback for the variable.

        MODE is one of "r", "w", "u" for read, write, undefine.
        CALLBACK must be a function which is called when
        the variable is read, written or undefined.

        Return the name of the callback.
        """
        cbname = self._master._register(callback)
        self._tk.call("trace", "variable", self._name, mode, cbname)
        
        # we build a list of the trace callbacks (the py functrions and the tcl functionnames)
        self.callbacklist[cbname] = mode
#        print "added trace:",callback,cbname
        
        return cbname
    trace=trace_variable
    def disable_traces(self):
        for cb,mode in self.callbacklist.items():
#            DoubleVar.trace_vdelete(self,v[0],k)
            self._tk.call("trace", "vdelete", self._name, mode,cb)
            # but no master delete!
            
    def recreate_traces(self):
        for cb,mode in self.callbacklist.items():
#            self.trace_variable(v[0],v[1])
            self._tk.call("trace", "variable", self._name, mode,cb)

    def trace_named(self, name, callback):
        if name in self.namedtraces:
            print "FancyDoubleVar: already had a trace named %s - replacing it" % name
            self.delete_named(name)

        cbname = self.trace_variable('w',callback) # this will register in self.callbacklist too
        
        self.namedtraces[name] = cbname
        return cbname
        
    def delete_named(self, name):
        if name in self.namedtraces:

            cbname = self.namedtraces[name]
            
            self.trace_vdelete('w',cbname)
	    #self._tk.call("trace","vdelete",self._name,'w',cbname)
            print "FancyDoubleVar: successfully deleted trace named %s" % name
        else:
            print "FancyDoubleVar: attempted to delete named %s which wasn't set to any function" % name

def get_selection(listbox):
    'Given a listbox, returns first selection as integer'
    selection = int(listbox.curselection()[0]) # blech
    return selection

if __name__=='__main__':
    root=Tk()
    root.tk_focusFollowsMouse()
    iv=IntVar()
    def cb():
        print "cb!"
    t = Togglebutton(root,text="testbutton",command=cb,variable=iv)
    t.pack()
    Entry(root,textvariable=iv).pack()
    root.mainloop()
