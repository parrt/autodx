import numpy as np
from torch.autograd import Variable
import torch
import autodx.forward_vec_ast

print("pytorch")
print('-------------')

a = np.array([9,7,0])
a = Variable(torch.from_numpy(a).double(), requires_grad=True)
y1 = torch.sum(a)
y1.backward()
print("y1 =", y1.data.numpy())
print("y1 grad =",a.grad.data.numpy())

a, b = np.array([9,7,0]), 99
a, b = Variable(torch.from_numpy(a).double(), requires_grad=True), \
       Variable(torch.Tensor([b]).double(), requires_grad=True)
y2 = torch.sum(a * b)
y2.backward()
print("y2 =", y2.data.numpy())
print("y2 grad =",a.grad.data.numpy(),b.grad.data.numpy())

a, b = np.array([9,7,0]), np.array([1,2,3])
a, b = Variable(torch.from_numpy(a).double(), requires_grad=True), \
       Variable(torch.from_numpy(b).double(), requires_grad=True)
y3 = torch.sum(a + b)
y3.backward()
print("y3 =", y3.data.numpy())
print("y3 grad =",a.grad.data.numpy(),b.grad.data.numpy())

print()
print("autodx")
print('-------------')

a = np.array([9,7,0])
a = autodx.forward_vec_ast.Var(a)
y1 = autodx.forward_vec_ast.sum(a)
g1 = y1.gradient([a])
print("y1 =", y1.value())
print("y1 grad =", g1[0])

a, b = np.array([9,7,0]), 99
a, b = autodx.forward_vec_ast.Var(a), autodx.forward_vec_ast.Var(b)
y2 = autodx.forward_vec_ast.sum(a * b)
g2 = y2.gradient([a, b])
print("y2 =", y2.value())
print("y2 grad =", g2[0], g2[1])

a, b = np.array([9,7,0]), np.array([1,2,3])
a, b = autodx.forward_vec_ast.Var(a), autodx.forward_vec_ast.Var(b)
y3 = autodx.forward_vec_ast.sum(a + b)
g3 = y3.gradient([a, b])
print("y3 =", y3.value())
print("y3 grad =", g3[0], g3[1])
