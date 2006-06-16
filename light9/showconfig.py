from os import path,getenv
from rdflib.Graph import Graph
from rdflib import URIRef
from namespaces import MUS, L9

def getGraph():
    graph = Graph()
    graph.parse(path.join(root(), 'config.n3'), format='n3')
    return graph

def root():
    r = getenv("LIGHT9_SHOW")
    if r is None:
        raise OSError(
            "LIGHT9_SHOW env variable has not been set to the show root")
    return r

def musicDir():
    return path.join(root(),"music_local")

def songInMpd(song):

    """mpd only works off its own musicroot, which for me is
    /my/music. song is a file in musicDir; this function returns a
    version starting with the mpd path, but minus the mpd root itself.
    the mpc ~/.mpdconf

    changed root to /home/drewp/projects/light9/show/dance2005 for now
    """
    
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
    graph = getGraph()
    return [graph.value(MUS['preSong'], L9['showPath']),
            graph.value(MUS['postSong'], L9['showPath'])]

