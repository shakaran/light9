import run_local
from light9 import dmxclient, Patch, Submaster
from light9.namespaces import L9

def test():
    assert Patch.get_channel_name(1) == "frontLeft"
    assert Patch.get_channel_name("1") == "frontLeft"
    assert Patch.get_channel_name("frontLeft") == "frontLeft"
    
    assert Patch.get_dmx_channel(1) == 1
    assert Patch.get_dmx_channel("1") == 1
    assert Patch.get_dmx_channel("frontLeft") == 1
    
    assert Patch.get_channel_name("b1") == "frontLeft"
    assert Patch.get_dmx_channel("b1") == 1
    assert Patch.resolve_name("b1") == "frontLeft"
    assert Patch.resolve_name("frontLeft") == "frontLeft"

    assert Patch.get_channel_uri("frontLeft") == L9['theater/skyline/channel/frontLeft']
    
