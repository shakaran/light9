"""Persistent Tree Dictionaries

Incidentally, this is also the Hiss Preferences System.  However, PTD is
expected to be usable outside of Hiss."""

__author__ = "David McClosky <dmcc@bigasterisk.com>, " + \
             "Drew Perttula <drewp@bigasterisk.com>"
__cvsid__ = "$Id: TreeDict.py,v 1.1 2003/07/06 08:33:06 dmcc Exp $"
__version__ = "$Revision: 1.1 $"[11:-2]

try:
    # use gnosis's XML pickler if available
    import gnosis.xml.pickle as pickle

    # this hack is needed or else xml.pickle will not be able to restore
    # methods (they will be restored as mysterious classes which contain
    # the same attributes but no methods, 
    # gnosis.xml.pickle.util._util.originalclassname, to be specific)
    # the important thing to get from this comment is that we cannot properly
    # pickle classes without them being "assigned" into gnosis.xml.pickle.
    # i hope this gets fixed in a later version of pickle.
except ImportError:
    # fallback to standard library pickle
    import pickle

def allow_class_to_be_pickled(class_obj):
    """to be documented"""
    name = class_obj.__name__
    setattr(pickle, name, class_obj)

class TreeDict(dict):
    """TreeDict is the workhorse for the preferences system.  It allows
    for simple creation and access of preference trees.  It could be
    used to store anything, though."""
    def __getattr__(self, attr):
        """Gets an attribute/item, but with a twist.  If not present, the
        attribute will be created, with the value set to a new TreeDict."""
        if attr.startswith('__'): # if it's special, we let dict handle it
            return self.dictgetattr(attr)
        if attr in self:
            return dict.__getitem__(self, attr)
        else:
            newtree = self.__class__()
            self.set_parent_attrs(newtree, attr) # record ourselves as the 
                                                 # parent
            dict.__setitem__(self, attr, newtree)
            return newtree
    def __setattr__(self, attr, newval):
        """Sets an attribute/item to a new value."""
        if attr.startswith('__'): # if it's special, we let dict handle it
            return dict.__setattr__(self, attr, newval)
        else:
            oldval = self[attr] or None
            dict.__setitem__(self, attr, newval)
            if isinstance(newval, self.__class__):
                self.set_parent_attrs(newval, attr)
            self.changed_callback(attr, oldval, newval)
    def __delattr__(self, attr):
        """Deletes an attribute/item"""
        if attr.startswith('__'): # if it's special, we let dict handle it
            return dict.__delattr__(self, attr)
        else: # otherwise, they meant a normal attribute/item
            dict.__delitem__(self, attr)

    # attr and item access are now the same
    __getitem__ = __getattr__
    __setitem__ = __setattr__
    __delitem__ = __delattr__

    # Original getattr/setattr for storing special attributes
    def dictgetattr(self, attr):
        """dict's original __getattribute__ method.  This is useful for
        storing bookkeeping information (like parents) which shouldn't
        be persistent."""
        return dict.__getattribute__(self, attr)
    def dictsetattr(self, attr, newval):
        """dict's original __setattr__ method.  This is useful for
        storing bookkeeping information (like parents) which shouldn't
        be persistent."""
        return dict.__setattr__(self, attr, newval)
    def set_parent_attrs(self, newtree, key):
        """Set ourselves as the parent to a new key."""
        # record that we are the parent of this new object
        newtree.dictsetattr('__parent', self)

        # we store the key that newtree is in
        newtree.dictsetattr('__parent_key', key)
    def get_path(self):
        """Returns the path to this TreeDict."""
        try:
            parent = self.dictgetattr('__parent')
            key = self.dictgetattr('__parent_key')
            return parent.get_path() + [key] 
        except AttributeError:
            return []

    def changed_callback(self, attr, oldval, newval):
        """Called whenever an attribute is changed.  It will be called with
        three arguments: the attribute that changed, the previous value of
        the attribute, and the newvalue of the attribute.
        If the attribute didn't exist before, the old value will be None.

        This should be overridden by subclasses of TreeDict."""

    # Tree operations
    def tree_update(self, othertree):
        """Recursive update().  All keys from the othertree are copied over.
        If both this tree and the other tree have a key which is a TreeDict,
        we will recurse into it."""
        for key in othertree: # if the key is in the other tree, merge it into
                              # ours
            if key in self and isinstance(self[key], self.__class__):
                self[key].tree_update(othertree[key])
            else: # copy othertree's branch to ours
                self[key] = othertree[key]

    # Loading and saving
    def load(self, filename, clobber=1):
        """Combine this TreeDict with the TreeDict previously save()d
        to a file.  If clobber=1, this tree will be clear()ed before
        combining (this is the default)."""
        newprefs = pickle.load(file(filename))
        if clobber: self.clear()
        self.tree_update(newprefs)
        return self
    def save(self, filename):
        """Save this TreeDict to a file.  You can later restore the TreeDict
        by creating a TreeDict and using the load() method:

        treedict.save("tree.xml")
        newtreedict = TreeDict()
        newtreedict.load("tree.xml")"""
        pickle.dump(self, file(filename, 'w'))

    def pprint(self, depth=0):
        "A simple pretty printing method, useful for debugging"
        for key in self:
            print "%s%s =" % ('\t' * depth, key),
            val = self[key]
            if isinstance(val, self.__class__):
                print
                val.pprint(depth + 1)
            else:
                print repr(self[key])

allow_class_to_be_pickled(TreeDict)

if __name__ == "__main__":
    # We subclass TreeDict here so we can demonstrate how to override
    # changed_callback.
    RealTreeDict = TreeDict
    class TreeDict(RealTreeDict):
        def changed_callback(self, attr, oldval, newval):
            fullpath = self.get_path() + [attr]
            
            if 0: # more information
                print 'changed_callback %s: %s -> %s' % ('.'.join(fullpath), 
                                                         oldval, newval)
            else: # output looks like the Python code that built the tree
                print 'changed_callback %s = %r' % ('.'.join(fullpath), 
                                                         newval)

    # store our new class so we can pickle :(
    # maybe we give someone a list of classes that we use, and it handles
    # the rest.  or, we just record a list of classes seen using 
    # setattr callbacks.
    allow_class_to_be_pickled(TreeDict)
    
    True = 1
    False = 0
    
    defaults_tree = TreeDict()
    defaults_tree.auto_scroll_to_bottom = True
    defaults_tree.aging.enabled = True
    defaults_tree.aging.fade_exponent = 3
    defaults_tree.aging.user_colors = TreeDict({'user1' : 'color1',
                                                'user2' : 'color2'})

    import time
    defaults_tree.current_time = time.asctime()

    # on disk
    new_tree = TreeDict()
    new_tree.some_extra_pref = "hi mom"
    new_tree.auto_scroll_to_bottom = False
    new_tree.aging.user_colors.user1 = 'green'

    defaults_tree.tree_update(new_tree)
    defaults_tree.pprint()

    # test load / save
    print "---"
    defaults_tree.save("persistence_test.xml")
    loaded_tree = TreeDict().load("persistence_test.xml")
    loaded_tree.pprint()
