from autodx.forward import *
import numpy as np

def Cost(X,y):
    square_error = [(X[i] - y[i])**2 for i in range(len(y))]
    return square_error

def f(x): return 5 *x*x  + 1

x = Variable(3)
y = f(x)
print(y)

def f2(x1,x2): return x1*x2

# Auto grad using forward differentiation
dX = gradient(f2, 3, 4) # x1*1 + x2*1
print(dX)

# manually

y1 = f2(Variable(3,1),Variable(4,0)) # partial wrt to x1
y2 = f2(Variable(3,0),Variable(4,1)) # partial wrt to x2
dX = [y1.dx, y2.dx]
print(dX)
