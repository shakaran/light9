"""

widget to show all dmx channel levels and allow editing. levels might
not actually match what dmxserver is outputting.

"""
from __future__ import nested_scopes,division
import Tkinter as tk
import time
from light9 import Patch
from light9.uihelpers import make_frame, colorlabel, eventtoparent
from dispatch import dispatcher

# this font makes each label take 16ms to create, so startup is slow.
# with default font, each labl takes about .5ms to create.
stdfont = ('Arial', 12)
import tkFont
# see replacement stdfont below


def gradient(lev, low=(80,80,180), high=(255,55,50)):
     out = [int(l+lev*(h-l)) for h,l in zip(high,low)]
     col="#%02X%02X%02X" % tuple(out)
     return col

class Onelevel(tk.Frame):
    """a name/level pair"""
    def __init__(self, parent, channelnum):
        """channelnum is 1..68, like the real dmx"""
        tk.Frame.__init__(self,parent)

        self.channelnum=channelnum
        self.currentlevel=0 # the level we're displaying, 0..1
        
        # 3 widgets, left-to-right:

        # channel number -- will turn yellow when being altered
        self.num_lab = tk.Label(self, text=str(channelnum),
                                width=3, bg='grey40', 
                                fg='white', font=stdfont,
                                padx=0, pady=0, bd=0, height=1)
        self.num_lab.pack(side='left')

        # text description of channel
        self.desc_lab=tk.Label(self, text=Patch.get_channel_name(channelnum),
                               width=14, font=stdfont,
                               anchor='w',
                               padx=0, pady=0, bd=0, 
                 height=1, bg='black', fg='white')
        self.desc_lab.pack(side='left')

        # current level of channel, shows intensity with color
        self.level_lab = tk.Label(self, width=3, bg='lightBlue',
                                  font=stdfont,
                                  anchor='e', 
                                  padx=1, pady=0, bd=0, height=1)
        self.level_lab.pack(side='left')

        self.setlevel(0)
        self.setupmousebindings()
        
    def setupmousebindings(self):
        def b1down(ev):
            self.desc_lab.config(bg='cyan')
            self._start_y=ev.y
            self._start_lev=self.currentlevel
        def b1motion(ev):
            delta=self._start_y-ev.y
            self.changelevel(self._start_lev+delta*.005)
        def b1up(ev):
            self.desc_lab.config(bg='black')
        def b3up(ev):
            self.changelevel(0.0)
        def b3down(ev):
            self.changelevel(1.0)

        # make the buttons work in the child windows
        for w in self.winfo_children():
            for e,func in (('<ButtonPress-1>',b1down),
                           ('<B1-Motion>',b1motion),
                           ('<ButtonRelease-1>',b1up),
                           ('<ButtonRelease-3>', b3up),
                           ('<ButtonPress-3>', b3down)):
                w.bind(e,func)
#                w.bind(e,lambda ev,e=e: eventtoparent(ev,e))
        
    def colorlabel(self):
        """color the level label based on its own text (which is 0..100)"""
        txt=self.level_lab['text'] or "0"
        lev=float(txt)/100
        self.level_lab.config(bg=gradient(lev))

    def setlevel(self,newlev):
        """the main program is telling us to change our
        display. newlev is 0..1"""
        self.currentlevel=newlev
        newlev="%d"%(newlev*100)
        olddisplay=self.level_lab.cget('text')
        if newlev!=olddisplay:
            self.level_lab.config(text=newlev)
            self.colorlabel()

    def getlevel(self):
        """returns currently displayed level, 0..1"""
        return self.currentlevel

    def changelevel(self,newlev):

        """the user is adjusting the level on this widget.  the main
        program needs to hear about it. then the main program will
        call setlevel()"""

        dispatcher.send("levelchanged",channel=self.channelnum,newlevel=newlev)
    
class Levelbox(tk.Frame):
    def __init__(self, parent, num_channels=68):
        tk.Frame.__init__(self,parent)
        global stdfont
        stdfont = tkFont.Font(size=9)
        self.levels = [] # Onelevel objects

        frames = (make_frame(self), make_frame(self))

        for channel in range(1, num_channels+1):

            # frame for this channel
            f = Onelevel(frames[channel > (num_channels/2)],channel)

            self.levels.append(f)
            f.pack(side='top')
        #dispatcher.connect(setalevel,"setlevel")

    def setlevels(self,newlevels):
        """sets levels to the new list of dmx levels (0..1). list can
        be any length"""
        for l,newlev in zip(self.levels,newlevels):
            l.setlevel(newlev)
