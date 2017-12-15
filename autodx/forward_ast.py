import numpy as np
import numbers

class Expr:
    def __init__(self, x : numbers.Number):
        self.x = x

    def value(self) -> numbers.Number:
        return self.x

    def dvdx(self, wrt : 'Expr') -> numbers.Number:
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
            return f'Var({self.x})'
        return f'Var({self.x:.4f})'

    def __repr__(self):
        return str(self)


class BinaryOp(Expr):
    def __init__(self, left : Expr, op: str, right : Expr):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def __repr__(self):
        return str(self)


class UnaryOp(Expr):
    def __init__(self, op : str, opnd : Expr):
        self.opnd = opnd
        self.op = op

    def __str__(self):
        return f"{self.op}({self.opnd})"

    def __repr__(self):
        return str(self)


class Add(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '+', right)

    def value(self):
        return self.left.value() + self.right.value()

    def dvdx(self, wrt : 'Expr') -> numbers.Number:
        return self.left.dvdx(wrt) + self.right.dvdx(wrt)


class Sub(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '-', right)

    def value(self):
        return self.left.value() - self.right.value()

    def dvdx(self, wrt : 'Expr') -> numbers.Number:
        return self.left.dvdx(wrt) - self.right.dvdx(wrt)


class Mul(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '*', right)

    def value(self):
        return self.left.value() * self.right.value()

    def dvdx(self, wrt : 'Expr') -> numbers.Number:
        return self.left.value() * self.right.dvdx(wrt) + \
               self.right.value() * self.left.dvdx(wrt)


class Div(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '/', right)

    def value(self):
        return self.left.value() / self.right.value()

    def dvdx(self, wrt : 'Expr') -> numbers.Number:
        return self.left.value() / self.right.dvdx(wrt) + \
               self.right.value() / self.left.dvdx(wrt)


class Sin(UnaryOp):
    def __init__(self, opnd):
        super().__init__('sin', opnd)

    def value(self):
        return np.sin(self.opnd.value())

    def dvdx(self, wrt : 'Expr') -> numbers.Number:
        return np.cos(self.opnd.value()) * self.opnd.dvdx(wrt)


def sin(x:Expr) -> Sin:
    return Sin(x)