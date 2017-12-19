from autodx.finite_diff import *
from test.test_autodx import autodx_vs_pytorch

def f(x1,x2): return x1*x2

# Auto grad using forward differentiation
h = 0.0001
dX = gradient(f, h, [3, 4]) # x1*1 + x2*1
print(dX)

def f(x): return 5 * x * x + 1

def f2(x1,x2): return x1 * x2

funcs = [f, f2]

autodx_vs_pytorch(funcs, funcs)