from typing import List

from autodx.forward_vec_ast import *
from autodx.support import *
from autodx.support import fontsize, YELLOW, GREEN, textcolor


def eqn(t : Expr) -> List[str]:
    """Perform a dynamic dispatch to X_viz.eqn() for node type X"""
    vizclass = globals()[t.__class__.__name__ + "_viz"]
    return getattr(vizclass, "eqn")(t)


def eqndx(t : Expr, wrt : 'Expr') -> List[str]:
    """Perform a dynamic dispatch to X_viz.eqndx() for node type X"""
    vizclass = globals()[t.__class__.__name__ + "_viz"]
    return getattr(vizclass, "eqndx")(t, wrt)


class Var_viz:
    @staticmethod
    def eqn(t : Var) -> List[str]:
        if t.varname is not None:
            return [f"{sub('v',t.vi)}", f"{t.varname}", round(t.value())]
        else:
            return [f"{sub('v',t.vi)}", "", round(t.value())]

    @staticmethod
    def eqndx(t : Var, wrt : 'Expr') -> List[str]:
        result = 1 if t==wrt else 0
        if wrt.varname is not None and t.varname is not None:
            return [fraction(f"{sub('∂v',t.vi)}", f"{'∂'+wrt.varname}"),
                    fraction(f"{'∂'+t.varname}", f"{'∂'+wrt.varname}"),
                    result]
        else:
            return [fraction(f"{sub('∂v',t.vi)}", f"{sub('∂v',wrt.vi)}"), "", result]


class Const_viz:
    @staticmethod
    def eqn(t : Const) -> List[str]:
        return [f"{sub('v',t.vi)}", "", round(t.value())]

    @staticmethod
    def eqndx(t : Const, wrt : 'Expr') -> List[str]:
        result = 1 if t==wrt else 0
        if wrt.varname is not None:
            return [fraction(f"{sub('∂v',t.vi)}", f"{'∂'+wrt.varname}"), "", result]
        else:
            return [fraction(f"{sub('∂v',t.vi)}", f"{sub('∂v',wrt.vi)}"), "", result]


class BinaryOp_viz:
    def eqn(t : BinaryOp) -> List[str]:
        if t.op == '*':
            op = "&times;"
        elif t.op == '-':
            op = "&minus;"
        elif t.op == '/' :
            op = "&frasl;"
        else:
            op = t.op
        return [f"{sub('v',t.vi)}",
                f"{sub('v',t.left.vi)} {op} {sub('v',t.right.vi)}",
                round(t.value())]



class UnaryOp_viz:
    @staticmethod
    def eqn(t : UnaryOp) -> List[str]:
        return [f"{sub('v',t.vi)}",
                f"{t.op}({sub('v',t.opnd.vi)})" if t.op.isalnum() else f"{t.op} {sub('v',t.opnd.vi)}",
                round(t.value())]


class Add_viz(BinaryOp_viz):
    @staticmethod
    def eqndx(t : BinaryOp, wrt : 'Expr') -> List[str]:
        return [
            fraction(f"{sub('∂v',t.vi)}", f"{'∂'+wrt.varname}"),
            f"{sub('∂v',t.left.vi)} + {sub('∂v',t.right.vi)}",
            f"{round(t.left.dvdx(wrt))} + {round(t.right.dvdx(wrt))} = {round(t.dvdx(wrt))}"
        ]


class Sub_viz(BinaryOp_viz):
    @staticmethod
    def eqndx(t : BinaryOp, wrt : 'Expr') -> List[str]:
        return [#f"{sub('∂v',t.vi)}",
            fraction(f"{sub('∂v',t.vi)}", f"{'∂'+wrt.varname}"),
            f"{sub('∂v',t.left.vi)} &minus; {sub('∂v',t.right.vi)}",
            f"{round(t.left.dvdx(wrt))} &minus; {round(t.right.dvdx(wrt))} = {round(t.dvdx(wrt))}"
        ]


class Mul_viz(BinaryOp_viz):
    @staticmethod
    def eqndx(t : BinaryOp, wrt : 'Expr') -> List[str]:
        return [
            fraction(f"{sub('∂v',t.vi)}", f"{'∂'+wrt.varname}"),
            f"{sub('v',t.left.vi)} &times; {sub('∂v',t.right.vi)} + {sub('v',t.right.vi)} &times; {sub('∂v',t.left.vi)}",
            f"{round(t.left.value() * t.right.dvdx(wrt))} + {round(t.right.value() * t.left.dvdx(wrt))} = {round(t.dvdx(wrt))}"]


class Div_viz(BinaryOp_viz):
    @staticmethod
    def eqndx(t : BinaryOp, wrt : 'Expr') -> List[str]:
        return [
            fraction(f"{sub('∂v',t.vi)}", f"{'∂'+wrt.varname}"),
            fraction(f"{sub('v',t.right.vi)} &times; {sub('∂v',t.left.vi)} &minus; {sub('v',t.left.vi)} &times; {sub('∂v',t.right.vi)}", f"{sub('v',t.right.vi)}<sup>2</sup>"),
            '<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="1"><tr><td>' +
            fraction(f"{round(t.right.value())} &times; {round(t.left.dvdx(wrt))} &minus; {round(t.left.value())} &times; {round(t.right.dvdx(wrt))}", f"{round(t.right.value())}<sup>2</sup>") +
            f"</td><td> = {round(t.dvdx(wrt))}</td></tr></table>",
            f"{round(t.left.value() * t.right.dvdx(wrt))} + {round(t.right.value() * t.left.dvdx(wrt))} = {round(t.dvdx(wrt))}"]


class Sin_viz(UnaryOp_viz):
    @staticmethod
    def eqndx(t : UnaryOp, wrt : 'Expr') -> List[str]:
        return [
            fraction(f"{sub('∂v',t.vi)}", f"{'∂'+wrt.varname}"),
            f"cos({sub('v',t.opnd.vi)}) &times; {sub('∂v',t.opnd.vi)}",
            f"cos({round(t.opnd.value())}) &times; {round(t.opnd.dvdx(wrt))} = {round(t.dvdx(wrt))}"]


class Ln_viz(UnaryOp_viz):
    @staticmethod
    def eqndx(t : UnaryOp, wrt : 'Expr') -> List[str]:
        return [
            fraction(f"{sub('∂v',t.vi)}", f"{'∂'+wrt.varname}"),
            f"(1 &frasl; {sub('v',t.opnd.vi)}) &times; {sub('∂v',t.opnd.vi)}",
            f"(1 &frasl; {round(t.opnd.value())}) &times; {round(t.opnd.dvdx(wrt))} = {round(t.dvdx(wrt))}"]


class Expand_viz(UnaryOp_viz):
    @staticmethod
    def eqndx(t : BinaryOp, wrt : 'Expr') -> List[str]:
        return [
            fraction(f"{sub('∂v',t.vi)}", f"{'∂'+wrt.varname}"),
            f"cos({sub('v',t.opnd.vi)}) &times; {sub('∂v',t.opnd.vi)}",
            f"cos({round(t.opnd.value())}) &times; {round(t.opnd.dvdx(wrt))} = {round(t.dvdx(wrt))}"]


def nonleaves(t : Expr) -> (List[Expr], List[List[Expr]]):
    """Return preorder list of nodes from ast t"""
    the_nonleaves = []
    clusters = []
    work = [t]
    while len(work)>0:
        node = work.pop(0)
        if len(node.children())>0:
            the_nonleaves.append(node)
            work += node.children()
            nonvarleaf_kids = [n for n in node.children() if not isinstance(n,Var)]
            if len(nonvarleaf_kids)>1:
                clusters += [nonvarleaf_kids] # track nonleaf children groups so we can make clusters
    return the_nonleaves, clusters


def astviz(t : Expr, wrt : Expr) -> graphviz.Source:
    "I had to do $ brew install graphviz --with-pango to get the cairo support for <sub>"
    set_var_indices(t,1)
    the_leaves = leaves(t)
    the_nonleaves, clusters = nonleaves(t)
    cluster_nodes = [item for cluster in clusters for item in cluster]

    consts = [n for n in the_leaves if isinstance(n,Const)]
    inputs = [n for n in the_leaves if isinstance(n,Var)]
    connections = []
    for node in the_leaves + the_nonleaves:
        connections += [connviz(node, kid) for kid in node.children()]

    opnd_clusters = ""
    the_nonleaves = [n for n in the_nonleaves if n not in cluster_nodes] # don't repeat nodes already in operand clusters
    nltab = "\n\t"
    # note: rank=same with edges crap is to force order of operands to be same as order given in dot file (subgraphs mess up order)
    # but we need subgraphs to put operands at same tree level.
    for i,cluster in enumerate(clusters):
        opnd_clusters += f"""
            subgraph cluster_opnds{i} {{
            style=invis; {{rank=same; {'->'.join([f'v{n.vi}' for n in cluster])} [style=invis]}}
            {nltab.join([nodeviz(node,wrt) for node in cluster])}
        }}\n"""
    s = f"""

    digraph G {{
        nodesep=.1;
        ranksep=.3;
        rankdir=RL;
        node [penwidth="0.5", shape=box, width=.1, height=.1];
        // OPERATORS
        {nltab.join([nodeviz(node,wrt) for node in the_nonleaves])}
        // CONSTANTS (not operand of binary op)
        {nltab.join([nodeviz(node,wrt) for node in [n for n in consts if n not in cluster_nodes]])}
        // OPERAND CLUSTERS
        {opnd_clusters}
        // INPUTS (leaves)
        subgraph cluster_inputs {{
            style=invis
            {nltab.join([nodeviz(node,wrt) for node in inputs])}
        }}
        // EDGES
        {nltab.join(connections)}
    }}
    """

    Var.VAR_COUNT = 1 # reset after visualization so next one has vars x1, x2, etc...

    return graphviz.Source(s)

def nodeviz(t : Expr, wrt : Expr) -> str:
    color = GREEN if isinstance(t,Var) else YELLOW
    return f'v{t.vi} [color="{DARK_GREY}", margin="0.02", fontcolor="{textcolor}", fontsize="{fontsize}" fontname="Times-Italic", style=filled, fillcolor="{color}", label=<{nodehtml(t,wrt)}>];'


def connviz(t : Expr, kid : Expr) -> str:
    return f'v{t.vi} -> v{kid.vi} [penwidth="0.5", color="{DARK_GREY}", arrowsize=.4]'


def nodehtml(t : Expr, wrt : Expr) -> str:
    rows = []
    e = eqn(t)
    if isinstance(t, Const):
        rows.append(f"""<tr><td>{e[0]}</td><td> = </td><td align="left">{e[2]}</td></tr>""")
        if wrt is not None:
            edx = eqndx(t, wrt)
            rows.append(
                f"""<tr><td>{edx[0]}</td><td> = </td><td align="left">{edx[2]}</td></tr>""")
    else:
        if len(e)==1:
            rows.append(f"""
            <tr><td>{e[0]}</td><td> = </td><td align="left">{e[1]}</td><td> = </td><td align="left">{e[2]}</td></tr>
            """)
        else:
            rows.append(f"""
            <tr><td>{e[0]}</td><td> = </td><td align="left">{e[1]}</td><td> = </td><td align="left">{e[2]}</td></tr>
            """)

        if wrt is not None:
            edx = eqndx(t,wrt)
            if len(edx)==1:
                rows.append(f"""
                <tr><td>{edx[0]}</td><td></td><td></td><td>=</td><td></td></tr>
                """)
            else:
                rows.append(f"""
                <tr><td>{edx[0]}</td><td> = </td><td align="left">{edx[1]}</td><td>=</td><td align="left">{edx[2]}</td></tr>
                """)

    return f"""<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="1">
    {''.join(rows)}
    </table>
    """

if __name__ == '__main__':
    b = [Var(2), Var(3)]
    c = Var(5)
    y = b + c
    # y = x1 * x2 - sin(x2)
    g = astviz(y, c)
    print(g.source)
    g.view()
    # dot(g,filename="/tmp/f.png",format='png',dpi=300)

    #
    # x1 = Var(2, sub("x",1))
    # x2 = Var(5, sub("x",2))
    # y = ln(x1) + x1 * x2 - sin(x2) * 9
    # g = astviz(y, x1)
    # print(g.source)
    # g.view()
