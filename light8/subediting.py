
from Patch import get_dmx_channel

class Subediting:
    """this class accepts input from Stage and edits subs. the
    Subpanels have widgets to tell us what subs to edit and when to
    save them. this Subediting object has no UI of its own.

    20:41:10 drewp: there are some funny rules
    20:41:37 drewp: if you drag a light that's in the sub you're editing, you'll adjust it from it's position in the sub (Even if that sub is not visialbe, or if the light is doing someting else)
    20:41:57 drewp: but if you touch a light that wasnt in the sub, the current light brightness from the stage gets copied into the sub, and then you adjust frmo there
    20:42:05 drewp: i dont know any other rules; but these seem odd
    20:42:29 drewp: it may be necessary to highlight which lights are already in the sub, so you know what you're doing as soon as you click on one
    """
    def __init__(self,currentoutputlevels):
        self.sub=None
        self.currentoutputlevels = currentoutputlevels

    def setsub(self,sub):
        """sets which (one) sub object should the stage be editing.

        this is called by widgets that are set up in the Subpanels interfaces.
        """
        
        print "subedit: editing ",sub.name
        self.sub = sub

    #
    # next two methods are called by the Stage
    #
    def startlevelchange(self):
        "stage is about to send some level changes. this method is called by the Stage."
        print "subedit: start-------"
        if self.sub is None:
            print "not editing any sub!"
            return

        self.startlevels = self.sub.getlevels()

    def getcurrentlevel(self,lightname):
        print "resolve",lightname
        ch = get_dmx_channel(lightname)
        try:
            ch = get_dmx_channel(lightname)
        except ValueError:
            return None
        print "resolved ch",ch
        return self.currentoutputlevels[ch]

    def levelchange(self,lightnames,delta):
        """stage sends this message with its light names and a delta
        0..1 measured from the last startlevelchange call. this method is
        called by the Stage"""

        print "subedit: level change",lightnames,delta
        if self.sub is None:
            print "not editing any sub!"
            return

        updatelevels={}

        for l in lightnames:
            if l not in self.startlevels:
                # level was not in the sub
                cl = self.getcurrentlevel(l)
                if cl is None:
                    print "light isn't even in the patch! skipping"
                    return
                print "copying current light level",cl,"into the sub"
                self.startlevels[l] = cl 

            updatelevels[l] = min(100,max(0,self.startlevels[l]+delta))

        self.sub.reviselevels(updatelevels)
    
