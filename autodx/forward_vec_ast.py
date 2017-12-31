"""A version of forward_ast.py that supports vector addition and dot product."""

from autodx.support import *

YELLOW = "#fefecd" # "#fbfbd0" # "#FBFEB0"
BLUE = "#D9E6F5"
GREEN = "#cfe2d4"

class Expr:
    def __init__(self, x : numbers.Number = 0):
        self.x = x
        self.vi = -1
        self.varname = None

    def __add__(self, other):
        if isinstance(other, numbers.Number):
            other = Const(other)
        if other.x.size==1 and self.x.size>1:
            return Add(self, Expand(other, self.x.size))
        elif self.x.size==1 and other.x.size>1:
            return Add(Expand(self, other.x.size), other)
        return Add(self,other)

    def __radd__(self, other):
        return Const(other).__add__(self) # other comes in as left operand so we flip order

    def __sub__(self, other):
        if isinstance(other, numbers.Number):
            other = Const(other)
        return Sub(self,other)

    def __rsub__(self, other):
        return Const(other).__sub__(self)

    def __mul__(self, other: 'Expr') -> 'Expr':  # yuck. must put 'Variable' type in string
        if isinstance(other, numbers.Number):
            other = Const(other)
        return Mul(self,other)

    def __rmul__(self, other):
        "Allows 5 * Variable(3) to invoke overloaded * operator"
        return Const(other).__mul__(self)

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            other = Const(other)
        return Div(self,other)

    def __rtruediv__(self, other):
        return Const(other).__truediv__(self)

    def value(self) -> Union[numbers.Number,np.ndarray]:
        return self.x

    def gradient(self, X):
        return np.array([self.dvdx(x) for x in X])

    def children(self):
        return []

    def isleaf(self) -> bool:
        return False

    def isvar(self) -> bool:
        return False

    def __repr__(self):
        return str(self)

class Var(Expr):
    def __init__(self, x, varname : str = None):
        self.x = np.array(x) # ensure all vars are vector vars even if 1x1 (scalars)
        self.vi = -1
        self.varname = varname

    def isvar(self) -> bool:
        return True

    def isleaf(self) -> bool:
        return True

    def dvdx(self, wrt : 'Expr') -> Union[numbers.Number,np.ndarray]:
        if isinstance(self.x, np.ndarray) and self.x.size>1:
            if self==wrt:
                return np.ones(self.x.size, dtype=int)
            else:
                return np.zeros(self.x.size, dtype=int)

        return 1 if self==wrt else 0

    def __str__(self):
        if isinstance(self.x, int) or isinstance(self.x, np.ndarray):
            return f'Var({self.x})'
        return f'Var({self.x:.4f})'


class Const(Expr):
    def __init__(self, v : numbers.Number):
        self.x = np.array(v) # ensure all consts are vector consts even if 1x1 (scalars)
        self.vi = -1
        self.varname = None

    def isleaf(self) -> bool:
        return True

    def dvdx(self, wrt : 'Expr') -> numbers.Number:
        return 0

    def __str__(self):
        if isinstance(self.x, int):
            return f'{self.x}'
        else:
            return f'{round(self.x)}'


class BinaryOp(Expr):
    def __init__(self, left : Expr, op: str, right : Expr):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right

    def children(self):
        return [self.left, self.right]

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"


class UnaryOp(Expr):
    def __init__(self, op : str, opnd : Expr):
        super().__init__()
        self.opnd = opnd
        self.op = op

    def children(self):
        return [self.opnd]

    def __str__(self):
        return f"{self.op}({self.opnd})"


class Add(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '+', right)

    def value(self) -> Union[numbers.Number,np.ndarray]:
        return self.left.value() + self.right.value()

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return self.left.dvdx(wrt) + self.right.dvdx(wrt) # when left/right are numpy vectors, this still works


class Sub(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '-', right)

    def value(self) -> Union[numbers.Number,np.ndarray]:
        return self.left.value() - self.right.value()

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return self.left.dvdx(wrt) - self.right.dvdx(wrt)


class Mul(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '*', right)

    def value(self) -> Union[numbers.Number,np.ndarray]:
        return self.left.value() * self.right.value()

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return self.left.value() * self.right.dvdx(wrt) + \
               self.right.value() * self.left.dvdx(wrt)


class VecDot(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, 'dot', right)

    def value(self) -> numbers.Number:
        return np.dot(self.left.value(), self.right.value())

    def dvdx(self, wrt : Expr) -> numbers.Number:
        dr = self.right.dvdx(wrt)
        dl = self.left.dvdx(wrt)
        return self.left.value() * dr + \
               self.right.value() * dl


class VecSum(UnaryOp):
    def __init__(self, opnd):
        super().__init__('sum', opnd)

    def value(self) -> Union[numbers.Number,np.ndarray]:
        return np.sum(self.opnd.value())

    def dvdx(self, wrt : Expr) -> numbers.Number:
        # return np.ones(self.opnd.value().size) * self.opnd.dvdx(wrt)
        return self.opnd.dvdx(wrt)


class Div(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '/', right)

    def value(self) -> Union[numbers.Number,np.ndarray]:
        return self.left.value() / self.right.value()

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return (self.left.dvdx(wrt) * self.right.value() - self.left.value() * self.right.dvdx(wrt)) / \
               self.right.value()**2


class Sin(UnaryOp):
    def __init__(self, opnd):
        super().__init__('sin', opnd)

    def value(self) -> Union[numbers.Number,np.ndarray]:
        return np.sin(self.opnd.value())

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return np.cos(self.opnd.value()) * self.opnd.dvdx(wrt)


class Ln(UnaryOp):
    def __init__(self, opnd):
        super().__init__('ln', opnd)

    def value(self) -> Union[numbers.Number,np.ndarray]:
        return np.log(self.opnd.value())

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return (1 / self.opnd.value()) * self.opnd.dvdx(wrt)


class Expand(UnaryOp):
    def __init__(self, opnd, n):
        super().__init__('expand', opnd)
        self.n = n

    def value(self) -> Union[numbers.Number,np.ndarray]:
        return np.ones(self.n) * self.opnd.value()

    def dvdx(self, wrt : Expr) -> numbers.Number:
        return self.n * self.opnd.dvdx(wrt)


def sin(x:Expr) -> Sin:
    if isinstance(x, numbers.Number):
        return Sin(Const(x))
    return Sin(x)


def ln(x:Expr) -> Ln:
    if isinstance(x, numbers.Number):
        return Ln(Const(x))
    return Ln(x)


def dot(a : Expr, b : Expr) -> np.ndarray:
    return VecDot(a, b)


def sum(a : Expr) -> VecSum:
    if isinstance(a, numbers.Number):
        return VecSum(Const(a))
    return VecSum(a)
