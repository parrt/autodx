import sys

import autodx.forward_vec_ast
import autodx.backward_ast
import numpy as np

# some vector tests

# def vf(a,b): return a + b
#
# X =  [np.array([1,3,5]), np.array([9,7,0])]
# X_ = [autodx.forward_vec_ast.Var(x) for x in X]
#
# y = vf(*X_)
# print(y,y.value(),y.gradient(X_))
#
#
# def vf2(a,b): return a * b  # dot product
#
# X =  [np.array([1,3,5]), np.array([9,7,0])]
# X_ = [autodx.forward_vec_ast.Var(x) for x in X]
#
# y = vf2(*X_)
# print(y,y.value(),y.gradient(X_))

def vf3(a,b,c): return a * b + c # dot product

X =  [np.array([1,3,5]), np.array([9,7,0]), 99]
X_ = [autodx.forward_vec_ast.Var(x) for x in X]

y = vf3(*X_)
print(y,y.value(),y.gradient(X_))