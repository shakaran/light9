from os import path,getenv

def root():
    r = getenv("LIGHT9_SHOW")
    if r is None:
        raise OSError("LIGHT9_SHOW env variable has not been set to the show root")
    return r

def musicDir():
    return path.join(root(),"music")

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
