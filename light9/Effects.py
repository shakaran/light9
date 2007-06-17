from __future__ import division
import random
import light9.Submaster as Submaster
from chase import chase as chase_logic
import showconfig
from rdflib import RDF
from light9 import Patch
from light9.namespaces import L9

def chase(t, ontime=0.5, offset=0.2, onval=1.0, 
          offval=0.0, names=None, combiner=max):
    """names is list of URIs. returns a submaster that chases through
    the inputs"""
    sub_vals = {}
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

    ret = Submaster.Submaster(leveldict=lev, temporary=True)
    return ret

def configExprGlobals():
    graph = showconfig.getGraph()
    ret = {}

    for chaseUri in graph.subjects(RDF.type, L9['Chase']):
        shortName = chaseUri.rsplit('/')[-1]
        chans = graph.value(chaseUri, L9['channels'])
        ret[shortName] = list(graph.items(chans))

    ret['chase'] = chase
    return ret
