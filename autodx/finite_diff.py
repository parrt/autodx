def gradient(f,h,X):
    """
    Compute gradient of f at location specified with vector X. Values in X
    must be in same order as args of f so we can call it with f(*X). h is
    the step size to use in forward finite difference computation. For 1D X,
    the finite difference is:

    f(x + h)-f(x)
    -------------
          h

    But, generally we need to tweak each of X_i and recompute f(X) to get
    the gradient.
    """
    # X = list(X)# flip to a list from tuple so we can modify elements
    fx = f(*X) # only need this once
    dX = []
    for i in range(len(X)):
        # Make a vector of Value(X_i, [0 ... 1 ... 0]) with 1 in ith position
        X[i] += h  # tweak in dimension i
        y = f(*X)
        X[i] -=h   # undo the tweak for next round
        dx = (y - fx)/h
        dX.append(dx)
    return dX
