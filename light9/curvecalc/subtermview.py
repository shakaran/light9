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
        self.entryBuffer.connect("deleted-text", self.evar_changed)
        self.entryBuffer.connect("inserted-text", self.evar_changed)
        dispatcher.connect(self.expr_changed,"expr_changed",
                           sender=self.subexpr)

        dispatcher.connect(lambda exc: self.error.set_text(str(exc)),
                           "expr_error",sender=self.subexpr,weak=0)
        
    def expr_changed(self):
        e = str(self.subexpr.expr)
        if e != self.entryBuffer.get_text():
            self.entryBuffer.set_text(e, len(e))
            
    def evar_changed(self,*args):
        print "hi change"
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


def add_one_subterm(graph, subUri, curveset, subterms, master, expr=None):
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
    master.attach(stv.label, 0, 1, y, y + 1, xoptions=0)
    master.attach(stv.exprView, 1, 2, y, y + 1)

    return term



def makeSubtermCommandRow(master, curveset, subterms, root, ssv, graph):
    """
    the row that starts with 'reload subs' button
    """
    f=tk.Frame(master,relief='raised',bd=1)
    newname = tk.StringVar()

    def add_cmd(evt):
        uri = L9['sub/%s' % newname.get()]
        graph.add((uri, RDF.type, L9.Subterm))
        graph.add((uri, RDFS.label, Literal(newname.get())))
        add_one_subterm(graph, uri,
                        curveset, subterms, ssv, None)
        if evt.state & 4: # control key modifier
            curveset.new_curve(newname.get())
        newname.set('')

    def reload_subs():
        dispatcher.send('reload all subs')

    tk.Button(f, text="reload subs (C-r)", 
        command=reload_subs).pack(side='left')
    tk.Label(f, text="new subterm named (C-Enter for curve too, C-n for focus):").pack(side='left')
    entry = tk.Entry(f, textvariable=newname)
    entry.pack(side='left', fill='x', exp=1)
    entry.bind("<Key-Return>", add_cmd)

    def focus_entry():
        entry.focus()
        
    dispatcher.connect(focus_entry, "focus new subterm", weak=False)

    return f
