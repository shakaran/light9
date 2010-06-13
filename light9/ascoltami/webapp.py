import web, jsonlib
from twisted.python.util import sibpath
from light9.namespaces import L9
from rdflib import URIRef
player = None
graph = None
show = None


def songLocation(graph, songUri):
    loc = graph.value(songUri, L9['showPath'])
    if loc is None:
        raise ValueError("no showPath for %r" % songUri)
    return loc
    
def songUri(graph, locationUri):
    try:
        return graph.subjects(L9['showPath'], locationUri).next()
    except StopIteration:
        raise ValueError("no song has :showPath of %r" % locationUri)

class root(object):
    def GET(self):
        web.header("Content-type", "application/xhtml+xml")
        # todo: use a template; embed the show name and the intro/post
        # times into the page
        return open(sibpath(__file__, "index.html")).read()

class timeResource(object):
    def GET(self):
        playingLocation = player.playbin.get_property("uri")
        if playingLocation:
            song = songUri(graph, URIRef(playingLocation))
        else:
            song = None
        return jsonlib.write({
            "song" : song,
            "started" : player.playStartTime,
            "duration" : player.duration(),
            "playing" : player.isPlaying(),
            "t" : player.currentTime()})

    def POST(self):
        """
        post a json object with {pause: true} or {resume: true} if you
        want those actions. Use {t: <seconds>} to seek, optionally
        with a pause/resume command too.
        """
        params = jsonlib.read(web.data(), use_float=True)
        if params.get('pause', False):
            player.pause()
        if params.get('resume', False):
            player.resume()
        if 't' in params:
            player.seek(params['t'])
        return "ok"

class songs(object):
    def GET(self):
        playList = graph.value(show, L9['playList'])
        if not playList:
            raise ValueError("%r has no l9:playList" % show)
        songs = list(graph.items(playList))

        
        web.header("Content-type", "application/json")
        return jsonlib.write({"songs" : [
            {"uri" : s,
             "path" : graph.value(s, L9['showPath']),
             "label" : graph.label(s)} for s in songs]})

class songResource(object):
    def POST(self):
        """post a uri of song to switch to (and start playing)"""
        player.setSong(songLocation(graph, URIRef(web.data())))
        return "ok"
    
class seekPlayOrPause(object):
    def POST(self):
        data = jsonlib.read(web.data(), use_float=True)
        if player.isPlaying():
            player.pause()
        else:
            player.seek(data['t'])
            player.resume()

def makeApp(thePlayer, theGraph, theShow):
    global player, graph, show
    player, graph, show = thePlayer, theGraph, theShow

    urls = ("/", "root",
            "/time", "timeResource",
            "/song", "songResource",
            "/songs", "songs",
            "/seekPlayOrPause", "seekPlayOrPause",
            )

    app = web.application(urls, globals(), autoreload=False)
    return app
