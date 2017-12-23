from typing import List, Dict
import numbers
import numpy as np
import graphviz
import tempfile
from IPython.display import SVG
from subprocess import check_call
from collections import defaultdict

fontsize = 13
subscript_fontsize = 10

YELLOW = "#fefecd"
BLUE = "#D9E6F5"
GREEN = "#cfe2d4"
DARK_GREY = "#444443"
BLACK = "#000000"

textcolor = BLACK #DARK_GREY

def sub(var : str, s):
    if isinstance(s, numbers.Number):
        return f'<font face="Times-Italic" point-size="{fontsize}">{var}</font><sub><font face="Times-Italic" point-size="{subscript_fontsize}">{str(s)}</font></sub>'
    else:
        return f'<font face="Times-Italic" point-size="{fontsize}">{var}</font><sub><font face="Times-Italic" point-size="{subscript_fontsize}">{s}</font></sub>'


def fraction(top : str, bottom : str):
    return f"""<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="0">
        <tr><td cellspacing="0" cellpadding="0" border="1" sides="b">{top}</td></tr>
        <tr><td cellspacing="0" cellpadding="0">{bottom}</td></tr>
    </table>
    """


def seq(*elems : List[str]):
    col = '<td cellspacing="0" cellpadding="0" border="0">%s</td>'
    return f"""<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="0">
        <tr>{''.join([col % elem for elem in elems])}</tr>
    </table>
    """


def round(x):
    if isinstance(x, int):
        return x
    if np.isclose(x, 0.0):
        return 0
    return float(f"{x:.4f}")


def nodes(t) -> (List, List, Dict):
    """
    Return preorder list of nodes from ast t and clusters of operands
    """
    all = []
    clusters = []
    work = [t]
    while len(work)>0:
        node = work.pop(0)
        all.append(node)
        if len(node.children())>0:
            work += node.children()
            nonvarleaf_kids = [n for n in node.children() if not n.isvar()]
            if len(nonvarleaf_kids)>1:
                clusters += [nonvarleaf_kids] # track nonleaf children groups so we can make clusters
    return all, clusters


def parents(t) -> Dict:
    """
    Return dict mapping node to list of parents. Operators, Consts always have
    singleton parent list. Vars can have multiple parents.
    """
    d = defaultdict(list)
    parents_(t,None,d)
    return d


def parents_(t, parent, d) -> None:
    if parent is None:
        d[t] = None
    else:
        d[t] += [parent]

    for child in t.children():
        parents_(child,t,d)


def leaves(t):
    """Return preorder list of nodes from ast t"""
    the_leaves = []
    work = [t]
    while len(work)>0:
        node = work.pop(0)
        if len(node.children())==0:
            if node not in the_leaves:
                the_leaves.append(node)
        else:
            work += node.children()
    return the_leaves


def show(g : graphviz.files.Source):
    fname = tempfile.mktemp('.dot')
    dot(g, filename=fname+".svg", format='svg')
    return SVG(filename=fname+".svg")


def dot(g, filename, format='svg', dpi=None):
    fname = tempfile.mktemp('.dot')
    g.save(fname)
    if not filename.endswith('.'+format):
        filename = filename + '.'+format
    options = ['-o', filename, f'-T{format}:cairo', fname]
    if dpi:
        options.append(f'-Gdpi={dpi}')
    check_call(['dot']+options)


def set_var_indices(t, first_index : int = 0) -> None:
    the_leaves = leaves(t)
    inputs = [n for n in the_leaves if n.isvar()]
    i = first_index
    for leaf in inputs:
        leaf.vi = i
        if leaf.varname is None:
            leaf.varname = sub("x", i)
        i += 1

    set_var_indices_(t,i)


def set_var_indices_(t, vi : int) -> int:
    if t.vi >= 0:
        return vi
    if t.isvar():
        t.vi = vi
        return t.vi + 1
    elif len(t.children())==0: # must be constant
        t.vi = vi
        return t.vi + 1
    elif hasattr(t, 'left'): # binary op
        vi = set_var_indices_(t.left,vi)
        vi = set_var_indices_(t.right,vi)
        t.vi = vi
        return t.vi + 1
    elif hasattr(t, 'opnd'):  # unary op
        t.vi = set_var_indices_(t.opnd,vi)
        return t.vi + 1
    return vi