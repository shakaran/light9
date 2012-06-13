#!/usr/bin/env python

from lib.ipython_view import IPythonView

import gi
from gi.repository import Gtk
from gi.repository import Pango

def togglePyConsole(self, item, user_ns):
    """
    toggles a toplevel window with an ipython console inside.

    self is an object we can stick the pythonWindow attribute on

    item is a checkedmenuitem

    user_ns is a dict you want to appear as locals in the console
    """
    if item.get_active():
        if not hasattr(self, 'python_window'):
            self.python_window = Gtk.Window()
            S = Gtk.ScrolledWindow()
            S.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
            V = IPythonView(user_ns=user_ns)
            V.modify_font(pango.FontDescription('luxi mono 8'))
            V.set_wrap_mode(Gtk.WRAP_CHAR)
            S.add(V)
            self.python_window.add(S)
            self.python_window.show_all()
            self.python_window.set_size_request(750, 550)
            self.python_window.set_resizable(True)
            
            def onDestroy(*args):
                item.set_active(False)
                del self.python_window
                
            self.python_window.connect('destroy', onDestroy)
    else:
        if hasattr(self, 'python_window'):
            self.python_window.destroy()

