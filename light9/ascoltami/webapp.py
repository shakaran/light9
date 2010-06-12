import web, jsonlib
from twisted.python.util import sibpath
from light9.namespaces import L9, MUS

player = None
graph = None
show = None

class root(object):
    def GET(self):
        web.header("Content-type", "application/xhtml+xml")
        return open(sibpath(__file__, "index.html")).read()

class timeResource(object):
    def GET(self):
        return jsonlib.write({"song" : player.playbin.get_property("uri"),
                              "started" : player.playStartTime,
                              "duration" : player.duration(),
                              "playing" : player.isPlaying(),
                              "t" : player.currentTime()})

    def POST(self):
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
        player.setSong(web.data())
        return "ok"

def makeApp(thePlayer, theGraph, theShow):
    global player, graph, show
    player, graph, show = thePlayer, theGraph, theShow

    urls = ("/", "root",
            "/time", "timeResource",
            "/song", "songResource",
            "/songs", "songs",
            "/api/position", "timeResource", # old
            )

    app = web.application(urls, globals(), autoreload=False)
    return app
