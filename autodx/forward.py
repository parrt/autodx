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
        return Value(self.x * other.x, self.x * other.dx + other.x * other.dx)

    def __str__(self):
        return f"(x={self.x}, dx={self.dx})"