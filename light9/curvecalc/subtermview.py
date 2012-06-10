import gtk
from louie import dispatcher
from rdflib import RDF, RDFS, Literal
from light9 import Submaster
from light9.namespaces import L9
from light9.curvecalc.subterm import Subterm, Subexpr

class Subexprview(object):
    def __init__(self, se):
        self.subexpr = se

        self.box = gtk.HBox()

        self.entryBuffer = gtk.EntryBuffer("", -1)
        self.entry = gtk.Entry()
        self.error = gtk.Label("")

        self.box.pack_start(self.entry, expand=True)
        self.box.pack_start(self.error, expand=False)

        self.entry.set_buffer(self.entryBuffer)
        self.expr_changed()
        self.entryBuffer.connect("deleted-text", self.entry_changed)
        self.entryBuffer.connect("inserted-text", self.entry_changed)
        dispatcher.connect(self.expr_changed,"expr_changed",
                           sender=self.subexpr)

        dispatcher.connect(lambda exc: self.error.set_text(str(exc)),
                           "expr_error",sender=self.subexpr,weak=0)
        
    def expr_changed(self):
        e = str(self.subexpr.expr)
        if e != self.entryBuffer.get_text():
            self.entryBuffer.set_text(e, len(e))
            
    def entry_changed(self, *args):
        self.subexpr.expr = self.entryBuffer.get_text()

class Subtermview(object):
    """
    has .label and .exprView widgets for you to put in a table
    """
    def __init__(self, graph, st):
        self.subterm = st

        self.label = gtk.Label("sub %s" % self.subterm.submaster.name)

        sev = Subexprview(self.subterm.subexpr)
        self.exprView = sev.box


def add_one_subterm(graph, subUri, curveset, subterms, master, expr=None, show=False):
    subname = graph.label(subUri)
    print "%s's label is %s" % (subUri, subname)
    if not subname: # fake sub, like for a chase
        st = graph.subjects(L9['sub'], subUri).next()
        subname = graph.label(st)
        print "using parent subterm's name instead. parent %r, name %r" % (st, subname)
    assert subname, "%s has no name" % subUri
    if expr is None:
        expr = '%s(t)' % subname

    term = Subterm(Submaster.Submaster(graph=graph, name=subname, sub=subUri),
                   Subexpr(curveset, expr))
    subterms.append(term)

    stv = Subtermview(graph, term)
    y = master.get_property('n-rows')
    master.resize(y + 1, columns=2)
    master.attach(stv.label, 0, 1, y, y + 1, xoptions=0, yoptions=0)
    master.attach(stv.exprView, 1, 2, y, y + 1, yoptions=0)
    if show:
        master.show_all()
    return term


