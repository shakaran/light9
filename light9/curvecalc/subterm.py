import math, os, random, logging
from rdflib import Graph, URIRef, RDF, RDFS, Literal
from louie import dispatcher
import light9.Effects
from light9 import Submaster, showconfig, Patch, prof
from light9.namespaces import L9
log = logging.getLogger()

class Expr(object):
    """singleton, provides functions for use in subterm expressions,
    e.g. chases"""
    def __init__(self):
        self.effectGlobals = light9.Effects.configExprGlobals()
    
    def exprGlobals(self, startDict, t):
        """globals dict for use by expressions"""

        glo = startDict.copy()
        
        # add in functions from Effects
        glo.update(self.effectGlobals)

        glo['nsin'] = lambda x: (math.sin(x * (2 * math.pi)) + 1) / 2
        glo['ncos'] = lambda x: (math.cos(x * (2 * math.pi)) + 1) / 2
        glo['within'] = lambda a, b: a < t < b
        glo['bef'] = lambda x: t < x


        def smoove(x):
            return -2 * (x ** 3) + 3 * (x ** 2)
        glo['smoove'] = smoove

        def aft(t, x, smooth=0):
            left = x - smooth / 2
            right = x + smooth / 2
            if left < t < right:
                return smoove((t - left) / (right - left))
            return t > x
        glo['aft'] = lambda x, smooth=0: aft(t, x, smooth)

        def chan(name):
            return Submaster.Submaster(
                leveldict={Patch.get_dmx_channel(name) : 1.0},
                temporary=True)
        glo['chan'] = chan

        def smooth_random(speed=1):
            """1 = new stuff each second, <1 is slower, fade-ier"""
            x = (t * speed) % len(self._smooth_random_items)
            x1 = int(x)
            x2 = (int(x) + 1) % len(self._smooth_random_items)
            y1 = self._smooth_random_items[x1]
            y2 = self._smooth_random_items[x2]
            return y1 + (y2 - y1) * ((x - x1))

        def notch_random(speed=1):
            """1 = new stuff each second, <1 is slower, notch-ier"""
            x = (t * speed) % len(self._smooth_random_items)
            x1 = int(x)
            y1 = self._smooth_random_items[x1]
            return y1
            
        glo['noise'] = smooth_random
        glo['notch'] = notch_random

        

        return glo

exprglo = Expr()
        
class Subexpr:
    curveset = None
    def __init__(self,curveset,expr=""):
        self.curveset = curveset
        self.lasteval = None
        self.expr=expr
        self._smooth_random_items = [random.random() for x in range(100)]
    def eval(self,t):
        if self.expr=="":
            dispatcher.send("expr_error",sender=self,exc="no expr, using 0")
            return 0
        glo = self.curveset.globalsdict()
        glo['t'] = t

        glo = exprglo.exprGlobals(glo, t)
        
        try:
            self.lasteval = eval(self.expr,glo)
        except Exception,e:
            dispatcher.send("expr_error",sender=self,exc=e)
        else:
            dispatcher.send("expr_error",sender=self,exc="ok")
        return self.lasteval

    def expr():
        doc = "python expression for level as a function of t, using curves"
        def fget(self):
            return self._expr
        def fset(self, value):
            self._expr = value
            dispatcher("expr_changed",sender=self)
        return locals()
    expr = property(**expr())

class Subterm:
    """one Submaster and its Subexpr"""
    def __init__(self, submaster, subexpr):
        self.submaster, self.subexpr = submaster, subexpr

    def scaled(self, t):
        subexpr_eval = self.subexpr.eval(t)
        # we prevent any exceptions from escaping, since they cause us to
        # stop sending levels
        try:
            if isinstance(subexpr_eval, Submaster.Submaster):
                # if the expression returns a submaster, just return it
                return subexpr_eval
            else:
                # otherwise, return our submaster multiplied by the value 
                # returned
                return self.submaster * subexpr_eval
        except Exception, e:
            dispatcher.send("expr_error", sender=self.subexpr, exc=str(e))
            return Submaster.Submaster('Error: %s' % str(e), temporary=True)

    def __repr__(self):
        return "<Subterm %s %s>" % (self.submaster, self.subexpr)


def graphPathForSubterms(song):
    return showconfig.subtermsForSong(showconfig.songFilenameFromURI(song)) + ".n3"

@prof.logTime
def read_all_subs(graph):
    """read all sub files into this graph so when add_one_subterm tries
    to add, the sub will be available"""
    subsDir = showconfig.subsDir()
    for filename in os.listdir(subsDir):
        # parsing nt is faster, but it should try n3 format if the parsing fails
        graph.parse(os.path.join(subsDir, filename), format="n3")

def createSubtermGraph(song, subterms):
    """rdf graph describing the subterms, readable by add_subterms_for_song"""
    graph = Graph()
    for subterm in subterms:
        assert subterm.submaster.name, "submaster has no name"
        uri = URIRef(song + "/subterm/" + subterm.submaster.name)
        graph.add((song, L9['subterm'], uri))
        graph.add((uri, RDF.type, L9['Subterm']))
        graph.add((uri, RDFS.label, Literal(subterm.submaster.name)))
        graph.add((uri, L9['sub'], L9['sub/%s' % subterm.submaster.name]))
        graph.add((uri, L9['expression'], Literal(subterm.subexpr.expr)))
    return graph

def savekey(song, subterms, curveset):
    print "saving", song
    g = createSubtermGraph(song, subterms)
    g.serialize(graphPathForSubterms(song), format="nt")

    curveset.save(basename=os.path.join(showconfig.curvesDir(),
                                        showconfig.songFilenameFromURI(song)))
    print "saved"
