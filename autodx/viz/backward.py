from typing import List

from autodx.backward_ast import *
from autodx.support import *

from autodx.support import fontsize, YELLOW, GREEN, textcolor

def eqn(t : Expr) -> List[str]:
    """Perform a dynamic dispatch to X_viz.eqn() for node type X"""
    vizclass = globals()[t.__class__.__name__ + "_viz"]
    return getattr(vizclass, "eqn")(t)


def eqndx(t : Expr, parents : List[Expr]) -> List[str]:
    """Perform a dynamic dispatch to X_viz.eqndx() for node type X"""
    if parents is None:
        return [
            fraction("∂y", f"{'∂'+sub('v',t.vi)}"),
            fraction("∂y", "∂y"),
            "",
            "1"
        ]
    vizclass = globals()[t.__class__.__name__ + "_viz"]
    return getattr(vizclass, "eqndx")(t, parents)


def eqndvdv(t : BinaryOp, wrt : Expr) -> List[str]:
    """Give equation for dv/dv"""
    vizclass = globals()[t.__class__.__name__ + "_viz"]
    return getattr(vizclass, "eqndvdv")(t, wrt)


class Var_viz:
    @staticmethod
    def eqn(t : Var) -> List[str]:
        if t.varname is not None:
            return [f"{sub('v',t.vi)}", f"{t.varname}", round(t.value())]
        else:
            return [f"{sub('v',t.vi)}", "", round(t.value())]

    @staticmethod
    def eqndvdv(t: Var, wrt: Expr) -> List[str]:
        return None

    @staticmethod
    def eqndx(t : Var, parents : List[Expr]) -> List[str]:
        # collect contributions from all parents
        contribs = []
        contribs_values = []
        for p in parents:
            if len(contribs)>0:
                contribs.append(" + ")
            contribs.append(fraction("∂y", f"{sub('∂v',p.vi)}"))
            contribs.append(" &times; ")
            contribs.append(fraction(f"{sub('∂v',p.vi)}", f"{sub('∂v',t.vi)}"))

            if len(contribs_values)>0:
                contribs_values.append(" + ")
            contribs_values.append(str(round(p.dydv)))
            contribs_values.append(" &times; ")
            contribs_values.append(str(round(p.dvdv(t))))

        return [fraction("∂y", f"{'∂'+t.varname}"),
                seq(*contribs),
                seq(*contribs_values),
                round(t.dydv)]


class Const_viz:
    @staticmethod
    def eqn(t : Const) -> List[str]:
        return [f"{sub('v',t.vi)}", "", round(t.value())]

    @staticmethod
    def eqndvdv(t: Var, wrt: Expr) -> List[str]:
        return None

    @staticmethod
    def eqndx(t : Const, parents : List[Expr]) -> List[str]:
        return [fraction("∂y", f"{sub('∂v',t.vi)}"),
                "",
                round(t.dydv)]


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

    @staticmethod
    def eqndx(t : BinaryOp, parents : List[Expr]) -> List[str]:
        return [
            fraction("∂y", f"{'∂'+sub('v',t.vi)}"),
            seq(fraction("∂y", f"{'∂'+sub('v',parents[0].vi)}")," &times; ",
                fraction(f"{'∂'+sub('v',parents[0].vi)}", f"{'∂'+sub('v',t.vi)}")),
            f"{parents[0].dydv} &times; {eqndvdv(parents[0],t)}",
            round(parents[0].dydv)
        ]


class UnaryOp_viz:
    @staticmethod
    def eqn(t : UnaryOp) -> List[str]:
        return [f"{sub('v',t.vi)}",
                f"{t.op}({sub('v',t.opnd.vi)})" if t.op.isalnum() else f"{t.op} {sub('v',t.opnd.vi)}",
                round(t.value())]

    @staticmethod
    def eqndx(t : UnaryOp, parents : List[Expr]) -> List[str]:
        return [
            fraction("∂y", f"{'∂'+sub('v',t.vi)}"),
            seq(fraction("∂y", f"{'∂'+sub('v',parents[0].vi)}")," &times; ",
                fraction(f"{'∂'+sub('v',parents[0].vi)}", f"{'∂'+sub('v',t.vi)}")),
            f"{parents[0].dydv} &times; {eqndvdv(parents[0],t)}",
            round(parents[0].dydv)
        ]


class Add_viz(BinaryOp_viz):
    @staticmethod
    def eqndvdv(t: Var, wrt: Expr) -> List[str]:
        return "1"


class Sub_viz(BinaryOp_viz):
    @staticmethod
    def eqndvdv(t: Var, wrt: Expr) -> List[str]:
        if t.left == wrt:
            return "1"
        else:
            return "-1"


class Mul_viz(BinaryOp_viz):
    @staticmethod
    def eqndvdv(t: Var, wrt: Expr) -> List[str]:
        if t.left == wrt:
            p = f"{sub('v',t.right.vi)}"
        else:
            p = f"{sub('v',t.left.vi)}"
        return p


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
    parentmap = parents(t)
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
            {nltab.join([nodeviz(node,parentmap[node]) for node in cluster])}
        }}\n"""
    s = f"""

    digraph G {{
        nodesep=.1;
        ranksep=.3;
        rankdir=TD;
        node [penwidth="0.5", shape=box, width=.1, height=.1];
        // OPERATORS
        {nltab.join([nodeviz(node,parentmap[node]) for node in the_nonleaves])}
        // CONSTANTS (not operand of binary op)
        {nltab.join([nodeviz(node,parentmap[node]) for node in [n for n in consts if n not in cluster_nodes]])}
        // OPERAND CLUSTERS
        {opnd_clusters}
        // INPUTS (leaves)
        subgraph cluster_inputs {{
            style=invis
            {nltab.join([nodeviz(node,parentmap[node]) for node in inputs])}
        }}
        // EDGES
        {nltab.join(connections)}
    }}
    """

    Var.VAR_COUNT = 1 # reset after visualization so next one has vars x1, x2, etc...

    return graphviz.Source(s)

def nodeviz(t : Expr, parent : Expr) -> str:
    color = GREEN if isinstance(t,Var) else YELLOW
    return f'v{t.vi} [color="{DARK_GREY}", margin="0.02", fontcolor="{textcolor}", fontsize="{fontsize}" fontname="Times-Italic", style=filled, fillcolor="{color}", label=<{nodehtml(t,parent)}>];'


def connviz(t : Expr, kid : Expr) -> str:
    return f'v{t.vi} -> v{kid.vi} [penwidth="0.5", color="{DARK_GREY}", arrowsize=.4]'


def nodehtml(t : Expr, parent : Expr) -> str:
    rows = []
    e = eqn(t)
    edx = eqndx(t, parent)
    if isinstance(t, Const):
        rows.append(f"""<tr><td>{e[0]}</td><td> = </td><td align="left">{e[2]}</td></tr>""")
        rows.append(
            f"""<tr><td>{edx[0]}</td><td> = </td><td align="left">{edx[2]}</td></tr>""")
    else:
        # EQN
        if t.isvar():
            rows.append(f"""
            <tr><td>{e[0]}</td><td> = </td><td align="left">{e[1]} = {e[2]}</td><td></td><td></td></tr>
            """)
        else:
            # rows.append(f"""
            # <tr><td>{" = ".join([str(x) for x in e])}</td></tr>
            # """)
            rows.append(f"""
            <tr><td>{e[0]}</td><td> = </td><td align="left">{e[1]}</td><td> = </td><td align="left">{e[2]}</td></tr>
            """)

        # EQNDX
        if parent is None:
            rows.append(f"""
            <tr><td>{edx[0]}</td><td> = </td><td align="left">{edx[1]}</td><td> = </td><td align="left">{edx[3]}</td></tr>
            """)
        else:
            rows.append(f"""
            <tr><td>{edx[0]}</td><td> = </td><td align="left">{edx[1]}</td><td> = </td><td align="left">{seq(edx[2], " = ", edx[3])}</td></tr>
            """)

    return f"""<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="1">
    {''.join(rows)}
    </table>
    """

if __name__ == '__main__':
    x1 = Var(2)
    x2 = Var(5)
    y = x1 - x1 * x2

    ast = x1 * x2 - sin(x2)
    set_var_indices(y,1)

    # compute gradients in leaves
    y = ast.forward()
    ast.backward()
    foo = [x.dydv for x in [x1,x2]]

    g = astviz(ast)
    print(g.source)
    f = g.view()
    dot(g,filename="/tmp/t.png",format='png',dpi=600)

    #
    # x1 = Var(2, sub("x",1))
    # x2 = Var(5, sub("x",2))
    # y = ln(x1) + x1 * x2 - sin(x2) * 9
    # g = astviz(y, x1)
    # print(g.source)
    # g.view()
