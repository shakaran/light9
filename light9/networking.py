import os
from ConfigParser import SafeConfigParser
# my intent was to pull these from a file in the LIGHT9_SHOW/ directory


def dmxServerUrl():
    #host = os.getenv('DMXHOST', 'localhost')
    #url = "http://%s:8030" % host
    return "http://spot:%s" % dmxServerPort()

def dmxServerPort():
    return 8030
    
def musicUrl():
    return "http://score:%s" % musicPort()

def musicPort():
    return 8040

def mpdServer():
    """servername, port"""
    return os.getenv('LIGHT9_MPD_SERVER', 'dash'),6600

def kcPort():
    return 8050

def kcServer():
    return 'dash'
