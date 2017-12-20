from typing import List

import numpy as np
import numbers
import graphviz

YELLOW = "#fefecd" # "#fbfbd0" # "#FBFEB0"
BLUE = "#D9E6F5"
GREEN = "#cfe2d4"

class Expr:
    def __init__(self, x : numbers.Number = 0, varname=None):
        self.x = x
        self.vi = -1
        self.varname = varname

    def value(self) -> numbers.Number:
        return self.x

    def dvdx(self, wrt : 'Expr') -> numbers.Number:
        return 1 if self==wrt else 0

    def __add__(self, other):
        if isinstance(other, numbers.Number):
            other = Const(other)
        return Add(self,other)

    def __radd__(self, other):
        return Add(Const(other),self) # other comes in as left operand so we flip order

    def __sub__(self, other):
        if isinstance(other, numbers.Number):
            other = Const(other)
        return Sub(self,other)

    def __rsub__(self, other):
        return Sub(Const(other),self) # other comes in as left operand so we flip order

    def __mul__(self, other: 'Expr') -> 'Expr':  # yuck. must put 'Variable' type in string
        if isinstance(other, numbers.Number):
            other = Const(other)
        return Mul(self,other)

    def __rmul__(self, other):
        "Allows 5 * Variable(3) to invoke overloaded * operator"
        return Mul(Const(other),self) # other comes in as left operand so we flip order

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            other = Const(other)
        return Div(self,other)

    def __rtruediv__(self, other):
        return Div(Const(other),self) # other comes in as left operand so we flip order

    def gradient(self, X):
        return [self.dvdx(x) for x in X]

    def set_var_indices(self, vi : int = 0):
        if self.vi<0:
            self.vi = vi
            return self.vi + 1
        return vi

    def eqn(self) -> List[str]:
        if self.varname is not None:
            return [f"v<sub>{self.vi}</sub>", f"{self.varname}", round(self.value())]
        else:
            return [f"v<sub>{self.vi}</sub>", "", round(self.value())]

    def eqndx(self, wrt : 'Expr') -> List[str]:
        result = 1 if self==wrt else 0
        if wrt.varname is not None and self.varname is not None:
            return [partial_html(f"∂v<sub>{self.vi}</sub>", f"∂{wrt.varname}"),
                    partial_html(f"∂{self.varname}", f"∂{wrt.varname}"),
                    result]
        if wrt.varname is not None and self.varname is None: # must be constant
            return [partial_html(f"∂v<sub>{self.vi}</sub>", f"∂{wrt.varname}"),
                    "",
                    result]
        else:
            return [partial_html(f"∂v<sub>{self.vi}</sub>", f"∂v<sub>{wrt.vi}</sub>"), "", result]

    def children(self):
        return []

    def __str__(self):
        if isinstance(self.x, int):
            return f'Var({self.x})'
        return f'Var({self.x:.4f})'

    def __repr__(self):
        return str(self)


class Const(Expr):
    def __init__(self, v : numbers.Number):
        self.x = v
        self.vi = -1
        self.varname = None

    def __str__(self):
        if isinstance(self.x, int):
            return f'{self.x}'
        else:
            return f'{round(self.x)}'

    def eqn(self) -> List[str]:
        return [f"v<sub>{self.vi}</sub>", "", round(self.value())]

    def eqndx(self, wrt : 'Expr') -> List[str]:
        result = 1 if self==wrt else 0
        if wrt.varname is not None:
            return [partial_html(f"∂v<sub>{self.vi}</sub>", f"∂{wrt.varname}"), "", result]
        else:
            return [partial_html(f"∂v<sub>{self.vi}</sub>", f"∂v<sub>{wrt.vi}</sub>"), "", result]


class BinaryOp(Expr):
    def __init__(self, left : Expr, op: str, right : Expr):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right

    def eqn(self):
        if self.op == '*':
            op = "&times;"
        elif self.op == '-':
            op = "&minus;"
        elif self.op == '/' :
            op = "&frasl;"
        else:
            op = self.op
        return [f"v<sub>{self.vi}</sub>",
                f"v<sub>{self.left.vi}</sub> {op} v<sub>{self.right.vi}</sub>",
                round(self.value())]

    def children(self):
        return [self.left, self.right]

    def set_var_indices(self, vi : int = 0) -> int:
        if self.vi<0:
            vi = self.left.set_var_indices(vi)
            vi = self.right.set_var_indices(vi)
            self.vi = vi
            return self.vi + 1
        return vi

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def __repr__(self):
        return str(self)


class UnaryOp(Expr):
    def __init__(self, op : str, opnd : Expr):
        super().__init__()
        self.opnd = opnd
        self.op = op

    def eqn(self):
        return [f"v<sub>{self.vi}</sub>",
                f"{self.op}(v<sub>{self.opnd.vi}</sub>)" if self.op.isalnum() else f"{self.op} v<sub>{self.opnd.vi}</sub>",
                round(self.value())]

    def children(self):
        return [self.opnd]

    def set_var_indices(self, vi : int = 0) -> int:
        if self.vi<0:
            self.vi = self.opnd.set_var_indices(vi)
            return self.vi + 1
        return vi

    def __str__(self):
        return f"{self.op}({self.opnd})"

    def __repr__(self):
        return str(self)


class Add(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '+', right)

    def value(self):
        return self.left.value() + self.right.value()

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return self.left.dvdx(wrt) + self.right.dvdx(wrt)

    def eqndx(self, wrt : 'Expr') -> List[str]:
        return [
            partial_html(f"∂v<sub>{self.vi}</sub>", f"∂{wrt.varname}"),
            f"∂v<sub>{self.left.vi}</sub> + ∂v<sub>{self.right.vi}</sub>",
            f"{round(self.left.dvdx(wrt))} + {round(self.right.dvdx(wrt))} = {round(self.dvdx(wrt))}"
        ]


class Sub(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '-', right)

    def value(self):
        return self.left.value() - self.right.value()

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return self.left.dvdx(wrt) - self.right.dvdx(wrt)

    def eqndx(self, wrt : 'Expr') -> List[str]:
        return [#f"∂v<sub>{self.vi}</sub>",
            partial_html(f"∂v<sub>{self.vi}</sub>", f"∂{wrt.varname}"),
            f"∂v<sub>{self.left.vi}</sub> &minus; ∂v<sub>{self.right.vi}</sub>",
            f"{round(self.left.dvdx(wrt))} &minus; {round(self.right.dvdx(wrt))} = {round(self.dvdx(wrt))}"
        ]


class Mul(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '*', right)

    def value(self):
        return self.left.value() * self.right.value()

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return self.left.value() * self.right.dvdx(wrt) + \
               self.right.value() * self.left.dvdx(wrt)

    def eqndx(self, wrt : 'Expr') -> List[str]:
        return [
            partial_html(f"∂v<sub>{self.vi}</sub>", f"∂{wrt.varname}"),
            f"v<sub>{self.left.vi}</sub> &times; ∂v<sub>{self.right.vi}</sub> + v<sub>{self.right.vi}</sub> &times; ∂v<sub>{self.left.vi}</sub>",
            f"{round(self.left.value() * self.right.dvdx(wrt))} + {round(self.right.value() * self.left.dvdx(wrt))} = {round(self.dvdx(wrt))}"]


class Div(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '/', right)

    def value(self):
        return self.left.value() / self.right.value()

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return (self.left.dvdx(wrt) * self.right.value() - self.left.value() * self.right.dvdx(wrt)) / \
               self.right.value()**2

    def eqndx(self, wrt : 'Expr') -> List[str]:
        return [
            partial_html(f"∂v<sub>{self.vi}</sub>", f"∂{wrt.varname}"),
            partial_html(f"v<sub>{self.right.vi}</sub> &times; ∂v<sub>{self.left.vi}</sub> &minus; v<sub>{self.left.vi}</sub> &times; ∂v<sub>{self.right.vi}</sub>", f"v<sub>{self.right.vi}</sub><sup>2</sup>"),
            '<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="1"><tr><td>'+
            partial_html(f"{round(self.right.value())} &times; {round(self.left.dvdx(wrt))} &minus; {round(self.left.value())} &times; {round(self.right.dvdx(wrt))}", f"{round(self.right.value())}<sup>2</sup>")+
            f"</td><td> = {round(self.dvdx(wrt))}</td></tr></table>",
            f"{round(self.left.value() * self.right.dvdx(wrt))} + {round(self.right.value() * self.left.dvdx(wrt))} = {round(self.dvdx(wrt))}"]


class Sin(UnaryOp):
    def __init__(self, opnd):
        super().__init__('sin', opnd)

    def value(self):
        return np.sin(self.opnd.value())

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return np.cos(self.opnd.value()) * self.opnd.dvdx(wrt)

    def eqndx(self, wrt : 'Expr') -> List[str]:
        return [
            partial_html(f"∂v<sub>{self.vi}</sub>", f"∂{wrt.varname}"),
            f"cos(v<sub>{self.opnd.vi}</sub>) &times; ∂v<sub>{self.opnd.vi}</sub>",
            f"cos({round(self.opnd.value())}) &times; {round(self.opnd.dvdx(wrt))} = {round(self.dvdx(wrt))}"]


class Ln(UnaryOp):
    def __init__(self, opnd):
        super().__init__('ln', opnd)

    def value(self):
        return np.log(self.opnd.value())

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return (1 / self.opnd.value()) * self.opnd.dvdx(wrt)

    def eqndx(self, wrt : 'Expr') -> List[str]:
        return [
            partial_html(f"∂v<sub>{self.vi}</sub>", f"∂{wrt.varname}"),
            f"(1 &frasl; v<sub>{self.opnd.vi}</sub>) &times; ∂v<sub>{self.opnd.vi}</sub>",
            f"(1 &frasl; {round(self.opnd.value())}) &times; {round(self.opnd.dvdx(wrt))} = {round(self.dvdx(wrt))}"]


def sin(x:Expr) -> Sin:
    return Sin(x)


def ln(x:Expr) -> Ln:
    return Ln(x)


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
            nonvarleaf_kids = [n for n in node.children() if n.varname is None and not isinstance(n,Const)]
            if len(nonvarleaf_kids)>1:
                clusters += [nonvarleaf_kids] # track nonleaf children groups so we can make clusters
    return the_nonleaves, clusters


def leaves(t : Expr) -> List[Expr]:
    """Return preorder list of nodes from ast t"""
    the_leaves = []
    work = [t]
    while len(work)>0:
        node = work.pop(0)
        if len(node.children())==0:
            the_leaves.append(node)
        else:
            work += node.children()
    return the_leaves


def astviz(t : Expr, wrt : Expr) -> graphviz.Source:
    "I had to do $ brew install graphviz --with-pango to get the cairo support for <sub>"
    t.set_var_indices(0)
    the_leaves = leaves(t)
    the_nonleaves, clusters = nonleaves(t)
    consts = [n for n in the_leaves if isinstance(n,Const)]
    inputs = [n for n in the_leaves if not n in consts]
    connections = []
    for node in the_leaves + the_nonleaves:
        connections += [connviz(node, kid) for kid in node.children()]
    opnd_clusters = ""
    nltab = "\n\t"
    for i,cluster in enumerate(clusters):
        opnd_clusters += f"""
            subgraph cluster_opnds{i} {{
            style=invis
            {nltab.join([nodeviz(node,wrt) for node in cluster])}
        }}\n"""
    s = f"""
    digraph G {{
        nodesep=.1;
        ranksep=.3;
        rankdir=TD;
        node [penwidth="0.5", shape=box, width=.1, height=.1];
        {nltab.join([nodeviz(node,wrt) for node in the_nonleaves])}
        {nltab.join([nodeviz(node,wrt) for node in consts])}
        {opnd_clusters}
        subgraph cluster_inputs {{
            style=invis
            {nltab.join([nodeviz(node,wrt) for node in inputs])}
        }}
        {nltab.join(connections)}
    }}
    """

    return graphviz.Source(s)

def nodeviz(t : Expr, wrt : Expr) -> str:
    color = GREEN if t.varname is not None else YELLOW
    return f'v{t.vi} [color="#444443", margin="0.02", fontcolor="#444443", fontname="Times-Italic", style=filled, fillcolor="{color}", label=<{nodehtml(t,wrt)}>];'


def connviz(t : Expr, kid : Expr) -> str:
    return f'v{t.vi} -> v{kid.vi} [penwidth="0.5", color="#444443", arrowsize=.4]'


def nodehtml(t : Expr, wrt : Expr) -> str:
    rows = []
    eqn = t.eqn()
    if isinstance(t, Const):
        rows.append(f"""<tr><td>{eqn[0]}</td><td> = </td><td align="left">{eqn[2]}</td></tr>""")
        if wrt is not None:
            eqndx = t.eqndx(wrt)
            rows.append(
                f"""<tr><td>{eqndx[0]}</td><td> = </td><td align="left">{eqndx[2]}</td></tr>""")
    else:
        if len(eqn)==1:
            rows.append(f"""
            <tr><td>{eqn[0]}</td><td> = </td><td align="left">{eqn[1]}</td><td> = </td><td align="left">{eqn[2]}</td></tr>
            """)
        else:
            rows.append(f"""
            <tr><td>{eqn[0]}</td><td> = </td><td align="left">{eqn[1]}</td><td> = </td><td align="left">{eqn[2]}</td></tr>
            """)

        if wrt is not None:
            eqndx = t.eqndx(wrt)
            if len(eqndx)==1:
                rows.append(f"""
                <tr><td>{eqndx[0]}</td><td></td><td></td><td>=</td><td></td></tr>
                """)
            else:
                rows.append(f"""
                <tr><td>{eqndx[0]}</td><td> = </td><td align="left">{eqndx[1]}</td><td>=</td><td align="left">{eqndx[2]}</td></tr>
                """)

    return f"""<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="1">
    {''.join(rows)}
    </table>
    """

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


if __name__ == '__main__':
    x1 = Expr(2, "x<sub>1</sub>")
    x2 = Expr(5, "x<sub>2</sub>")
    y = ln(x1) + x1 * x2 - sin(x2)
    g = astviz(y, x1)
    print(g.source)
    g.view()