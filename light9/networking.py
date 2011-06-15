from urlparse import urlparse
from urllib import splitport
from showconfig import getGraph, showUri
from namespaces import L9

class ServiceAddress(object):
    def __init__(self, service):
        self.service = service

    def _url(self):
        graph = getGraph()
        net = graph.value(showUri(), L9['networking'])
        return graph.value(net, self.service)

    @property
    def port(self):
        _, netloc, _, _, _, _ = urlparse(self._url())
        host, port = splitport(netloc)
        return int(port)

    @property
    def host(self):
        _, netloc, _, _, _, _ = urlparse(self._url())
        host, port = splitport(netloc)
        return host

    @property
    def url(self):
        return self._url()

    def path(self, more):
        return self.url + more

dmxServer = ServiceAddress(L9['dmxServer'])
musicPlayer = ServiceAddress(L9['musicPlayer'])
keyboardComposer = ServiceAddress(L9['keyboardComposer'])

