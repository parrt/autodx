from autodx.finite_diff import *

def f(x1,x2): return x1*x2

# Auto grad using forward differentiation
h = 0.0001
dX = gradient(f, h, 3, 4) # x1*1 + x2*1
print(dX)

# manual
h = 0.0001
fx = f(3,4)
dX = [(f(3+h,4)-fx)/h, (f(3,4+h)-fx)/h]
print(dX)
