from typing import List

from autodx.backward_ast import *
from autodx.support import *

YELLOW = "#fefecd" # "#fbfbd0" # "#FBFEB0"
BLUE = "#D9E6F5"
GREEN = "#cfe2d4"

def eqn(t : Expr) -> List[str]:
    """Perform a dynamic dispatch to X_viz.eqn() for node type X"""
    vizclass = globals()[t.__class__.__name__ + "_viz"]
    return getattr(vizclass, "eqn")(t)


def eqndx(t : Expr, parent : Expr) -> List[str]:
    """Perform a dynamic dispatch to X_viz.eqndx() for node type X"""
    vizclass = globals()[t.__class__.__name__ + "_viz"]
    return getattr(vizclass, "eqndx")(t, parent)


class Var_viz:
    @staticmethod
    def eqn(t : Var) -> List[str]:
        if t.varname is not None:
            return [f"{sub('v',t.vi)}", f"{t.varname}", round(t.value())]
        else:
            return [f"{sub('v',t.vi)}", "", round(t.value())]

    @staticmethod
    def eqndx(t : Var, parent : Expr) -> List[str]:
        return [fraction("∂y", f"{'∂'+t.varname}"),
                fraction("∂y", f"{sub('∂v',t.vi)}"),
                t.dydv]


class Const_viz:
    @staticmethod
    def eqn(t : Const) -> List[str]:
        return [f"{sub('v',t.vi)}", "", round(t.value())]

    @staticmethod
    def eqndx(t : Const, parent : Expr) -> List[str]:
        return [fraction("∂y", f"{sub('∂v',t.vi)}"),
                "",
                t.dydv]


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
    pass


class Sub_viz(BinaryOp_viz):
    pass


class Mul_viz(BinaryOp_viz):
    @staticmethod
    def eqndx(t : BinaryOp, parent : Expr) -> List[str]:
        return [
            fraction("∂y", f"{'∂'+sub('v',t.vi)}"),
            f"{sub('v',t.left.vi)} &times; {sub('∂v',t.right.vi)} + {sub('v',t.right.vi)} &times; {sub('∂v',t.left.vi)}",
            f"{round(t.left.value() * t.right.dvdx(wrt))} + {round(t.right.value() * t.left.dvdx(wrt))} = {round(t.dvdx(wrt))}"]


class Div_viz(BinaryOp_viz):
    pass


class Sin_viz(UnaryOp_viz):
    pass


class Ln_viz(UnaryOp_viz):
    pass

def astviz(t : Expr) -> graphviz.Source:
    "I had to do $ brew install graphviz --with-pango to get the cairo support for <sub>"
    set_var_indices(t,1)
    the_leaves = leaves(t)
    allnodes, clusters = nodes(t)
    the_nonleaves = [n for n in allnodes if not n.isleaf()]
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
            {nltab.join([nodeviz(node) for node in cluster])}
        }}\n"""
    s = f"""

    digraph G {{
        nodesep=.1;
        ranksep=.3;
        rankdir=TD;
        node [penwidth="0.5", shape=box, width=.1, height=.1];
        // OPERATORS
        {nltab.join([nodeviz(node) for node in the_nonleaves])}
        // CONSTANTS (not operand of binary op)
        {nltab.join([nodeviz(node) for node in [n for n in consts if n not in cluster_nodes]])}
        // OPERAND CLUSTERS
        {opnd_clusters}
        // INPUTS (leaves)
        subgraph cluster_inputs {{
            style=invis
            {nltab.join([nodeviz(node) for node in inputs])}
        }}
        // EDGES
        {nltab.join(connections)}
    }}
    """

    Var.VAR_COUNT = 1 # reset after visualization so next one has vars x1, x2, etc...

    return graphviz.Source(s)

def nodeviz(t : Expr, parent : Expr) -> str:
    color = GREEN if isinstance(t,Var) else YELLOW
    return f'v{t.vi} [color="#444443", margin="0.02", fontcolor="#444443", fontsize="13" fontname="Times-Italic", style=filled, fillcolor="{color}", label=<{nodehtml(t,parent)}>];'


def connviz(t : Expr, kid : Expr) -> str:
    return f'v{t.vi} -> v{kid.vi} [penwidth="0.5", color="#444443", arrowsize=.4]'


def nodehtml(t : Expr, parent : Expr) -> str:
    rows = []
    e = eqn(t)
    if isinstance(t, Const):
        rows.append(f"""<tr><td>{e[0]}</td><td> = </td><td align="left">{e[2]}</td></tr>""")
        edx = eqndx(t,parent)
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

        edx = eqndx(t,parent)
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
    x1 = Var(3)
    x2 = Var(5)
    y = x1 * x2

    ast = y
    set_var_indices(y,1)

    # compute gradients in leaves
    y = ast.forward()
    ast.backward()
    foo = [x.dydv for x in [x1,x2]]

    g = astviz(ast)
    print(g.source)
    g.view()

    #
    # x1 = Var(2, sub("x",1))
    # x2 = Var(5, sub("x",2))
    # y = ln(x1) + x1 * x2 - sin(x2) * 9
    # g = astviz(y, x1)
    # print(g.source)
    # g.view()
