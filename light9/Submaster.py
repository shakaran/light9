from __future__ import division
import os
from rdflib.Graph import Graph
from rdflib import RDFS, Literal, BNode
from light9.namespaces import L9, XSD
from light9.TLUtility import dict_scale, dict_max
from light9 import Patch, showconfig
try:
    import dispatch.dispatcher as dispatcher
except ImportError:
    from louie import dispatcher

class Submaster:
    "Contain a dictionary of levels, but you didn't need to know that"
    def __init__(self,
                 name=None,
                 graph=None, sub=None,
                 leveldict=None, temporary=False):
        """sub is the URI for this submaster, graph is a graph where
        we can learn about the sub. If graph is not provided, we look
        in a file named name.

        name is the filename where we can load a graph about this URI
        (see showconfig.subFile)

        passing name alone makes a new empty sub

        temporary means the sub won't get saved or loaded


        pass:
          name, temporary=True  -  no rdf involved
          sub, filename         -  read sub URI from graph at filename
          
          name - new sub
          sub - n
          name, sub - new 
        
        """
        if name is sub is leveldict is None:
            raise TypeError("more args are needed")
        if sub is not None:
            name = graph.label(sub)
        if graph is not None:
            # old code was passing leveldict as second positional arg
            assert isinstance(graph, Graph)
        self.name = name
        self.uri = sub
        self.temporary = temporary
        if leveldict:
            self.levels = leveldict
        else:
            self.levels = {}
            self.reload(quiet=True, graph=graph)
        if not self.temporary:
            dispatcher.connect(self.reload, 'reload all subs')
            
    def reload(self, quiet=False, graph=None):
        if self.temporary:
            return
        try:
            oldlevels = self.levels.copy()
            self.levels.clear()
            patchGraph = showconfig.getGraph()
            if graph is None:
                graph = Graph()
                graph.parse(showconfig.subFile(self.name), format="nt")
            self.uri = L9['sub/%s' % self.name]
            for lev in graph.objects(self.uri, L9['lightLevel']):
                chan = graph.value(lev, L9['channel'])
                val = graph.value(lev, L9['level'])
                name = patchGraph.label(chan)
                if not name:
                    print "sub %r has channel %r with no name- leaving out that channel" % (self.name, chan)
                    continue
                self.levels[name] = float(val)

            if (not quiet) and (oldlevels != self.levels):
                print "sub %s changed" % self.name
        except IOError, e:
            print "Can't read file for sub: %r (%s)" % (self.name, e)
    def save(self):
        if self.temporary:
            print "not saving temporary sub named",self.name
            return

        graph = Graph()
        subUri = L9['sub/%s' % self.name]
        graph.add((subUri, RDFS.label, Literal(self.name)))
        for chan in self.levels.keys():
            try:
                chanUri = Patch.get_channel_uri(chan)
            except KeyError:
                print "saving dmx channels with no :Channel node is not supported yet. Give channel %s a URI for it to be saved. Omitting this channel from the sub." % chan
                continue
            lev = BNode()
            graph.add((subUri, L9['lightLevel'], lev))
            graph.add((lev, L9['channel'], chanUri))
            graph.add((lev, L9['level'],
                       Literal(self.levels[chan], datatype=XSD['decimal'])))

        graph.serialize(showconfig.subFile(self.name), format="nt")

    def set_level(self, channelname, level, save=True):
        self.levels[Patch.resolve_name(channelname)] = level
        if save:
            self.save()
    def set_all_levels(self, leveldict):
        self.levels.clear()
        for k, v in leveldict.items():
            self.set_level(k, v, save=0)
        self.save()
    def get_levels(self):
        return self.levels
    def no_nonzero(self):
        return (not self.levels.values()) or not (max(self.levels.values()) > 0)
    def __mul__(self, scalar):
        return Submaster("%s*%s" % (self.name, scalar), 
                         leveldict=dict_scale(self.levels, scalar),
                         temporary=True)
    __rmul__ = __mul__
    def max(self, *othersubs):
        return sub_maxes(self, *othersubs)
    def __repr__(self):
        items = self.levels.items()
        items.sort()
        levels = ' '.join(["%s:%.2f" % item for item in items])
        return "<'%s': [%s]>" % (self.name, levels)
    def get_dmx_list(self):
        leveldict = self.get_levels() # gets levels of sub contents

        levels = []
        for k, v in leveldict.items():
            if v == 0:
                continue
            try:
                dmxchan = Patch.get_dmx_channel(k) - 1
            except ValueError:
                print "error trying to compute dmx levels for submaster %s" % self.name
                raise
            if dmxchan >= len(levels):
                levels.extend([0] * (dmxchan - len(levels) + 1))
            levels[dmxchan] = max(v, levels[dmxchan])

        return levels
    def normalize_patch_names(self):
        """Use only the primary patch names."""
        # possibly busted -- don't use unless you know what you're doing
        self.set_all_levels(self.levels.copy())
    def get_normalized_copy(self):
        """Get a copy of this sumbaster that only uses the primary patch 
        names.  The levels will be the same."""
        newsub = Submaster("%s (normalized)" % self.name, temporary=1)
        newsub.set_all_levels(self.levels)
        return newsub
    def crossfade(self, othersub, amount):
        """Returns a new sub that is a crossfade between this sub and
        another submaster.  
        
        NOTE: You should only crossfade between normalized submasters."""
        otherlevels = othersub.get_levels()
        keys_set = {}
        for k in self.levels.keys() + otherlevels.keys():
            keys_set[k] = 1
        all_keys = keys_set.keys()

        xfaded_sub = Submaster("xfade", temporary=1)
        for k in all_keys:
            xfaded_sub.set_level(k, 
                                 linear_fade(self.levels.get(k, 0),
                                             otherlevels.get(k, 0),
                                             amount))

        return xfaded_sub
    def __cmp__(self, other):
        raise NotImplementedError
        return cmp(repr(self), repr(other))
    def __hash__(self):
        raise NotImplementedError
        return hash(repr(self))
                                            
def linear_fade(start, end, amount):
    """Fades between two floats by an amount.  amount is a float between
    0 and 1.  If amount is 0, it will return the start value.  If it is 1,
    the end value will be returned."""
    level = start + (amount * (end - start))
    return level

def sub_maxes(*subs):
    nonzero_subs = [s for s in subs if not s.no_nonzero()]
    name = "max(%s)" % ", ".join([repr(s) for s in nonzero_subs])
    return Submaster(name,
                     leveldict=dict_max(*[sub.levels for sub in nonzero_subs]),
                     temporary=1)

def combine_subdict(subdict, name=None, permanent=False):
    """A subdict is { Submaster objects : levels }.  We combine all
    submasters first by multiplying the submasters by their corresponding
    levels and then max()ing them together.  Returns a new Submaster
    object.  You can give it a better name than the computed one that it
    will get or make it permanent if you'd like it to be saved to disk.
    Serves 8."""
    scaledsubs = [sub * level for sub, level in subdict.items()]
    maxes = sub_maxes(*scaledsubs)
    if name:
        maxes.name = name
    if permanent:
        maxes.temporary = False

    return maxes

class Submasters:
    "Collection o' Submaster objects"
    def __init__(self):
        self.submasters = {}

        files = os.listdir(showconfig.subsDir())

        for filename in files:
            # we don't want these files
            if filename.startswith('.') or filename.endswith('~') or \
               filename.startswith('CVS'):
                continue
            self.submasters[filename] = Submaster(filename)
        print "loaded subs", self.submasters
    def get_all_subs(self):
        "All Submaster objects"
        l = self.submasters.items()
        l.sort()
        l = [x[1] for x in l]
        songs = []
        notsongs = []
        for s in l:
            if s.name.startswith('song'):
                songs.append(s)
            else:
                notsongs.append(s)
        combined = notsongs + songs

        return combined
    def get_all_sub_names(self):
        return [s.name for s in self.get_all_subs()]
    def get_sub_by_name(self, name):
        "Makes a new sub if there isn't one."
        if name in self.submasters:
            return self.submasters[name]
        return Submaster(name)
    __getitem__ = get_sub_by_name

def fullsub(*chans):
    """Make a submaster with chans at full."""
    return Submaster('%r' % chans,
        leveldict=dict([(c, 1.0) for c in chans]), temporary=True)

# a global instance of Submasters, created on demand
_submasters = None

def get_global_submasters():
    """Get (and make on demand) the global instance of Submasters"""
    global _submasters
    if _submasters is None:
        _submasters = Submasters()
    return _submasters

def get_sub_by_name(name, submasters=None):
    """name is a channel or sub nama, submasters is a Submasters object.
    If you leave submasters empty, it will use the global instance of
    Submasters."""
    if not submasters:
        submasters = get_global_submasters()

    if name in submasters.get_all_sub_names():
        return submasters.get_sub_by_name(name)

    try:
        val = int(name)
        s = Submaster("#%d" % val, leveldict={val : 1.0}, temporary=True)
        return s
    except ValueError:
        pass

    try:
        subnum = Patch.get_dmx_channel(name)
        s = Submaster("'%s'" % name, leveldict={subnum : 1.0}, temporary=True)
        return s
    except ValueError:
        pass

    # make an error sub
    return Submaster('%s' % name)

if __name__ == "__main__":
    Patch.reload_data()
    s = Submasters()
    print s.get_all_subs()
    if 0: # turn this on to normalize all subs
        for sub in s.get_all_subs():
            print "before", sub
            sub.normalize_patch_names()
            sub.save()
            print "after", sub
