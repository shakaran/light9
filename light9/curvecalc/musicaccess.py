import restkit
import json
from louie import dispatcher
from rdflib import URIRef
from light9 import networking
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.internet.protocol import Protocol
from twisted.internet.defer import Deferred     
from zope.interface import implements
from twisted.internet.defer import succeed
from twisted.web.iweb import IBodyProducer

class GatherJson(Protocol):
    """calls back the 'finished' deferred with the parsed json data we
    received"""
    def __init__(self, finished):
        self.finished = finished
        self.buf = ""

    def dataReceived(self, bytes):
        self.buf += bytes

    def connectionLost(self, reason):
        self.finished.callback(json.loads(self.buf))

class StringProducer(object):
    # http://twistedmatrix.com/documents/current/web/howto/client.html
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass

class Music:
    def __init__(self):
        self.recenttime=0
        self.player = Agent(reactor)
        dispatcher.connect(self.seekplay_or_pause,"music seek")
        self.timePath = networking.musicPlayer.path("time")
        
    def current_time(self):
        """return deferred which gets called with the current
        time. This gets called really often"""
        d = self.player.request("GET", self.timePath)
        d.addCallback(self._timeReturned)
        return d

    def _timeReturned(self, response):
        done = Deferred()
        done.addCallback(self._bodyReceived)
        response.deliverBody(GatherJson(done))
        return done

    def _bodyReceived(self, data):
        dispatcher.send("input time",val=data['t'])
        return data['t'] # pass along to the real receiver
    
    def seekplay_or_pause(self,t):
        d = self.player.request("POST",
                                networking.musicPlayer.path("seekPlayOrPause"),
                                bodyProducer=StringProducer(json.dumps({"t" : t})))



def currentlyPlayingSong():
    """ask the music player what song it's on"""
    player = restkit.Resource(networking.musicPlayer.url)
    t = json.loads(player.get("time").body_string())
    if t['song'] is None:
        raise ValueError("music player is not playing any song")
    return URIRef(t['song'])
