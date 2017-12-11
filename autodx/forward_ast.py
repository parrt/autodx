import numpy as np
import numbers

class Variable:
    def __init__(self, x : numbers.Number):
        self.x = x

    def value(self) -> numbers.Number:
        return self.x

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return 1 if self==wrt else 0

    def __add__(self, other):
        return Add(self,other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return Sub(self,other)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other: 'Variable') -> 'Value':  # yuck. must put 'Variable' type in string
        return Mul(self,other)

    def __rmul__(self, other):
        "Allows 5 * Variable(3) to invoke overloaded * operator"
        return self.__mul__(other)

    def __truediv__(self, other):
        return Div(self,other)

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __str__(self):
        if isinstance(self.x, int):
            return f'Var({self.x})'
        return f'Var({self.x:.4f})'

    def __repr__(self):
        return str(self)


class Value(Variable):
    "A Value is the value of a subexpression result (temporary variable)"
    def __init__(self, x, dx=None):
        super().__init__(0)
        self.dx = 0

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return 0

    def __str__(self):
        return f"(x={self.x}, dx={self.dx})"

    def __repr__(self):
        return str(self)


class BinaryOp(Value):
    def __init__(self, left : Variable, op: str, right : Variable):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def __repr__(self):
        return str(self)


class UnaryOp(Value):
    def __init__(self, op : str, opnd : Variable):
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

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return self.left.partial(wrt) + self.right.partial(wrt)


class Sub(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '-', right)

    def value(self):
        return self.left.value() - self.right.value()

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return self.left.partial(wrt) - self.right.partial(wrt)


class Mul(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '*', right)

    def value(self):
        return self.left.value() * self.right.value()

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return self.left.value() * self.right.partial(wrt) + \
               self.right.value() * self.left.partial(wrt)


class Div(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '/', right)

    def value(self):
        return self.left.value() / self.right.value()

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return self.left.value() / self.right.partial(wrt) + \
               self.right.value() / self.left.partial(wrt)


class Sin(UnaryOp):
    def __init__(self, opnd):
        super().__init__('sin', opnd)

    def value(self):
        return np.sin(self.opnd.value())

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return np.cos(self.opnd.value()) * self.opnd.partial(wrt)


def sin(x:Variable) -> Value:
    return Sin(x)