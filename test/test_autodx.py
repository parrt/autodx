import sys

import autodx.forward
import autodx.finite_diff

import torch
from torch.autograd import Variable
import numpy as np
from inspect import signature
import numbers

def pytorch_eval(f, X):
    if isinstance(X, numbers.Number):
        X = [X]
    X_ = Variable(torch.from_numpy(np.array(X)), requires_grad=True)

    y = f(*X_)

    y.backward()

    return y.data[0], X_.grad.data.numpy().tolist()


def autodx_eval_forward(f, X):
    if isinstance(X, numbers.Number):
        y = f(X)
    else:
        y = f(*X)
    return y, autodx.forward.gradient(f, X)


def autodx_eval_finite(f, X):
    h = 0.001
    if isinstance(X, numbers.Number):
        y = f(X)
    else:
        y = f(*X)
    return y, autodx.finite_diff.gradient(f, h, X)


def autodx_vs_pytorch(autodx_funcs, pytorch_funcs, method):
    np.random.seed(999)  # use reproducible random sequence
    NLOCATIONS = 10
    LOW = -5
    HIGH = 100
    errors = 0
    for autdox_func,pytorch_func in zip(autodx_funcs, pytorch_funcs):
        for test in range(NLOCATIONS):
            nargs = len(signature(autdox_func).parameters)
            X = list(np.random.uniform(low=LOW, high=HIGH, size=nargs))
            y1, gradient1 = method(autdox_func, X)
            # print("autodx: ",y1,gradient1)
            y2, gradient2 = pytorch_eval(pytorch_func, X)
            # print("pytorch:",y2,gradient2)
            if not np.isclose(y1, y2):
                sys.stderr.write(f"f(X) mismatch: found {y1} but should be {y2}\n")
                errors += 1
            if not np.isclose(gradient1, gradient2).all():
                sys.stderr.write(f"Gradient mismatch: found {gradient1} but should be {gradient2}\n")
                errors += 1

    return errors


def f(x): return 5 * x * x + 1

def f2(x1, x2): return x1 * x2

funcs = [f, f2]
print(f"Testing {len(funcs)} functions")

errors = autodx_vs_pytorch(funcs, funcs, method=autodx_eval_finite)
if not errors:
    print(f"Finite difference PASSED gradient test")
else:
    print(f"Finite difference FAILED {errors} gradient tests")

errors = autodx_vs_pytorch(funcs, funcs, method=autodx_eval_forward)
if not errors:
    print(f"Forward PASSED gradient test across")
else:
    print(f"Forward FAILED {errors} gradient tests")
