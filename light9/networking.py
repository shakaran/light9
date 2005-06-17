from ConfigParser import SafeConfigParser
# my intent was to pull these from a file in the LIGHT9_SHOW/ directory

def dmxServerUrl():
    #host = os.getenv('DMXHOST', 'localhost')
    #url = "http://%s:8030" % host
    return "http://localhost:%s" % dmxServerPort()

def dmxServerPort():
    return 8030
    
def musicUrl():
    return "http://localhost:%s" % musicPort()

def musicPort():
    return 8040

def mpdServer():
    """servername, port"""
    return 'dash',6600

def kcPort():
    return 8050

def kcServer():
    return 'dash'
