import os
from light9.Submaster import Submaster

def testCalc():
    dest = "/home/drewp/projects/light9/show/dance2007/subs/sub"
    try:
        os.remove(dest)
    except OSError:
        pass
    
    sub = Submaster('sub', {'front1' : .5, 'front2' : .7})
    assert not sub.no_nonzero()
    assert sub.get_dmx_list()
    sub.save()
    
    assert os.path.exists(dest)

    sub2 = Submaster('sub')
    sub2.reload()
    assert sub == sub2
    assert sub2.get_levels() == {'front1' : .5, 'front2' : .7}
