from autodx.forward import *
import numpy as np

def Cost(X,y):
    square_error = [(X[i] - y[i])**2 for i in range(len(y))]
    return square_error

def f(x): return x*x * 5 + 1

x = Value(3)
y = f(x)
print(y)

def f2(x1,x2): return x1*x2

print(gradient(f2, 3, 4)) # x1*1 + x2*1
x1 = Value(3)
x2 = Value(4)
y = f2(x1,x2)
print(y)