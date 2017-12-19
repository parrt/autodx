import numbers
import numpy as np

class Expr:
    def __init__(self, x, dx=1):
        self.x = x
        self.dx = dx

    def value(self):
        return self.x

    def dvdx(self):
        return 0

    def __add__(self, other):
        if isinstance(other, numbers.Number):
            return Expr(self.x + other, self.dx)  # d/dx(x + c) = dx
        return Expr(self.x, self.dx + other.dx)

    def __radd__(self, other): return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, numbers.Number):
            return Expr(self.x - other, self.dx)  # d/dx(x - c) = dx
        return Expr(self.x, self.dx - other.dx)

    def __rsub__(self, other): return self.__sub__(other)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Expr(self.x * other, other * self.dx) # d/dx(x * c) = c * dx
        return Expr(self.x * other.x, self.dx * other.x + self.x * other.dx)

    def __rmul__(self, other):
        "Allows 5 * Variable(3) to invoke overloaded * operator"
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            return Expr(self.x / other.x, self.dx / other.x) # d/dx(x / c) = 1/c * dx = dx/c
        return Expr(self.x / other.x, (self.dx * other.x - self.x * other.dx)/other.x**2)

    def __rtruediv__(self, other): return self.__truediv__(other)

    def __str__(self):
        return f"(x={self.x}, dx={self.dx})"

    def __repr__(self):
        return str(self)


def sin(expr:Expr) -> Expr:
    return Expr(np.sin(expr.x), np.cos(expr.x) * expr.dx)


def ln(expr:Expr) -> Expr:
    return Expr(np.log(expr.x), (1 / expr.x) * expr.dx)


def gradient(f,X):
    """
    Compute gradient of f at location specified with vector X. Variables in X
    must be in same order as args of f so we can call it with f(*X).
    """
    dX = []
    for i in range(len(X)):
        # Make a vector of Variable(X_i, [0 ... 1 ... 0]) with 1 in ith position
        X_ = [Expr(x, dx=1 if i == j else 0) for j, x in enumerate(X)]
        result = f(*X_)
        dX.append(result.dx)
    return dX
