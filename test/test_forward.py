from autodx.forward import *
import numpy as np

def Cost(X,y):
    square_error = [(X[i] - y[i])**2 for i in range(len(y))]
    return square_error

def f(x): return 5 *x*x  + 1

X = Expr(3)
y = f(X)
print(y)

def f2(x1,x2): return x1*x2

# Auto grad using forward differentiation
dX = gradient(f2, 3, 4) # x1*1 + x2*1
print("x1*x2 at 3, 4 =", f2(3,4))
print(dX)

# manually

y1 = f2(Expr(3, 1), Expr(4, 0)) # partial wrt to x1
y2 = f2(Expr(3, 0), Expr(4, 1)) # partial wrt to x2
dX = [y1.dx, y2.dx]
print("gradient of x1*x2 at 3, 4 =",dX)

# use pytorch for test results

import torch
from torch.autograd import Variable
from torch import FloatTensor

def autodx_results(f, X):
    y = f(*X)
    return y, gradient(f, *X)


def pytorch_results(f, X):
    X_ = Variable(torch.from_numpy(np.array(X)), requires_grad=True)

    y = f(*X_)

    y.backward()

    return y.data[0], X_.grad.data.numpy().tolist()


X = (3, 4)
y, dx = autodx_results(f2, X)
print(y,dx)
y, dx = pytorch_results(f2, X)
print(y,dx)
