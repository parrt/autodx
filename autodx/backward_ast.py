from autodx.support import *

class Expr:
    def __init__(self, x : numbers.Number = None):
        self.vi = -1
        if x is None:
            x = 0
        self.x = x
        self.dydv = 0
        self.varname = None

    def value(self):
        return self.x

    def isvar(self) -> bool:
        return False

    def isleaf(self) -> bool:
        return False

    def children(self) -> List['Expr']:
        return []

    def forward(self) -> numbers.Number:
        """
        Compute and return value of expression tree; squirrel away subexpression values
        as self.x in each subtree root.

        This specific method is used to compute the value of a leaf node.
        """
        return self.x

    def backward(self) -> None:
        "Leave hook for backward()'s dvdv() call to root's parent in case we need it"
        class OutputNode(Expr):
            def dvdv(self, wrt: 'Expr') -> numbers.Number:
                return 1
        self.backward_(OutputNode(),1)

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
        return 1 if self==wrt else 0

    def __add__(self, other):
        if isinstance(other, numbers.Number):
            other = Const(other)
        return Add(self,other)

    def __radd__(self, other):
        return Const(other).__add__(self) # other comes in as left operand so we flip order

    def __sub__(self, other):
        if isinstance(other, numbers.Number):
            other = Const(other)
        return Sub(self,other)

    def __rsub__(self, other):
        return Const(other).__sub__(self)

    def __mul__(self, other: 'Expr') -> 'Expr':  # yuck. must put 'Expr' type in string
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


class Var(Expr):
    def __init__(self, x : numbers.Number, varname : str = None):
        super().__init__(x)
        self.varname = varname

    def isvar(self) -> bool:
        return True

    def isleaf(self) -> bool:
        return True

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
        return 1 if self==wrt else 0

    def backward_(self, parent : Expr, dydv : numbers.Number) -> None:
        # actual variable leaf nodes must accumulate all contributions
        # of this var from up the tree. Sum all dy/dx_i computed backwards.
        self.dydv += dydv * parent.dvdv(self)

    def __str__(self):
        if isinstance(self.x, int):
            return f'Var({self.x})'
        return f'Var({self.x:.4f})'


class Const(Expr):
    def __init__(self, v : numbers.Number):
        super().__init__(v)
        self.x = v

    def isleaf(self) -> bool:
        return True

    def backward_(self, parent : Expr, dydv : numbers.Number) -> None:
        self.dydv = 0

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
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

    def backward_(self, parent : Expr, dydv : numbers.Number) -> None:
        self.dydv = dydv * parent.dvdv(self) # don't need to accum subexpr adjoints (they are unique)
        self.left.backward_(self, self.dydv)
        self.right.backward_(self, self.dydv)

    def forward_trace(self):
        return self.left.forward_trace() + self.right.forward_trace() + [f"v{self.vi} = {self.asvar()}"]

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def __repr__(self):
        return str(self)

    def asvar(self):
        return f"v{self.left.vi} {self.op} v{self.right.vi}"


class UnaryOp(Expr):
    def __init__(self, op : str, opnd : Expr):
        super().__init__()
        self.opnd = opnd
        self.op = op

    def children(self):
        return [self.opnd]

    def backward_(self, parent : Expr, dydv : numbers.Number) -> None:
        self.dydv = dydv * parent.dvdv(self) # don't need to accum subexpr adjoints (they are unique)
        self.opnd.backward_(self, self.dydv)

    def forward_trace(self):
        return self.opnd.forward_trace() + [f"v{self.vi} = {self.asvar()}"]

    def __str__(self):
        return f"{self.op}({self.opnd})"

    def __repr__(self):
        return str(self)

    def asvar(self):
        return f"{self.op} v{self.opnd.vi}"


class Add(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '+', right)

    def forward(self):
        self.x = self.left.forward() + self.right.forward()
        return self.x

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
        # d/dx(x + y) = d/dy(x - y) = 1
        p = 1
        return p


class Sub(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, '-', right)

    def forward(self):
        self.x = self.left.forward() - self.right.forward()
        return self.x

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
        # d/dx(x - y) = 1
        # d/dy(x - y) = -1
        if self.left == wrt:
            p = 1
        else:
            p = -1
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
        return p


class Ln(UnaryOp):
    def __init__(self, opnd):
        super().__init__('ln', opnd)

    def forward(self):
        self.x = np.log(self.opnd.forward())
        return self.x

    def dvdv(self, wrt : 'Expr') -> numbers.Number:
        p = 1 / self.opnd.x if self.opnd == wrt else 0
        return p


def sin(x:Expr) -> Sin:
    if isinstance(x, numbers.Number):
        return Sin(Const(x))
    return Sin(x)


def ln(x : Expr) -> Ln:
    if isinstance(x, numbers.Number):
        return Ln(Const(x))
    return Ln(x)
