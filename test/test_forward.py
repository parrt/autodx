from autodx.forward import *

import torch
from torch.autograd import Variable
import numpy as np
from inspect import signature

from test.test_autodx import autodx_vs_pytorch

# def Cost(X,y):
#     square_error = [(X[i] - y[i])**2 for i in range(len(y))]
#     return square_error

def f(x): return 5 * x * x + 1

def f2(x1,x2): return x1 * x2

funcs = [f, f2]

autodx_vs_pytorch(funcs, funcs)