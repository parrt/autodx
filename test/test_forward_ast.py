from autodx.forward_ast import *

x = Variable(9)

y = x * x
print(y,'=',y.value())
print('d/dx',y,'=',y.partial(x))

x1 = Variable(1.5)
x2 = Variable(3.6)
f = x1 + x2
print(f.value())
print(f.partial(x1))
print(f.partial(x2))

x = Variable(np.pi / 4.0)
y = sin(x)
print(y,'=',y.value())
print('d/dx',y,'=',y.partial(x))

