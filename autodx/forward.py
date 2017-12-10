import numbers

class Value:
    def __init__(self, x, dx=None):
        self.x = x
        self.dx = dx if dx is not None else 1

    def value(self):
        return self.x

    def partial(self):
        return 0

    def __add__(self, other):
        if isinstance(other, numbers.Number):
            return Value(self.x + other, self.dx)  # x + c = dx
        return Value(self.x, self.dx + other.dx)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Value(self.x * other, other * self.dx) # x * c = c * dx
        return Value(self.x * other.x, self.x * other.dx + other.x * self.dx)

    def __str__(self):
        return f"(x={self.x}, dx={self.dx})"

    def __repr__(self):
        return str(self)


def gradient(f,*X):
    """
    Compute gradient of f at location specified with vector X. Values in X
    must be in same order as args of f so we can call it with f(*X).
    """
    dX = []
    for i in range(len(X)):
        X_ = [Value(x,dx=1 if i==j else 0) for j,x in enumerate(X)]
        result = f(*X_)
        dX.append(result.dx)
    return dX
