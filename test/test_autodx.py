import sys

import autodx.forward
import autodx.forward_ast
import autodx.backward_ast
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


def autodx_eval_backward_ast(f, X):
    if isinstance(X, numbers.Number):
        X = [X]
    X_ = [autodx.backward_ast.Expr(x) for x in X]
    ast = f(*X_)
    autodx.backward_ast.set_var_indices(ast,1)
    y = ast.forward()
    ast.backward()
    return y, [x.dydv for x in X_]


def autodx_eval_forward_ast(f, X):
    if isinstance(X, numbers.Number):
        X = [X]
    X_ = [autodx.forward_ast.Var(x) for x in X]
    ast = f(*X_)
    return ast.value(), ast.gradient(X_)


def autodx_eval_forward(f, X):
    if isinstance(X, numbers.Number):
        X = [X]
    X_ = [autodx.forward.Expr(x) for x in X]
    if isinstance(X, numbers.Number):
        y = f(X_)
    else:
        y = f(*X_)
    return y.x, autodx.forward.gradient(f, X)


def autodx_eval_finite_diff(f, X):
    h = 0.0000001 # has real problems with range (-0.001,0.001)
    if isinstance(X, numbers.Number):
        y = f(X)
    else:
        y = f(*X)
    return y, autodx.finite_diff.gradient(f, h, X)


def autodx_vs_pytorch(autodx_funcs, pytorch_funcs, method, ranges, tolerance=0.00000001):
    np.random.seed(999)  # use reproducible random sequence
    NCOORDINATES = 10
    errors = 0
    for lohi in ranges:
        for autodx_func,pytorch_func in zip(autodx_funcs, pytorch_funcs):
            for test in range(NCOORDINATES):
                nargs = len(signature(autodx_func).parameters)
                X = list(np.random.uniform(low=lohi[0], high=lohi[1], size=nargs))
                y1, gradient1 = method(autodx_func, X)
                # print("autodx: ",y1,gradient1)
                y2, gradient2 = pytorch_eval(pytorch_func, X)
                # print("pytorch:",y2,gradient2)
                if not np.isclose(y1, y2, atol=tolerance):
                    sys.stderr.write(f"f(X) mismatch for {autodx_func.__name__} method={method.__name__} at {[float(format(x,'.5f')) for x in X]}:\n\tfound     {y1} but\n\tshould be {y2}\n")
                    errors += 1
                if not np.isclose(gradient1,gradient2, atol=tolerance).any():
                    sys.stderr.write(f"Gradient mismatch for {autodx_func.__name__} method={method.__name__} at {[float(format(x,'.5f')) for x in X]}:\n\tfound     {gradient1} but\n\tshould be {gradient2}\n")
                    errors += 1

    if not errors:
        print(f"Test {', '.join([f.__name__ for f in autodx_funcs])} method={method.__name__} PASSED")
    else:
        print(f"Test {', '.join([f.__name__ for f in autodx_funcs])} method={method.__name__} FAILED {errors}")

    return errors


def f(x): return 5 * x * x + 1
def f2(x1, x2): return x1 * x2
def f3(x1, x2): return (x1 * x2) / 5

def f4_finite_diff(x1, x2)  : return 8 * np.sin(x1) - x2
def f4_forward(x1, x2)      : return 8 * autodx.forward.sin(x1) - x2
def f4_forward_ast(x1, x2)  : return 8 * autodx.forward_ast.sin(x1) - x2
def f4_backward_ast(x1, x2) : return 8 * autodx.backward_ast.sin(x1) - x2
def f4_pytorch(x1, x2)      : return 8 * torch.sin(x1) - x2

def f5_finite_diff(x1, x2)  :
    return np.log(x1) + x1 * x2 - np.sin(x2)
def f5_forward(x1, x2)      : return autodx.forward.ln(x1) + x1 * x2 - autodx.forward.sin(x2)
def f5_forward_ast(x1, x2)  : return autodx.forward_ast.ln(x1) + x1 * x2 - autodx.forward_ast.sin(x2)
def f5_backward_ast(x1, x2) : return autodx.backward_ast.ln(x1) + x1 * x2 - autodx.backward_ast.sin(x2)
def f5_pytorch(x1, x2)      : return torch.log(x1) + x1 * x2 - torch.sin(x2)

simple_funcs = [f, f2, f3]

finite_diff_funcs = [f4_finite_diff, f5_finite_diff]
forward_funcs = [f4_forward, f5_forward]
forward_ast_funcs = [f4_forward_ast, f5_forward_ast]
backward_ast_funcs = [f4_backward_ast, f5_backward_ast]

pytorch_funcs = [f4_pytorch, f5_pytorch]

simple_ranges = [(-5000, 5000), (-0.001, 0.001)]
ranges = [(1, 5000), (0.001, 0.002)]

print(f"Testing {len(simple_funcs)+len(pytorch_funcs)} functions in ranges {ranges}")

autodx_vs_pytorch(simple_funcs, simple_funcs, method=autodx_eval_finite_diff, ranges=simple_ranges, tolerance=1) # can't handle the small and big range with same h
autodx_vs_pytorch(finite_diff_funcs, pytorch_funcs, method=autodx_eval_finite_diff, ranges=ranges, tolerance=1)

autodx_vs_pytorch(simple_funcs, simple_funcs, method=autodx_eval_forward, ranges=simple_ranges)
autodx_vs_pytorch(forward_funcs, pytorch_funcs, method=autodx_eval_forward, ranges=ranges)

autodx_vs_pytorch(simple_funcs, simple_funcs, method=autodx_eval_forward_ast, ranges=simple_ranges)
autodx_vs_pytorch(forward_ast_funcs, pytorch_funcs, method=autodx_eval_forward_ast, ranges=ranges)

autodx_vs_pytorch(simple_funcs, simple_funcs, method=autodx_eval_backward_ast, ranges=simple_ranges)
autodx_vs_pytorch(backward_ast_funcs, pytorch_funcs, method=autodx_eval_backward_ast, ranges=ranges)
