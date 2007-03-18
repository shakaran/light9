# allows bin/* to work without installation

# this should be turned off when the programs are installed

import sys,os
sys.path.insert(0,os.path.join(os.path.dirname(sys.argv[0]),".."))

import cgitb
from twisted.python.failure import Failure

import Tkinter
def rce(self, exc, val, tb):
    sys.stderr.write("Exception in Tkinter callback\n")
    if True:
        sys.excepthook(exc, val, tb)
    else:
        Failure(val, exc, tb).printDetailedTraceback()
Tkinter.Tk.report_callback_exception = rce

cgitb.enable(format='txt')
