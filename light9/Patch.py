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
        raise ValueError("Invalid channel name: %r" % name)

def get_channel_name(dmxnum):
    """if you pass a name, it will get normalized"""
    try:
        return reverse_patch[dmxnum]
    except KeyError:
        return str(dmxnum)

def get_channel_uri(name):
    return uri_map[name]

def dmx_from_uri(uri):
    return uri_patch[uri]

def reload_data():
    global patch, reverse_patch, uri_map, uri_patch
    patch = {}
    reverse_patch = {}
    uri_map = {}
    uri_patch = {}

    graph = showconfig.getGraph()

    for chan in graph.subjects(RDF.type, L9['Channel']):
        for which, name in enumerate([graph.label(chan)] +
                                     list(graph.objects(chan, L9['altName']))):
            name = str(name)
            uri_map[name] = chan

            if name in patch:
                raise ValueError("channel name %r used multiple times" % name)
            for output in graph.objects(chan, L9['output']):
                for addr in graph.objects(output, L9['dmxAddress']):
                    addrInt = int(addr)
                    patch[name] = addrInt
                    uri_patch[chan] = addrInt

                    if which == 0:
                        reverse_patch[addrInt] = name
                        reverse_patch[addr] = name
                        norm_name = name
                    else:
                        reverse_patch[name] = norm_name

# importing patch will load initial data
reload_data()

