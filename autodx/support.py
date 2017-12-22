import numbers
import numpy as np
import graphviz
import tempfile
from IPython.display import SVG
from subprocess import check_call


def sub(var : str, s):
    if isinstance(s, numbers.Number):
        return f'<font face="Times-Italic" point-size="13">{var}</font><sub><font face="Times-Italic" point-size="9">{str(s)}</font></sub>'
    else:
        return f'<font face="Times-Italic" point-size="13">{var}</font><sub><font face="Times-Italic" point-size="9">{s}</font></sub>'


def partial_html(top : str, bottom : str):
    return f"""<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="0">
        <tr><td cellspacing="0" cellpadding="0" border="1" sides="b">{top}</td></tr>
        <tr><td cellspacing="0" cellpadding="0">{bottom}</td></tr>
    </table>
    """


def round(x):
    if isinstance(x, int):
        return x
    if np.isclose(x, 0.0):
        return 0
    return float(f"{x:.4f}")


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


def display(g : graphviz.files.Source):
    fname = tempfile.mktemp('.dot')
    g.save(fname)
    check_call(['dot', '-o', fname+".svg", '-Tsvg:cairo', fname])
    return SVG(filename=fname+".svg")


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