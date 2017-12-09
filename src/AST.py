import numpy as np

class Value:
    def __init__(self, data):
        self.data = data

    def value(self):
        return self.data

    def partial(self):
        return 0

    def __add__(self, other):
        return Add(self,other)

    def __mul__(self, other):
        return Mul(self,other)


class Add(Value):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        # super().__init__(self.value())

    def value(self):
        return self.left.value() + self.right.value()

    def partial(self):
        return self.left.partial() + self.right.partial()


class Mul(Value):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        # super().__init__(self.value())

    def value(self):
        return self.left.value() * self.right.value()

    def partial(self):
        return self.left.value() * self.right.partial() + \
               self.right.value() * self.left.partial()


class Sin(Value):
    def __init__(self, arg):
        self.arg = arg
        # super().__init__(self.value())

    def value(self):
        return np.sin(self.arg)

if __name__ == '__main__':
    x1 = Value(1.5)
    x2 = Value(3.6)
    f = x1 + x2
    print(f.value())