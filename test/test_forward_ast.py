from autodx.forward_ast import *

x = Expr(9)

y = x * x
print(y,'=',y.value())
print('d/dx', y,'=', y.dvdx(x))

x1 = Expr(1.5)
x2 = Expr(3.6)
f = x1 + x2
print(f.value())
print(f.dvdx(x1))
print(f.dvdx(x2))

x = Expr(np.pi / 4.0)
y = sin(x)
print(y,'=',y.value())
print('d/dx', y,'=', y.dvdx(x))


x1 = Expr(1.5)
x2 = Expr(np.pi / 4.0)

y = x1*x2 + sin(x1)
print()
print(y,'=',y.value())
# gradient symbolically is [cos(x1)+x2, x1]
print('d/dx1', y,'=', y.dvdx(x1))
print('d/dx2', y,'=', y.dvdx(x2))
print("Expecting", [np.cos(x1.value())+x2.value(), x1.value()])

