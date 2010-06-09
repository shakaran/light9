import time
from os import path, getenv
from rdflib.Graph import Graph
from rdflib import URIRef
from namespaces import MUS, L9

_config = (None, None, None) # graph, mtime, len
def getGraph():
    global _config
    configPath = path.join(root(), 'config.n3')

    # file patch.n3 mtime is not currently being checked
    
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
    graph.parse(path.join(root(), "patch.n3"), format="n3")
    
    _config = (graph, diskMtime, len(graph))
    return graph

def root():
    r = getenv("LIGHT9_SHOW")
    if r is None:
        raise OSError(
            "LIGHT9_SHOW env variable has not been set to the show root")
    return r

def findMpdHome():
    """top of the music directory for the mpd on this system,
    including trailing slash"""
    
    mpdHome = None
    for mpdConfFilename in ["/my/dl/modified/mpd/src/mpdconf-testing",
                            "~/.mpdconf", "/etc/mpd.conf"]:
        try:
            mpdConfFile = open(path.expanduser(mpdConfFilename))
        except IOError:
            continue
        for line in mpdConfFile:
            if line.startswith("music_directory"):
                mpdHome = line.split()[1].strip('"')
                return mpdHome.rstrip(path.sep) + path.sep  

    raise ValueError("can't find music_directory in any mpd config file")


def songInMpd(song):
    """
    get the mpd path (with correct encoding) from the song URI

    mpd only works off its own musicroot, which for me is
    /my/music. song is a file in musicDir; this function returns a
    version starting with the mpd path, but minus the mpd root itself.
    the mpc ~/.mpdconf

    changed root to /home/drewp/projects/light9/show/dance2005 for now
    """

    assert isinstance(song, URIRef), "songInMpd now takes URIRefs"

    mpdPath = getGraph().value(song, L9['showPath'])
    if mpdPath is None:
        raise ValueError("no mpd path found for subject=%r" % song)
    return mpdPath.encode('ascii')

def songOnDisk(song):
    """given a song URI, where's the on-disk file that mpd would read?"""
    graph = getGraph()
    showPath = graph.value(song, L9['showPath'])
    if not showPath:
        raise ValueError("no mpd path found for subject=%r" % song)
    songFullPath = path.join(findMpdHome(), showPath)
    return songFullPath

def songFilenameFromURI(uri):
    """
    'http://light9.bigasterisk.com/show/dance2007/song8' -> 'song8'

    everything that uses this should be deprecated for real URIs
    everywhere"""
    assert isinstance(uri, URIRef)
    return uri.split('/')[-1]

def curvesDir():
    return path.join(root(),"curves")

def songFilename(song):
    return path.join(root(), "music", "%s.wav" % song)

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

