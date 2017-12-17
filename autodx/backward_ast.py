import numpy as np
import numbers

VAR_COUNT = -1

class Expr:
    def __init__(self, x : numbers.Number = None):
        # global VAR_COUNT
        # self.vi = VAR_COUNT
        # VAR_COUNT += 1
        self.vi = -1
        if x is None:
            x = 0
        self.x = x
        self.dydv = 0

    def forward(self) -> numbers.Number:
        """
        Compute and return value of expression tree; squirrel away subexpression values
        as self.x in each subtree root.

        This specific method is used to compute the value of a leaf node.
        """
        return self.x

    def backward(self, dy_dvi : numbers.Number, dvi_dvj : numbers.Number) -> None:
        print(f"backward(v{self.vi} = {self.asvar()})")
        # actual variable leaf nodes must accumulate all contributions
        # of this var from up the tree. Sum all dy/dx_i computed backwards.
        t = dy_dvi * dvi_dvj
        print(f"Adding {t} to v{self.vi} ({self.dydv})")
        self.dydv += t
        print(f"adjoint v{self.vi} = {self.dydv}")

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
        return 1 if self==wrt else 0

    def __add__(self, other):
        if isinstance(other, numbers.Number):
            other = Expr(other)
        return Add(self,other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, numbers.Number):
            other = Expr(other)
        return Sub(self,other)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other: 'Expr') -> 'Expr':  # yuck. must put 'Variable' type in string
        if isinstance(other, numbers.Number):
            other = Expr(other)
        return Mul(self,other)

    def __rmul__(self, other):
        "Allows 5 * Variable(3) to invoke overloaded * operator"
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            other = Expr(other)
        return Div(self,other)

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __str__(self):
        if isinstance(self.x, int):
            return f'v{self.vi}({self.x})'
        return f'v{self.vi}({self.x:.4f})'

    def __repr__(self):
        return str(self)

    def asvar(self):
        return f"v{self.vi}"

    def forward_trace(self):
        return [f"v{self.vi} = {self.x}"]

    def set_var_indices(self, vi : int = 0):
        if self.vi<0:
            self.vi = vi
            return self.vi + 1
        return vi


class Operator(Expr):
    def __init__(self):
        super().__init__()


class BinaryOp(Operator):
    def __init__(self, left : Expr, op: str, right : Expr):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right

    def backward(self, dy_dvi : numbers.Number, dvi_dvj : numbers.Number) -> None:
        print(f"backward(v{self.vi} = {self.asvar()})")
        self.adjoint = dy_dvi * dvi_dvj # don't need to accum subexpr adjoints (they are unique)
        print(f"adjoint v{self.vi} = {self.adjoint}")
        self.left.backward(self.adjoint, self.dvdv(self.left))
        self.right.backward(self.adjoint, self.dvdv(self.right))

    def forward_trace(self):
        return self.left.forward_trace() + self.right.forward_trace() + [f"v{self.vi} = {self.asvar()}"]

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def __repr__(self):
        return str(self)

    def asvar(self):
        return f"v{self.left.vi} {self.op} v{self.right.vi}"

    def dbg(self,wrt,p):
        print(f"partial ∂v{self.vi}/∂v{wrt.vi} of {self.asvar()} = {p}")
        print(f"\tv{self.vi} = {self.asvar()} = {self}")
        print(f"\tv{self.left.vi} = {self.left.x}")
        print(f"\tv{self.right.vi} = {self.right.x}")

    def set_var_indices(self, vi : int = 0) -> int:
        if self.vi<0:
            vi = self.left.set_var_indices(vi)
            vi = self.right.set_var_indices(vi)
            self.vi = vi
            return self.vi + 1
        return vi


class UnaryOp(Operator):
    def __init__(self, op : str, opnd : Expr):
        super().__init__()
        self.opnd = opnd
        self.op = op

    def backward(self, dy_dvi : numbers.Number, dvi_dvj : numbers.Number) -> None:
        print(f"backward(v{self.vi} = {self.asvar()})")
        self.adjoint = dy_dvi * dvi_dvj # don't need to accum subexpr adjoints (they are unique)
        print(f"adjoint v{self.vi} = {self.adjoint}")
        self.opnd.backward(self.adjoint, self.dvdv(self.opnd))

    def forward_trace(self):
        return self.opnd.forward_trace() + [f"v{self.vi} = {self.asvar()}"]

    def __str__(self):
        return f"{self.op}({self.opnd})"

    def __repr__(self):
        return str(self)

    def asvar(self):
        return f"{self.op} v{self.opnd.vi}"

    def dbg(self,wrt,p):
        print(f"partial ∂v{self.vi}/∂v{wrt.vi} of {self.asvar()} = {p}")
        print(f"\tv{self.vi} = {self.asvar()} = {self}")
        if isinstance(wrt, Operator):
            print(f"\tv{wrt.vi} = {wrt.asvar()} = {wrt.x}")
        else:
            print(f"\tv{wrt.vi} = {wrt.x}")

    def set_var_indices(self, vi : int = 0) -> int:
        if self.vi<0:
            self.vi = self.opnd.set_var_indices(vi)
            return self.vi + 1
        return vi


class Add(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '+', right)

    def forward(self):
        self.x = self.left.forward() + self.right.forward()
        return self.x

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
        p = 1
        self.dbg(wrt,p)
        return p


class Sub(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '-', right)

    def forward(self):
        self.x = self.left.forward() - self.right.forward()
        return self.x

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
        if self.left == wrt:
            p = 1
        else:
            p = -1
        self.dbg(wrt,p)
        return p


class Mul(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '*', right)

    def forward(self):
        self.x = self.left.forward() * self.right.forward()
        return self.x

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
        if self.left == wrt:
            p = self.right.x
        else:
            p = self.left.x
        self.dbg(wrt,p)
        return p


class Div(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '/', right)

    def forward(self):
        self.x = self.left.forward() / self.right.forward()
        return self.x

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
        if self.left == wrt:
            p = 1 / self.right.forward()
        else:
            p = - self.left.forward() * (1 / self.right.forward()**2)
        self.dbg(wrt,p)
        return p


class Sin(UnaryOp):
    def __init__(self, opnd):
        super().__init__('sin', opnd)

    def forward(self):
        self.x = np.sin(self.opnd.forward())
        return self.x

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
        if self.opnd == wrt:
            p = np.cos(self.opnd.forward())
        else:
            p = 0
        self.dbg(wrt,p)
        return p


class Ln(UnaryOp):
    def __init__(self, opnd):
        super().__init__('ln', opnd)

    def forward(self):
        self.x = np.log(self.opnd.forward())
        return self.x

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
        p = 1 / self.opnd.x if self.opnd == wrt else 0
        self.dbg(wrt,p)
        return p


def sin(x:Expr) -> Sin:
    return Sin(x)


def ln(x : Expr) -> Ln:
    return Ln(x)