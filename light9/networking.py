import os
from ConfigParser import SafeConfigParser
# my intent was to pull these from a file in the LIGHT9_SHOW/ directory


def dmxServerUrl():
    #host = os.getenv('DMXHOST', 'localhost')
    #url = "http://%s:8030" % host
    return "http://plus:%s" % dmxServerPort()

def dmxServerPort():
    return 8030
    
def musicUrl():
    return "http://dash:%s/" % musicPort()

def musicPort():
    return 8040

def mpdServer():
    """servername, port"""
    return os.getenv('LIGHT9_MPD_SERVER', 'score'),6600

def kcPort():
    return 8050

def kcServer():
    return 'plus'

def keyboardComposerUrl():
    return "http://%s:%s" % (kcServer(), kcPort())
