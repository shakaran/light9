"""Collected utility functions, many are taken from Drew's utils.py in
Cuisine CVS and Hiss's Utility.py."""

from __future__ import generators
import sys

__author__ = "David McClosky <dmcc@bigasterisk.com>, " + \
             "Drew Perttula <drewp@bigasterisk.com>"
__cvsid__ = "$Id: TLUtility.py,v 1.1 2003/05/25 08:25:35 dmcc Exp $"
__version__ = "$Revision: 1.1 $"[11:-2]

def make_attributes_from_args(*argnames):
    """
    This function simulates the effect of running
      self.foo=foo
    for each of the given argument names ('foo' in the example just
    now). Now you can write:
        def __init__(self,foo,bar,baz):
            copy_to_attributes('foo','bar','baz')
            ...
    instead of:
        def __init__(self,foo,bar,baz):
            self.foo=foo
            self.bar=bar
            self.baz=baz
            ... 
    """
    
    callerlocals=sys._getframe(1).f_locals
    callerself=callerlocals['self']
    for a in argnames:
        try:
            setattr(callerself,a,callerlocals[a])
        except KeyError:
            raise KeyError, "Function has no argument '%s'" % a

def enumerate(*collections):
    """Generates an indexed series:  (0,coll[0]), (1,coll[1]) ...
    
    this is a multi-list version of the code from the PEP:
    enumerate(a,b) gives (0,a[0],b[0]), (1,a[1],b[1]) ...
    """
    i = 0
    iters = [iter(collection) for collection in collections]
    while 1:
        yield [i,] + [iterator.next() for iterator in iters]
        i += 1

def dumpobj(o):
    """Prints all the object's non-callable attributes"""
    print repr(o)
    for a in [x for x in dir(o) if not callable(getattr(o, x))]:
        try:
            print "  %20s: %s " % (a, getattr(o, a))
        except:
            pass
    print ""

def dict_filter_update(d, **newitems):
    """Adds a set of new keys and values to dictionary 'd' if the values are
    true:

    >>> some_dict = {}
    >>> dict_filter_update(some_dict, a=None, b=0, c=1, e={}, s='hello')
    >>> some_dict
    {'c': 1, 's': 'hello'}
    """
    for k, v in newitems.items():
        if v: d[k] = v

def try_get_logger(channel):
    """Tries to get a logger with the channel 'channel'.  Will return a
    silent DummyClass if logging is not available."""
    try:
        import logging
        log = logging.getLogger(channel)
    except ImportError:
        log = DummyClass()
    return log

class DummyClass:
    """A class that can be instantiated but never used.  It is intended to
    be replaced when information is available.
    
    Usage:
    >>> d = DummyClass(1, 2, x="xyzzy")
    >>> d.someattr
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
      File "Utility.py", line 33, in __getattr__
        raise AttributeError, "Attempted usage of a DummyClass: %s" % key
    AttributeError: Attempted usage of a DummyClass: someattr
    >>> d.somefunction()
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
      File "Utility.py", line 33, in __getattr__
        raise AttributeError, "Attempted usage of a DummyClass: %s" % key
    AttributeError: Attempted usage of a DummyClass: somefunction"""
    def __init__(self, use_warnings=1, raise_exceptions=0, **kw):
        """Constructs a DummyClass"""
        make_attributes_from_args('use_warnings', 'raise_exceptions')
    def __getattr__(self, key):
        """Raises an exception to warn the user that a Dummy is not being
        replaced in time."""
        if key == "__del__":
            return
        msg = "Attempted usage of '%s' on a DummyClass" % key
        if self.use_warnings:
            import warnings
            warnings.warn(msg)
        if self.raise_exceptions:
            raise AttributeError, msg
        return lambda *args, **kw: self.bogus_function()
    def bogus_function(self):
        pass

class ClassyDict(dict):
    """A dict that accepts attribute-style access as well (for keys
    that are legal names, obviously). I used to call this Struct, but
    chose the more colorful name to avoid confusion with the struct
    module."""
    def __getattr__(self, a):
        return self[a]
    def __setattr__(self, a, v):
        self[a] = v
    def __delattr__(self, a):
        del self[a]

def trace(func):
    """Good old fashioned Lisp-style tracing.  Example usage:
    
    >>> def f(a, b, c=3):
    >>>     print a, b, c
    >>>     return a + b
    >>>
    >>>
    >>> f = trace(f)
    >>> f(1, 2)
    |>> f called args: [1, 2]
    1 2 3
    <<| f returned 3
    3

    TODO: print out default keywords (maybe)
          indent for recursive call like the lisp version (possible use of 
              generators?)"""
    name = func.func_name
    def tracer(*args, **kw):
        s = '|>> %s called' % name
        if args:
            s += ' args: %r' % list(args)
        if kw:
            s += ' kw: %r' % kw
        print s
        ret = func(*args, **kw)
        print '<<| %s returned %s' % (name, ret)
        return ret
    return tracer

# these functions taken from old light8 code
def dict_max(*dicts):
    """
    ({'a' : 5, 'b' : 9}, {'a' : 10, 'b' : 4})
      returns ==> {'a' : 10, 'b' : 9}
    """
    newdict = {}
    for d in dicts:
        for k,v in d.items():
            newdict[k] = max(v, newdict.get(k, 0))
    return newdict

def dict_scale(d,scl):
    """scales all values in dict and returns a new dict"""
    return dict([(k,v*scl) for k,v in d.items()])
    
def dict_subset(d, dkeys, default=0):
    """Subset of dictionary d: only the keys in dkeys.  If you plan on omitting
    keys, make sure you like the default."""
    newd = {} # dirty variables!
    for k in dkeys:
        newd[k] = d.get(k, default)
    return newd

# functions specific to Timeline
# TBD
def last_less_than(array, x):
    """array must be sorted"""
    best = None
    for elt in array:
        if elt <= x:
            best = elt
        elif best is not None:
            return best
    return best

# TBD
def first_greater_than(array, x):
    """array must be sorted"""
    array_rev = array[:]
    array_rev.reverse()
    best = None
    for elt in array_rev:
        if elt >= x:
            best = elt
        elif best is not None:
            return best
    return best


