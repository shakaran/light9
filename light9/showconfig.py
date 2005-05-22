from os import path,getenv
import ConfigParser

def root():
    r = getenv("LIGHT9_SHOW")
    if r is None:
        raise OSError(
            "LIGHT9_SHOW env variable has not been set to the show root")
    return r

def musicDir():
    return path.join(root(),"music")

def songInMpd(song):

    """mpd only works off its own musicroot, which for me is
    /my/music. song is a file in musicDir; this function returns a
    version starting with the mpd path, but minus the mpd root itself.
    the mpc ~/.mpdconf """
    
    if 'dance2005' in root():
        return "projects/dance2005/%s" % song
    raise NotImplementedError

def curvesDir():
    return path.join(root(),"curves")

def songFilename(song):
    return path.join(musicDir(),"%s.wav" % song)

def subtermsForSong(song):
    return path.join(root(),"subterms",song)

def subFile(subname):
    return path.join(root(),"subs",subname)

def subsDir():
    return path.join(root(),'subs')

def patchData():
    return path.join(root(),"patchdata.py")

def prePostSong():
    p = ConfigParser.SafeConfigParser()
    p.read([path.join(root(),'config')])
    return p.get('music','preSong'), p.get('music','postSong')
