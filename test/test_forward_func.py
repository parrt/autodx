from autodx.forward import *
import numpy as np

def Cost(X,y):
    square_error = [(X[i] - y[i])**2 for i in range(len(y))]
    return square_error

def f(x): return x*x * 5 + 1

x = Value(3)
y = f(x)
print(y)