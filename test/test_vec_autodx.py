import sys

import autodx.forward_vec_ast
import autodx.backward_ast
import numpy as np
import numbers
from torch.autograd import Variable
import torch

def pytorch_eval(f, *args):
    # args = [[x] if isinstance(x, numbers.Number) else x for x in args]
    X_ = [Variable(torch.Tensor([arg]).double(), requires_grad=True)
              if isinstance(arg, numbers.Number)
              else Variable(torch.from_numpy(np.array(arg)).double(), requires_grad=True) for arg in args]

    y = f(*X_)

    y.backward()

    return y, np.array([x.grad.data.numpy() if x.grad is not None else None for x in X_])


# some vector tests

def vf(a,b): return a + b

X =  [np.array([1,3,5]), np.array([9,7,0])]
X_ = [autodx.forward_vec_ast.Var(x) for x in X]

y = vf(*X_)
print(y,'=',y.value())
print("Jacobian:")
print(y.gradient(X_))

# -----------------------------------------

def vf(a,b): return a + b

X =  [np.array([1,3,5]), 9]
X_ = [autodx.forward_vec_ast.Var(x) for x in X]

y = vf(*X_)
print()
print(y,'=',y.value())
print("Jacobian:")
print(y.gradient(X_))

# -----------------------------------------

def vf2(a,b): return autodx.forward_vec_ast.dot(a, b)
def vf2_pytorch(a,b): return torch.dot(a, b)

X =  [np.array([1,3,5]), np.array([9,7,0])]
X_ = [autodx.forward_vec_ast.Var(x) for x in X]

y = vf2(*X_)
print()
print(y,'=',y.value())
print("Jacobian:")
print(y.gradient(X_))
print(pytorch_eval(vf2_pytorch, *X)[1])

# -----------------------------------------

def vf3(a,b,c): return autodx.forward_vec_ast.dot(a + b, b + c)
def vf3_pytorch(a,b,c):
    r = torch.dot(a + b, b + c)
    return r

X =  [np.array([1,3,5]), np.array([9,7,0]), 99]
X_ = [autodx.forward_vec_ast.Var(x) for x in X]

y = vf3(*X_)
print()
print(y,'=',y.value())
print("Jacobian:")
print(y.gradient(X_))
print(pytorch_eval(vf3_pytorch, *X)[1])