import numpy as np
import numbers

VAR_COUNT = -1

class Variable:
    def __init__(self, x : numbers.Number = None):
        global VAR_COUNT
        self.vi = VAR_COUNT
        VAR_COUNT += 1
        if x is None:
            x = 0
        self.x = x
        self.adjoint = 0
        self.parent = None

    def forward(self) -> numbers.Number:
        """
        Compute and return value of expression tree; squirrel away subexpression values
        as self.x in each subtree root.

        This specific method is used to compute the value of a leaf node.
        """
        return self.x

    # def backward(self, parent_adjoint : numbers.Number = 1) -> None:
    def backward(self) -> None:
        if self.parent is None:
            # Root node dy/dy is 1
            self.adjoint = 1
        else:
            # actual variable leaf nodes must accumulate all contributions
            # of this var up the tree. Sum all dy/dx_i computed backwards.
            self.adjoint += self.parent.adjoint * self.parent.partial(self)

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
            return f'v{self.vi}({self.x})'
        return f'v{self.vi}({self.x:.4f})'

    def __repr__(self):
        return str(self)


class BinaryOp(Variable):
    def __init__(self, left : Variable, op: str, right : Variable):
        super().__init__()
        left.parent = self
        right.parent = self
        self.left = left
        self.op = op
        self.right = right

    def backward(self) -> None:
        if self.parent is None:
            self.adjoint = 1
        else:
            self.adjoint = self.parent.adjoint * self.parent.partial(self) # don't need to accum subexpr adjoints (they are unique)
        self.left.backward()
        self.right.backward()

    def __str__(self):
        return f"v{self.vi}:({self.left} {self.op} {self.right})"

    def __repr__(self):
        return str(self)


class UnaryOp(Variable):
    def __init__(self, op : str, opnd : Variable):
        super().__init__()
        opnd.parent = self
        self.opnd = opnd
        self.op = op

    def backward(self) -> None:
        if self.parent is None:
            self.adjoint = 1
        else:
            self.adjoint = self.parent.adjoint * self.parent.partial(self) # don't need to accum subexpr adjoints (they are unique)
        self.opnd.backward()

    def __str__(self):
        return f"v{self.vi}:{self.op}({self.opnd})"

    def __repr__(self):
        return str(self)


class Add(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '+', right)

    def forward(self):
        self.x = self.left.forward() + self.right.forward()
        return self.x

    def partial(self,wrt : 'Variable') -> numbers.Number:
        p = 1
        print(f"partial dv{self.vi}/dv{wrt.vi} {wrt} of {self} = {p}")
        return p


class Sub(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '-', right)

    def forward(self):
        self.x = self.left.forward() - self.right.forward()
        return self.x

    def partial(self,wrt : 'Variable') -> numbers.Number:
        if self.left == wrt:
            p = 1
        else:
            p = -1
        print(f"partial dv{self.vi}/dv{wrt.vi} of {self} = {p}")
        return p


class Mul(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '*', right)

    def forward(self):
        self.x = self.left.forward() * self.right.forward()
        return self.x

    def partial(self,wrt : 'Variable') -> numbers.Number:
        if self.left == wrt:
            p = self.right.forward()
        else:
            p = self.left.forward()
        print(f"partial dv{self.vi}/dv{wrt.vi} of {self} = {p}")
        return p


class Div(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '/', right)

    def forward(self):
        self.x = self.left.forward() / self.right.forward()
        return self.x

    def partial(self,wrt : 'Variable') -> numbers.Number:
        if self.left == wrt:
            p = 1 / self.right.forward()
        else:
            p = - self.left.forward() * (1 / self.right.forward()**2)
        print(f"partial dv{self.vi}/dv{wrt.vi} of {self} = {p}")
        return p

class Sin(UnaryOp):
    def __init__(self, opnd):
        super().__init__('sin', opnd)

    def forward(self):
        self.x = np.sin(self.opnd.forward())
        return self.x

    def partial(self,wrt : 'Variable') -> numbers.Number:
        if self.opnd == wrt:
            p = np.cos(self.opnd.forward())
        else:
            p = 0
        print(f"partial dv{self.vi}/dv{wrt.vi} of {self} = {p}")
        return p


class Ln(UnaryOp):
    def __init__(self, opnd):
        super().__init__('ln', opnd)

    def forward(self):
        self.x = np.log(self.opnd.forward())
        return self.x

    def partial(self,wrt : 'Variable') -> numbers.Number:
        p = 1 / self.opnd.forward() if self.opnd == wrt else 0
        print(f"partial wrt {wrt} of {self} = {p}")
        return p


def sin(x:Variable) -> Sin:
    return Sin(x)


def ln(x : Variable) -> Ln:
    return Ln(x)