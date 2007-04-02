import os
from rdflib import RDF
from light9.namespaces import L9
from light9 import showconfig


def resolve_name(channelname):
    "Ensure that we're talking about the primary name of the light."
    return get_channel_name(get_dmx_channel(channelname))

def get_all_channels():
    """returns primary names for all channels (sorted)"""
    prinames = reverse_patch.values()[:]
    prinames.sort()
    return prinames

def get_dmx_channel(name):
    if name in patch:
        return patch[name]

    try:
        i = int(name)
        return i
    except ValueError:
        raise ValueError("Invalid channel name: %s" % name)

def get_channel_name(dmxnum):
    try:
        return reverse_patch[dmxnum]
    except KeyError:
        return str(dmxnum)

def reload_data():
    global patch, reverse_patch
    patch = {}
    reverse_patch = {}

    graph = showconfig.getGraph()

    for chan in graph.subjects(RDF.type, L9['Channel']):
        name = graph.label(chan)
        # int() shouldn't be required, but some code in subcomposer
        # ignores channel numbers if they're not int
        addr = int(graph.value(chan, L9['dmxAddress']))
        patch[name] = addr
        reverse_patch[addr] = name

# importing patch will load initial data
reload_data()

