from __future__ import division

def chase(t, ontime=0.5, offset=0.2, onval=1.0, 
          offval=0.0, names=None, combiner=max):
    names = names or []
    # maybe this is better:
    # period = ontime + ((offset + ontime) * (len(names) - 1))
    period = (offset + ontime) * len(names)
    outputs = {}
    for index, name in enumerate(names):
        # normalize our time
        local_offset = (offset + ontime) * index
        local_t = t - local_offset
        local_t %= period

        # see if we're still in the on part
        if local_t <= ontime:
            value = onval
        else:
            value = offval

        # it could be in there twice (in a bounce like (1, 2, 3, 2)
        if name in outputs:
            outputs[name] = combiner(value, outputs[name])
        else:
            outputs[name] = value
    return outputs

if __name__ == "__main__":
    # a little testing
    for x in range(80):
        x /= 20.0
        output = chase(x, onval='x', offval=' ', ontime=0.1, offset=0.2,
                       names=('a', 'b', 'c', 'd'))
        output = output.items()
        output.sort()
        print "%.2f\t%s" % (x, ' '.join([str(x) for x in output]))
