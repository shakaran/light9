from Subs import *
from Patch import *
from types import TupleType

from Config import patch, subs

import re
import Patch
Patch.reload_data(0)

def resolve_name(channelname):
    "Insure that we're talking about the primary name of the light"
    return Patch.get_channel_name(Patch.get_dmx_channel(channelname))

subusage = {}

# colors = 'ROGBVndcihs'
colors = 'ndcihs'

color_chart = {
    '1-01' : 'ROYd',   # broadway (morning - afternoon)
    '1-02' : 'i',      # int. mission
    '1-03' : 'R',      # phone booth
    '1-04' : 'RBVh',   # hotbox
    '1-05' : 'RBd',    # off broadway
    '1-06' : 'ROYd',   # ext. mission
    '1-07' : 'ROYn',   # gambler intro, off broadway
    '1-08' : 'ROBIVc',  # havana, clubs
    '1-09' : 'ROYBIVc', # havana, outside, night
    '1-10' : 'BVn',     # ext. mission, night (4am)

    '2-01' : 'RBIVh',  # hotbox
    '2-02' : 'RBn',    # more can i wish you
    '2-03' : 'GBs',    # sewer (crap game)
    '2-04' : 'Bn',     # sue me
    '2-05' : 'i',      # int. mission
    '2-06' : '',       # marry
    '2-07' : 'd',      # broadway finale
}

scene_names = {
    '1-01' : 'broadway (morning to afternoon)',
    '1-02' : 'int. mission',
    '1-03' : 'phone booth',
    '1-04' : 'hotbox',
    '1-05' : 'guys and dolls (off broadway)',
    '1-06' : 'ext. mission, lunch time',
    '1-07' : 'gambler intro, off broadway',
    '1-08' : 'havana, clubs',
    '1-09' : 'havana, outside, night',
    '1-10' : 'ext. mission, night (4am)',

    '2-01' : 'hotbox',
    '2-02' : 'more can i wish you',
    '2-03' : 'sewer (crap game)',
    '2-04' : 'sue me',
    '2-05' : 'rock the boat (int. mission)',
    '2-06' : 'marry (trav)',
    '2-07' : 'finale (broadway)',
}

sub_to_scene = {}

blacklist = 'god upfill1 upfill2 upfill3 upfill4 red1 red2 red3 red4 blue1 blue2 blue3 blue4 cycleft cycright sidefill1 sidefill2'.split()
blacklist.extend(['side l','side r'])

for subname, levdict in subs.items():
    if type(subname) == TupleType:
        subname = subname[0]
    oldname = subname
    subname = re.sub(r'\*(\d-\d+)-.*', r'\1', subname)
    if oldname == subname: continue
    sub_to_scene[oldname] = subname
    subname = oldname # restore 'em.  restore 'em good.
    if not levdict:
        print "Warning: %s is useless (empty sub)." % subname
    else:
        for ch, lev in levdict.items():
            if lev:
                ch = resolve_name(ch)
                subusage.setdefault(ch, [])
                subusage[ch].append((lev, subname))

def twist(l):
    return [(b,a) for a,b in l]

def format_usage(ch, usage):
    if ch in blacklist: return
    usage=twist(usage)
    usage.sort()
#    usage.reverse()
    usage=twist(usage)
    print "======= %s ======= (%d uses)" % (ch, len(usage))
    if 1:
        use_str = ''
        for lev, sub in usage:
            if lev>30:
                if sub_to_scene[sub] in color_chart:
                    subcolors = color_chart[sub_to_scene[sub]]
                    col_str = ''
                    for c in colors:
                        if c in subcolors: col_str += c
                        else: col_str +=  ' '
                    print col_str,
                else:
                    print ' ' * len(colors),
                scenename = scene_names.get(sub_to_scene[sub], '')
                levbar="*"*(lev//5)
                print '  %3d %-20s\t%-30s %s' % (lev, levbar,sub, scenename)
    else:
        use_str = '\n    '.join(["%d\t%s" % (lev, sub) for lev, sub in usage])
        print '    ' + use_str

subitems = subusage.items()
subitems.sort()
for ch, usage in subitems:
    if 0:
        usedict = {}
        for lev, subname in usage: # remove duplicates
            usedict[subname] = max(lev, usedict.get(subname, 0))

        newusage = [(lev, sub) for sub, lev in usedict.items()]

        format_usage(ch, newusage)
    else:
        format_usage(ch, usage)
