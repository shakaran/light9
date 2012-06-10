import web, json, socket
from twisted.python.util import sibpath
from light9.namespaces import L9
from light9.showconfig import getSongsFromShow, songOnDisk
from rdflib import URIRef
from web.contrib.template import render_genshi
render = render_genshi([sibpath(__file__, ".")])
app = None


_songUris = {} # locationUri : song
def songLocation(graph, songUri):
    loc = URIRef("file://%s" % songOnDisk(songUri))
    _songUris[loc] = songUri
    return loc
    
def songUri(graph, locationUri):
    return _songUris[locationUri]

class root(object):
    def GET(self):
        web.header("Content-type", "application/xhtml+xml")
        # todo: use a template; embed the show name and the intro/post
        # times into the page
        return render.index(host=socket.gethostname())

class timeResource(object):
    def GET(self):
        player = app.player
        graph = app.graph

        playingLocation = player.getSong()
        if playingLocation:
            song = songUri(graph, URIRef(playingLocation))
        else:
            song = None
        web.header("content-type", "application/json")
        return json.dumps({
            "song" : song,
            "started" : player.playStartTime,
            "duration" : player.duration(),
            "playing" : player.isPlaying(),
            "t" : player.currentTime(),
            "state" : player.states(),
            })

    def POST(self):
        """
        post a json object with {pause: true} or {resume: true} if you
        want those actions. Use {t: <seconds>} to seek, optionally
        with a pause/resume command too.
        """
        params = json.loads(web.data())
        player = app.player
        if params.get('pause', False):
            player.pause()
        if params.get('resume', False):
            player.resume()
        if 't' in params:
            player.seek(params['t'])
        web.header("content-type", "text/plain")
        return "ok"

class songs(object):
    def GET(self):
        graph = app.graph

        songs = getSongsFromShow(graph, app.show)

        web.header("Content-type", "application/json")
        return json.dumps({"songs" : [
            {"uri" : s,
             "path" : graph.value(s, L9['showPath']),
             "label" : graph.label(s)} for s in songs]})

class songResource(object):
    def POST(self):
        """post a uri of song to switch to (and start playing)"""
        graph = app.graph

        app.player.setSong(songLocation(graph, URIRef(web.data())))
        web.header("content-type", "text/plain")
        return "ok"
    
class seekPlayOrPause(object):
    def POST(self):
        player = app.player

        data = json.loads(web.data())
        if player.isPlaying():
            player.pause()
        else:
            player.seek(data['t'])
            player.resume()

def makeWebApp(theApp):
    global app
    app = theApp

    urls = (r"/", "root",
            r"/time", "timeResource",
            r"/song", "songResource",
            r"/songs", "songs",
            r"/seekPlayOrPause", "seekPlayOrPause",
            )

    return web.application(urls, globals(), autoreload=False)
