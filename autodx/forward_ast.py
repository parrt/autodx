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
            other = Expr(other)
        return Add(self,other)

    def __radd__(self, other):
        return Add(Expr(other),self) # other comes in as left operand so we flip order

    def __sub__(self, other):
        if isinstance(other, numbers.Number):
            other = Expr(other)
        return Sub(self,other)

    def __rsub__(self, other):
        return Sub(Expr(other),self) # other comes in as left operand so we flip order

    def __mul__(self, other: 'Expr') -> 'Expr':  # yuck. must put 'Variable' type in string
        if isinstance(other, numbers.Number):
            other = Expr(other)
        return Mul(self,other)

    def __rmul__(self, other):
        "Allows 5 * Variable(3) to invoke overloaded * operator"
        return Mul(Expr(other),self) # other comes in as left operand so we flip order

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            other = Expr(other)
        return Div(self,other)

    def __rtruediv__(self, other):
        return Div(Expr(other),self) # other comes in as left operand so we flip order

    def gradient(self, X):
        return [self.dvdx(x) for x in X]

    def set_var_indices(self, vi : int = 0):
        if self.vi<0:
            self.vi = vi
            return self.vi + 1
        return vi

    def eqn(self) -> List[str]:
        if self.varname is not None:
            return [f"v<sub>{self.vi}</sub>", f"{self.varname}", self.value()]
        else:
            return [f"v<sub>{self.vi}</sub>", "", self.value()]

    def eqndx(self, wrt : 'Expr') -> List[str]:
        result = 1 if self==wrt else 0
        if wrt.varname is not None:
            return [partial_html(f"∂v<sub>{self.vi}</sub>", f"∂{wrt.varname}"),
                    partial_html(f"∂{self.varname}", f"∂{wrt.varname}"),
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


class BinaryOp(Expr):
    def __init__(self, left : Expr, op: str, right : Expr):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right

    def eqn(self):
        op = "&times;" if self.op=='*' else self.op
        return [f"v<sub>{self.vi}</sub>",
                f"v<sub>{self.left.vi}</sub> {op} v<sub>{self.right.vi}</sub>",
                self.value()]

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
        return [f"{self.vi}",
                f"{self.op} v{self.opnd.vi}",
                self.value()]

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
        return [#f"∂v<sub>{self.vi}</sub>",
            partial_html(f"∂v<sub>{self.vi}</sub>", f"∂v<sub>{wrt.vi}</sub>"),
            f"∂v<sub>{self.left.vi}</sub> + ∂v<sub>{self.right.vi}</sub>",
            f"{self.left.dvdx(wrt)} + {self.right.dvdx(wrt)} = {self.dvdx(wrt)}"
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
            partial_html(f"∂v<sub>{self.vi}</sub>", f"∂v<sub>{wrt.vi}</sub>"),
            f"∂v<sub>{self.left.vi}</sub> - ∂v<sub>{self.right.vi}</sub>",
            self.dvdx(wrt)
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
            partial_html(f"∂v<sub>{self.vi}</sub>", f"∂v<sub>{wrt.vi}</sub>"),
            f"v<sub>{self.left.vi}</sub> &times; ∂v<sub>{self.right.vi}</sub> + v<sub>{self.right.vi}</sub> &times; ∂v<sub>{self.left.vi}</sub>",
            f"{self.left.value() * self.right.dvdx(wrt)} + {self.right.value() * self.left.dvdx(wrt)} = {self.dvdx(wrt)}"]


class Div(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '/', right)

    def value(self):
        return self.left.value() / self.right.value()

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return (self.left.dvdx(wrt) * self.right.value() - self.left.value() * self.right.dvdx(wrt)) / \
               self.right.value()**2


class Sin(UnaryOp):
    def __init__(self, opnd):
        super().__init__('sin', opnd)

    def value(self):
        return np.sin(self.opnd.value())

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return np.cos(self.opnd.value()) * self.opnd.dvdx(wrt)


class Ln(UnaryOp):
    def __init__(self, opnd):
        super().__init__('ln', opnd)

    def value(self):
        return np.log(self.opnd.value())

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return (1 / self.opnd.value()) * self.opnd.dvdx(wrt)


def sin(x:Expr) -> Sin:
    return Sin(x)


def ln(x:Expr) -> Ln:
    return Ln(x)


def nodes(t : Expr) -> List[Expr]:
    """Return preorder list of nodes from ast t"""
    all = []
    work = [t]
    while len(work)>0:
        node = work.pop(0)
        all.append(node)
        work += node.children()
    return list(all)


def astviz(t : Expr, wrt : Expr) -> graphviz.Source:
    "I had to do $ brew install graphviz --with-pango to get the cairo support for <sub>"
    t.set_var_indices(0)
    all = nodes(t)
    connections = []
    for node in all:
        connections += [connviz(node, kid) for kid in node.children()]
    nl = "\n"
    nltab = "\n\t"
    s = f"""
    digraph G {{
        nodesep=.1;
        ranksep=.3;
        rankdir=TD;
        node [penwidth="0.5", shape=box, width=.1, height=.1];
        {nltab.join([nodeviz(node,wrt) for node in all])}
        {nltab.join(connections)}
    }}
    """

    return graphviz.Source(s)

def nodeviz(t : Expr, wrt : Expr) -> str:
    return f'v{t.vi} [color="#444443", margin="0.02", fontcolor="#444443", fontname="Times-Italic", style=filled, fillcolor="{YELLOW}", label=<{nodehtml(t,wrt)}>];'


def connviz(t : Expr, kid : Expr) -> str:
    return f'v{t.vi} -> v{kid.vi} [penwidth="0.5", color="#444443", arrowsize=.4]'


def nodehtml(t : Expr, wrt : Expr) -> str:
    # partial = f'∂v<sub>{t.vi}</sub>/∂v<sub>{wrt.vi}</sub>'
#        <tr><td>{partial}&nbsp;</td><td>=</td><td></td></tr>

    eqn = t.eqn()
    rows = []
    if len(eqn)==1:
        rows.append(f"""
        <tr><td>{eqn[0]}</td><td> = </td><td align="left">{eqn[2]}</td><td> = </td><td align="left">{eqn[2]}</td></tr>
        """)
    else:
        rows.append(f"""
        <tr><td>{eqn[0]}</td><td> = </td><td align="left">{eqn[1]}</td><td> = </td><td align="left">{eqn[2]}</td></tr>
        """)

    eqndx = t.eqndx(wrt)
    if len(eqndx)==1:
        rows.append(f"""
        <tr><td>{eqndx[0]}</td><td></td><td></td><td>=</td><td></td></tr>
        """)
    else:
        rows.append(f"""
        <tr><td>{eqndx[0]}</td><td> = </td><td align="left">{eqndx[1]}</td><td>=</td><td align="left">{eqndx[2]}</td></tr>
        """)

    return f"""<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="0">
    {''.join(rows)}
    </table>
    """

def partial_html(top : str, bottom : str):
    return f"""<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="0">
        <tr><td cellspacing="0" cellpadding="0" border="1" sides="b">{top}</td></tr>
        <tr><td cellspacing="0" cellpadding="0">{bottom}</td></tr>
    </table>
    """


if __name__ == '__main__':
    x1 = Expr(3, "x<sub>1</sub>")
    x2 = Expr(4, "x<sub>2</sub>")
    y = x1 + x2 * x1
    g = astviz(y, x1)
    print(g.source)
    g.view()