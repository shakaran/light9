
def maxes(dicts):
    '''
    ({'a' : 5, 'b' : 9}, {'a' : 10, 'b' : 943})
    '''
    newdict = {}
    for d in dicts:
        for k,v in d.items():
            newdict[k] = max(v, newdict.get(k, 0))
    return newdict

def scaledict(d,scl):
    # scales all values in dict and returns a new dict
    return dict([(k,v*scl) for k,v in d.items()])
    
# class Setting that scales, maxes        
