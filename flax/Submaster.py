from __future__ import division
from TLUtility import dict_scale, dict_max

import sys
sys.path.append('../light8')

import Patch

class Submaster:
    "Contain a dictionary of levels, but you didn't need to know that"
    def __init__(self, name, leveldict=None):
        self.name = name
        if leveldict:
            self.levels = leveldict
        else:
            self.levels = {}
            self.reload()
    def reload(self):
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
            dict_scale(self.levels, scalar))
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
        # possibly busted -- don't use unless you know what you're doing
        self.set_all_levels(self.levels.copy())

def sub_maxes(*subs):
    return Submaster("max(%r)" % (subs,),
        dict_max(*[sub.levels for sub in subs]))

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
        return self.submasters.values()
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
