from autodx.forward import *

import torch
from torch.autograd import Variable
import numpy as np
from inspect import signature

def autodx_eval(f, X):
    if isinstance(X, numbers.Number):
        y = f(X)
    else:
        y = f(*X)
    return y, gradient(f, X)


def pytorch_eval(f, X):
    if isinstance(X, numbers.Number):
        X = [X]
    X_ = Variable(torch.from_numpy(np.array(X)), requires_grad=True)

    y = f(*X_)

    y.backward()

    return y.data[0], X_.grad.data.numpy().tolist()


def autodx_vs_pytorch(autodx_funcs, pytorch_funcs):
    np.random.seed(999)  # use reproducible random sequence
    NLOCATIONS = 10
    LOW = -5
    HIGH = 100
    for test in range(NLOCATIONS):
        for autdox_func,pytorch_func in zip(autodx_funcs, pytorch_funcs):
            nargs = len(signature(autdox_func).parameters)
            X = list(np.random.uniform(low=LOW, high=HIGH, size=nargs))
            y1, gradient1 = autodx_eval(autdox_func, X)
            #print("autodx: ",y1,gradient1)
            y2, gradient2 = pytorch_eval(pytorch_func, X)
            #print("pytorch:",y2,gradient2)
            assert np.isclose(y1, y2)
            assert np.isclose(gradient1, gradient2).all()

    print(f"Passed gradient test at {NLOCATIONS} coordinates across {len(autodx_funcs)} functions")
