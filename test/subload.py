# run this with py.test
import run_local
import os, shutil
import py.test
from light9 import dmxclient, Patch, Submaster
from light9.namespaces import L9

def testCreateArgs():
    py.test.raises(TypeError, Submaster.Submaster)
    assert Submaster.Submaster("newname", leveldict={})
    assert Submaster.Submaster(sub=L9['sub/newname'])
    assert Submaster.Submaster(name="newname", sub=L9["sub/newname"])
    py.test.raises(ValueError, Submaster.Submaster(name="newname",
                                                   sub=L9["other/newname"]))

    # old code might try to pass leveldict positionally
    py.test.raises(Exception, Submaster.Submaster("newname", {}))

def testLevels():
    levels = {'1' : .5, '2' : 1}
    s = Submaster.Submaster("newname", leveldict=levels)
    assert s.get_levels() == levels

    s.set_level('3', .5, save=False)
    assert s.get_levels()['3'] == .5

    assert s.get_dmx_list()[:3] == [.5, 1, .5]
    
    
    #s = Submaster.Submasters().get_sub_by_name("t1")
    #assert s.get_dmx_list() == [0]
