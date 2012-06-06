import Tix as tk
from louie import dispatcher
from rdflib import RDF, RDFS, Literal
from light9 import Submaster
from light9.namespaces import L9
from light9.curvecalc.subterm import Subterm, Subexpr


class Subexprview(tk.Frame):
    def __init__(self,master,se,**kw):
        self.subexpr=se
        tk.Frame.__init__(self,master,**kw)
        self.evar = tk.StringVar()
        e = self.ent = tk.Entry(self,textvariable=self.evar)
        e.pack(side='left',fill='x',exp=1)
        self.expr_changed()
        self.evar.trace_variable('w',self.evar_changed)
        dispatcher.connect(self.expr_changed,"expr_changed",
                           sender=self.subexpr)
        self.error = tk.Label(self)
        self.error.pack(side='left')
        dispatcher.connect(lambda exc: self.error.config(text=str(exc)),
                           "expr_error",sender=self.subexpr,weak=0)
    def expr_changed(self):
        if self.subexpr.expr!=self.evar.get():
            self.evar.set(self.subexpr.expr)
    def evar_changed(self,*args):
        self.subexpr.expr = self.evar.get()

class Subtermview(tk.Frame):
    def __init__(self, master, graph, st, **kw):
        self.subterm = st
        tk.Frame.__init__(self,master,bd=1,relief='raised',**kw)
        l = tk.Label(self, text="sub %s" % self.subterm.submaster.name)
        l.pack(side='left')
        sev=Subexprview(self,self.subterm.subexpr)
        sev.pack(side='left',fill='both',exp=1)

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
                   Subexpr(curveset,expr))
    subterms.append(term)

    stv=Subtermview(master, graph, term)
    stv.pack(side='top',fill='x')

    return term
