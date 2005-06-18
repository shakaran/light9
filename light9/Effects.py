import random
import light9.Submaster as Submaster
from chase import chase as chase_logic

__all__ = ['chase']

thirds = 'third-l', 'third-c', 'third-r'
thirds_bounce = 'third-l', 'third-c', 'third-r', 'third-c'
flutter = ['scoop-l', 'scoop-c', 'scoop-r', 'down-c', 'down-l', 'down-r'] * 5
random.shuffle(flutter)

def chase(t, ontime=0.5, offset=0.2, onval=1.0, 
          offval=0.0, names=None, combiner=max):
    """names is list of sub or channel names"""
    sub_vals = {}
    chase_vals = chase_logic(t, ontime, offset, onval, offval, names, combiner)
    for name, value in chase_vals.items():
        sub = Submaster.get_sub_by_name(name)
        sub_vals[sub] = value

    return Submaster.combine_subdict(sub_vals)
