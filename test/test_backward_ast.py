# seems broken
from autodx.backward_ast import *

# x = Variable(9)
#
# y = x * x
# print(y,'=',y.forward())
# y.backward()
# print('d/dx',y,'=',x.adjoint)
#
# x1 = Variable(1.5)
# x2 = Variable(3.6)
# f = x1 + x2
# print(f.forward())
# f.backward()
# print(x1.adjoint)
# print(x2.adjoint)
#
# x = Variable(np.pi / 4.0)
# y = sin(x)
# print(y,'=',y.forward())
# y.backward()
# print('d/dx',y,'=',x.adjoint)
#
# x1 = Variable(1.5)
# x2 = Variable(np.pi / 4.0)
# y = x1*x2 + sin(x1)
# print()
# print(y,'=',y.forward())
# # gradient symbolically is [cos(x1)+x2, x1]
# y.backward()
# print('d/dx1',y,'=',x1.adjoint)
# print('d/dx2',y,'=',x2.adjoint)
# print("Expecting", [np.cos(x1.forward())+x2.forward(), x1.forward()])

x1 = Expr(2)
x2 = Expr(5)

print()
y = ln(x1) + x1 * x2 - sin(x2)
#y = ln(x1) + x1
#y.set_var_indices(0)
for op in y.forward_trace():
    print(op)
print("f(2,5) = ln(x1) + x1 * x2 - sin(x2) =", y.forward())
y.backward(1,1)
print('d/dx1', y,'=', x1.dydv)
print('d/dx2', y,'=', x2.dydv)
