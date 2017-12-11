from autodx.backward_ast import *

x = Variable(9)

y = x * x
print(y,'=',y.forward())
print('d/dx',y,'=',y.partial(x))

x1 = Variable(1.5)
x2 = Variable(3.6)
f = x1 + x2
print(f.value())
print(f.partial(x1))
print(f.partial(x2))

x = Variable(np.pi / 4.0)
y = sin(x)
print(y,'=',y.forward())
print('d/dx',y,'=',y.partial(x))


x1 = Variable(1.5)
x2 = Variable(np.pi / 4.0)

y = x1*x2 + sin(x1)
print()
print(y,'=',y.value())
# gradient symbolically is [cos(x1)+x2, x1]
print('d/dx1',y,'=',y.partial(x1))
print('d/dx2',y,'=',y.partial(x2))
print("Expecting", [np.cos(x1.forward())+x2.forward(), x1.forward()])