from __future__ import division
from random import Random
import light9.Submaster as Submaster
from chase import chase as chase_logic
import showconfig
from rdflib import RDF
from light9 import Patch
from light9.namespaces import L9

def chase(t, ontime=0.5, offset=0.2, onval=1.0, 
          offval=0.0, names=None, combiner=max, random=False):
    """names is list of URIs. returns a submaster that chases through
    the inputs"""
    if random:
        r = Random(random)
        names = names[:]
        r.shuffle(names)

    chase_vals = chase_logic(t, ontime, offset, onval, offval, names, combiner)
    lev = {}
    for uri, value in chase_vals.items():
        try:
            dmx = Patch.dmx_from_uri(uri)
        except KeyError:
            print ("chase includes %r, which doesn't resolve to a dmx chan" %
                   uri)
            continue
        lev[dmx] = value

    return Submaster.Submaster(leveldict=lev, temporary=True)

def stack(t, names=None):
    """names is list of URIs. returns a submaster that stacks the the inputs"""
    frac = 1.0 / (len(names) + 1)
    threshold = frac

    lev = {}
    for uri in names:
        try:
            dmx = Patch.dmx_from_uri(uri)
        except KeyError:
            print ("stack includes %r, which doesn't resolve to a dmx chan" %
                   uri)
            continue
        lev[dmx] = 1

        threshold += frac
        if threshold > t:
            break

    return Submaster.Submaster(leveldict=lev, temporary=True)

def configExprGlobals():
    graph = showconfig.getGraph()
    ret = {}

    for chaseUri in graph.subjects(RDF.type, L9['Chase']):
        shortName = chaseUri.rsplit('/')[-1]
        chans = graph.value(chaseUri, L9['channels'])
        ret[shortName] = list(graph.items(chans))
        print "%r is a chase" % shortName

    ret['chase'] = chase
    ret['stack'] = stack
    return ret
