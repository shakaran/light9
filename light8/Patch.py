from types import TupleType

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

def reload_data(dummy):
    global patch, reverse_patch
    if dummy:
        import ConfigDummy as Config
    else:
        import Config

    reload(Config)
    loadedpatch = Config.patch
    patch = {}
    reverse_patch = {}
    for k, v in loadedpatch.items():
        if type(k) == TupleType:
            for name in k:
                patch[name] = v
            reverse_patch[v] = k[0]
        else:
            patch[k] = v
            reverse_patch[v] = k
