import random
import light9.Submaster as Submaster
from chase import chase as chase_logic

thirds = 'third-l', 'third-c', 'third-r'
thirds_bounce = 'third-l', 'third-c', 'third-r', 'third-c'
backs = ['back%d' % d for d in range(1, 11)]
rand_flutter = ['scoop-l', 'scoop-c', 'scoop-r', 'down-c', 'down-l', 'down-r', 'cyc', 'zip_blue', 'zip_red', 'zip_green', 'zip_orange'] + backs
rand_flutter *= 10
random.shuffle(rand_flutter)

# don't forget to update this!
__all__ = ['chase', 'thirds', 'thirds_bounce', 'rand_flutter', 'backs']

def chase(t, ontime=0.5, offset=0.2, onval=1.0, 
          offval=0.0, names=None, combiner=max):
    """names is list of sub or channel names"""
    sub_vals = {}
    chase_vals = chase_logic(t, ontime, offset, onval, offval, names, combiner)
    for name, value in chase_vals.items():
        sub = Submaster.get_sub_by_name(name)
        sub_vals[sub] = value

    return Submaster.combine_subdict(sub_vals)
