from __future__ import division
from light9.TLUtility import dict_scale, dict_max
from light9 import Patch

class Submaster:
    "Contain a dictionary of levels, but you didn't need to know that"
    def __init__(self, name, leveldict=None, temporary=0):
        self.name = name
        self.temporary = temporary
        if leveldict:
            self.levels = leveldict
        else:
            self.levels = {}
            self.reload()
    def reload(self):
        if self.temporary:
            return
        try:
            self.levels.clear()
            subfile = file("subs/%s" % self.name)
            for line in subfile.readlines():
                if not line.strip(): # if line is only whitespace
                    continue # "did i say newspace?"

                try:
                    name, val = line.split(':')
                    name = name.strip()
                    self.levels[name] = float(val)
                except ValueError:
                    print "(%s) Error with this line: %s" % (self.name, 
                        line[:-1])
        except IOError:
            print "Can't read file for sub: %s" % self.name
    def save(self):
        if self.temporary:
            print "not saving temporary sub named",self.name
            return

        subfile = file("subs/%s" % self.name, 'w')
        names = self.levels.keys()
        names.sort()
        for name in names:
            val = self.levels[name]
            subfile.write("%s : %s\n" % (name, val))
    def set_level(self, channelname, level, save=1):
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
    def __mul__(self, scalar):
        return Submaster("%s*%s" % (self.name, scalar), 
            dict_scale(self.levels, scalar), temporary=1)
    __rmul__ = __mul__
    def max(self, *othersubs):
        return sub_maxes(self, *othersubs)
    def __repr__(self):
        levels = ' '.join(["%s:%.2f" % item for item in self.levels.items()])
        return "<'%s': [%s]>" % (self.name, levels)
    def get_dmx_list(self):
        leveldict = self.get_levels() # gets levels of sub contents

        levels = [0] * 68
        for k, v in leveldict.items():
            dmxchan = Patch.get_dmx_channel(k) - 1
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
                                            
def linear_fade(start, end, amount):
    """Fades between two floats by an amount.  amount is a float between
    0 and 1.  If amount is 0, it will return the start value.  If it is 1,
    the end value will be returned."""
    level = start + (amount * (end - start))
    return level

def sub_maxes(*subs):
    return Submaster("max(%r)" % (subs,),
        dict_max(*[sub.levels for sub in subs]), temporary=1)

class Submasters:
    "Collection o' Submaster objects"
    def __init__(self):
        self.submasters = {}

        import os
        files = os.listdir('subs')

        for filename in files:
            # we don't want these files
            if filename.startswith('.') or filename.endswith('~') or \
               filename.startswith('CVS'):
                continue
            self.submasters[filename] = Submaster(filename)
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
    def get_sub_by_name(self, name):
        "Makes a new sub if there isn't one."
        return self.submasters.get(name, Submaster(name))
    __getitem__ = get_sub_by_name

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
