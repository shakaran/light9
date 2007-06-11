import time
from os import path, getenv
from rdflib.Graph import Graph
from rdflib import URIRef
from namespaces import MUS, L9

_config = (None, None, None) # graph, mtime, len
def getGraph():
    global _config
    configPath = path.join(root(), 'config.n3')
    
    now = time.time()
    diskMtime = path.getmtime(configPath)
    if diskMtime <= _config[1]:
        graph = _config[0]
        # i'm scared of some program modifying the graph, and then i
        # return that from a new getGraph call. Maybe I should be
        # copying it right here, or doing something clever with
        # contexts
        assert len(graph) == _config[2]
        return _config[0]

    graph = Graph()
    graph.parse(configPath, format='n3')
    _config = (graph, diskMtime, len(graph))
    return graph

def root():
    r = getenv("LIGHT9_SHOW")
    if r is None:
        raise OSError(
            "LIGHT9_SHOW env variable has not been set to the show root")
    return r

def songInMpd(song):

    """mpd only works off its own musicroot, which for me is
    /my/music. song is a file in musicDir; this function returns a
    version starting with the mpd path, but minus the mpd root itself.
    the mpc ~/.mpdconf

    changed root to /home/drewp/projects/light9/show/dance2005 for now
    """

    assert isinstance(song, URIRef), "songInMpd now takes URIRefs"

    mpdHome = None
    for line in open(path.expanduser("~/.mpdconf")):
        if line.startswith("music_directory"):
            mpdHome = line.split()[1].strip('"')
    if mpdHome is None:
        raise ValueError("can't find music_directory in your ~/.mpdconf")
    mpdHome = mpdHome.rstrip(path.sep) + path.sep

    songFullPath = songOnDisk(song)
    if not songFullPath.startswith(mpdHome):
        raise ValueError("the song path %r is not under your MPD music_directory (%r)" % (songFullPath, mpdHome))
        
    mpdRelativePath = songFullPath[len(mpdHome):]
    if path.join(mpdHome, mpdRelativePath) != songFullPath:
        raise ValueError("%r + %r doesn't make the songpath %r" % (mpdHome, mpdRelativePath, songFullPath))
    return mpdRelativePath.encode('ascii')

def songOnDisk(song):
    graph = getGraph()
    songFullPath = path.join(root(), graph.value(song, L9['showPath']))
    return songFullPath

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

def prePostSong():
    graph = getGraph()
    return [graph.value(MUS['preSong'], L9['showPath']),
            graph.value(MUS['postSong'], L9['showPath'])]

