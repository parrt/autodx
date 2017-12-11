import numpy as np
import numbers

class Variable:
    def __init__(self, x : numbers.Number):
        self.x = x
        self.parent = None

    def forward(self) -> numbers.Number:
        """
        Compute and return value of expression tree; squirrel away subexpression values
        as self.x in each subtree root.
        """
        return self.x

    def backward(self) -> None:
        pass

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return 1 if self==wrt else 0

    def __add__(self, other):
        if isinstance(other, numbers.Number):
            other = Variable(other)
        return Add(self,other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, numbers.Number):
            other = Variable(other)
        return Sub(self,other)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other: 'Variable') -> 'Variable':  # yuck. must put 'Variable' type in string
        if isinstance(other, numbers.Number):
            other = Variable(other)
        return Mul(self,other)

    def __rmul__(self, other):
        "Allows 5 * Variable(3) to invoke overloaded * operator"
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            other = Variable(other)
        return Div(self,other)

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __str__(self):
        if isinstance(self.x, int):
            return f'Var({self.x})'
        return f'Var({self.x:.4f})'

    def __repr__(self):
        return str(self)


class BinaryOp(Variable):
    def __init__(self, left : Variable, op: str, right : Variable):
        left.parent = self
        right.parent = self
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def __repr__(self):
        return str(self)


class UnaryOp(Variable):
    def __init__(self, op : str, opnd : Variable):
        opnd.parent = self
        self.opnd = opnd
        self.op = op

    def __str__(self):
        return f"{self.op}({self.opnd})"

    def __repr__(self):
        return str(self)


class Add(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '+', right)

    def forward(self):
        self.x = self.left.forward() + self.right.forward()
        return self.x

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return self.left.partial(wrt) + self.right.partial(wrt)


class Sub(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '-', right)

    def forward(self):
        self.x = self.left.forward() - self.right.forward()
        return self.x

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return self.left.partial(wrt) - self.right.partial(wrt)


class Mul(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '*', right)

    def forward(self):
        self.x = self.left.forward() * self.right.forward()
        return self.x

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return self.left.forward() * self.right.partial(wrt) + \
               self.right.forward() * self.left.partial(wrt)


class Div(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '/', right)

    def forward(self):
        self.x = self.left.forward() / self.right.forward()
        return self.x

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return self.left.forward() / self.right.partial(wrt) + \
               self.right.forward() / self.left.partial(wrt)


class Sin(UnaryOp):
    def __init__(self, opnd):
        super().__init__('sin', opnd)

    def forward(self):
        self.x = np.sin(self.opnd.forward())
        return self.x

    def partial(self,wrt : 'Variable') -> numbers.Number:
        return np.cos(self.opnd.forward()) * self.opnd.partial(wrt)


def sin(x:Variable) -> Sin:
    return Sin(x)