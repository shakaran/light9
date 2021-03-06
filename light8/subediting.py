
from Patch import get_dmx_channel

class Subediting:
    """this class accepts input from Stage and edits subs. the
    Subpanels have widgets to tell us what subs to edit and when to
    save them. this Subediting object has no UI of its own.

    20:41:10 drewp: there are some funny rules
    20:41:37 drewp: if you drag a light that's in the sub you're editing, you'll adjust it from it's position in the sub (Even if that sub is not visialbe, or if the light is doing someting else)
    20:41:57 drewp: but if you touch a light that wasnt in the sub, the current light brightness from the stage gets copied into the sub, and then you adjust frmo there
    20:42:05 drewp: i dont know any other rules; but these seem odd
    20:42:29 drewp: it may be necessary to highluight which lights are already in the sub, so you know what you're doing as soon as you click on one
    """
    def __init__(self,currentoutputlevels):
        self.sub=None
        self.currentoutputlevels = currentoutputlevels
        self.widgets={} # subname : widget list
        self.oldcolors={} # widget : bgcolor

    def refresh(self):
        self.sub=None # this wouldn't last even if we wanted it to;
        # the Sub objects are rebuilt upon reload
        self.widgets={}
        self.oldcolors={}

    def register(self,subname,widget):
        """tell subediting about any widgets that should be highlighted
        when a sub is being edited"""
        if subname not in self.widgets:
            self.widgets[subname]=[]
        self.widgets[subname].append(widget)
        self.oldcolors[widget] = widget.cget('bg')
    
    def setsub(self,sub):
        """sets which (one) sub object should the stage be editing.

        this is called by widgets that are set up in the Subpanels interfaces.
        """
        
        print "subedit: editing ",sub.name
        self.sub = sub
        self.highlighteditsub()
    def highlighteditsub(self, color='red'):
        """based on how widgets got self.register'd, we highlight
        just the row that's being edited"""

        # highlight that row only
        for n,wl in self.widgets.items():
            if n == self.sub.name:
                self.colorsub(n, color)
            else:
                self.colorsub(n, 'restore')

        '''
        # highlight that row only
        for n,wl in self.widgets.items():
            if n==self.sub.name:
                for w in wl:
                    w.config(bg=color)
            else:
                for w in wl:
                    w.config(bg=self.oldcolors[w])
        '''
    def colorsub(self, name, color):
        for w in self.widgets[name]:
            if color == 'restore':
                w.config(bg=self.oldcolors[w])
            else:
                w.config(bg=color)
        
    #
    # next two methods are called by the Stage
    #
    def startlevelchange(self):
        """stage is about to send some level changes. this method is
        called by the Stage."""
        print "subedit: start-------"
        if self.sub is None:
            print "not editing any sub!"
            return

        self.startlevels = self.sub.getlevels()

    def getcurrentlevel(self,lightname):
        try:
            ch = get_dmx_channel(lightname)
        except ValueError:
            return None
        return self.currentoutputlevels[ch]

    def levelchange(self,lightnames,delta):
        """stage sends this message with its light names and a delta
        0..1 measured from the last startlevelchange call. this method is
        called by the Stage"""

#        print "subedit: level change",lightnames,delta
        if self.sub is None:
            print "not editing any sub!"
            return

        updatelevels={}

        for l in lightnames:
            if l not in self.startlevels:
                # level was not in the sub
                cl = self.getcurrentlevel(l)
                if cl is None:
                    print "light '%s' isn't even in the patch! skipping" % l
                    continue
                print "copying current light level",cl,"into the sub"
                self.startlevels[l] = cl 

            updatelevels[l] = min(100,max(0,self.startlevels[l]+delta))

        self.sub.reviselevels(updatelevels)
    
