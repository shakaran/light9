import time, logging
from os import path, getenv
from rdflib import Graph
from rdflib import URIRef
from namespaces import MUS, L9
log = logging.getLogger('showconfig')

_config = (None, None, None) # graph, mtime, len
def getGraph():
    global _config
    configPath = path.join(root(), 'config.n3')

    # file patch.n3 mtime is not currently being checked
    
    now = time.time()
    diskMtime = path.getmtime(configPath)
    if diskMtime <= _config[1]:
        log.debug("config.n3 hasn't changed")
        graph = _config[0]
        # i'm scared of some program modifying the graph, and then i
        # return that from a new getGraph call. Maybe I should be
        # copying it right here, or doing something clever with
        # contexts
        assert len(graph) == _config[2]
        return _config[0]

    graph = Graph()
    log.info("reading %s", configPath)
    graph.parse(configPath, format='n3')
    patchPath = path.join(root(), "patch.n3")
    log.info("reading %s", patchPath)
    graph.parse(patchPath, format="n3")
    
    _config = (graph, diskMtime, len(graph))
    return graph

def root():
    r = getenv("LIGHT9_SHOW")
    if r is None:
        raise OSError(
            "LIGHT9_SHOW env variable has not been set to the show root")
    return r

def showUri():
    """Return the show URI associated with $LIGHT9_SHOW."""
    return URIRef(file(path.join(root(), 'URI')).read().strip())

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

def songOnDisk(song):
    """given a song URI, where's the on-disk file that mpd would read?"""
    graph = getGraph()
    root = graph.value(showUri(), L9['musicRoot'])
    if not root:
        raise ValueError("%s has no :musicRoot" % showUri())
    
    name = graph.value(song, L9['songFilename'])
    if not name:
        raise ValueError("Song %r has no :songFilename" % song)

    return path.join(root, name)

def songFilenameFromURI(uri):
    """
    'http://light9.bigasterisk.com/show/dance2007/song8' -> 'song8'

    everything that uses this should be deprecated for real URIs
    everywhere"""
    assert isinstance(uri, URIRef)
    return uri.split('/')[-1]

def getSongsFromShow(graph, show):
    playList = graph.value(show, L9['playList'])
    if not playList:
        raise ValueError("%r has no l9:playList" % show)
    songs = list(graph.items(playList))

    return songs

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
