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

    return y.item(), np.array([x.grad.data.numpy() if x.grad is not None else None for x in X_])


def autodx_eval_forward_vec_ast(f, *args):
    X_ = [autodx.forward_vec_ast.Var(arg) for arg in args]
    ast = f(*X_)
    return ast, ast.value(), ast.gradient(X_)


# some vector tests

# def vf_add_const(a): return a + 99
#
# X =  [np.array([1,3,5])]
#
# y, g   = autodx_eval_forward_vec_ast(vf_add_const, X)
# ty, tg = pytorch_eval(vf_add_const, *X)
#
# print(y,'=',y,'vs',ty)
# print("gradient",'=',g,'vs',tg)

# -----------------------------------------

def vf(a,b): return autodx.forward_vec_ast.sum(a + b)
def vf_pytorch(a,b): return torch.sum(a + b)

X =  [np.array([1,3,5]), 9]

ast, y, g   = autodx_eval_forward_vec_ast(vf, *X)
ty, tg = pytorch_eval(vf_pytorch, *X)

print(ast,'=',y,'vs',ty)
print("gradient",'=',g,'vs',tg)

# -----------------------------------------

def vf(a,b): return autodx.forward_vec_ast.sum(a * b)
def vf_pytorch(a,b): return torch.sum(a * b)

X =  [np.array([1,3,5]), 9]

ast, y, g   = autodx_eval_forward_vec_ast(vf, *X)
ty, tg = pytorch_eval(vf_pytorch, *X)

print()
print(ast,'=',y,'vs',ty)
print("gradient",'=',g,'vs',tg)

# -----------------------------------------

def vf2(a,b): return autodx.forward_vec_ast.dot(a, b)
def vf2_pytorch(a,b): return torch.dot(a, b)

X =  [np.array([1,3,5]), np.array([9,7,0])]
ast, y, g   = autodx_eval_forward_vec_ast(vf2, *X)
ty, tg = pytorch_eval(vf2_pytorch, *X)

print()
print(ast,'=',y,'vs',ty)
print("gradient",'=',g,'vs',tg)

# -----------------------------------------

def vf3(a,b,c): return autodx.forward_vec_ast.dot(a + b, b + c)
def vf3_pytorch(a,b,c):
    r = torch.dot(a + b, b + c)
    return r

X =  [np.array([1,3,5]), np.array([9,7,0]), 2]
ast, y, g   = autodx_eval_forward_vec_ast(vf3, *X)
ty, tg = pytorch_eval(vf3_pytorch, *X)

print()
print(ast,'=',y,'vs',ty)
print("gradient",'=',g,'vs',tg)

# -----------------------------------------

def vf4(a,b,c): return autodx.forward_vec_ast.dot(a, b + c)
def vf4_pytorch(a,b,c): return torch.dot(a, b + c)

X =  [np.array([1,3,5]), np.array([9,7,0]), 2]
ast, y, g   = autodx_eval_forward_vec_ast(vf4, *X)
ty, tg = pytorch_eval(vf4_pytorch, *X)

print()
print(ast,'=',y,'vs',ty)
print("gradient",'=',g,'vs',tg)
