from __future__ import print_function
from fenics import *
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from mpl_toolkits.mplot3d import axes3d

C_PI = 3.1415926535

# Create mesh and define function space
mesh = RectangleMesh(Point(0.0, 0.0), Point(C_PI, C_PI), 30, 30)
V = FunctionSpace(mesh, 'P', 3)

# Mark boundary subdomains
bn_left  = CompiledSubDomain("near(x[0], side) && on_boundary", side = 0.0)
bn_right = CompiledSubDomain("near(x[0], side) && on_boundary", side = C_PI)
#bn_up    = CompiledSubDomain("near(x[1], side) && on_boundary", side = C_PI)
#bn_down  = CompiledSubDomain("near(x[1], side) && on_boundary", side = 0.0)

# Expressions for DirichletBC function
c_left  = Constant(0.0)
c_right = Expression('cos(2*x[1])', degree=3)
#c_up    = Constant(0.0)
#c_down  = Constant(0.0)

# Dirichlet boundary conditions
bc_left  = DirichletBC(V, c_left,  bn_left)
bc_right = DirichletBC(V, c_right, bn_right)
#bc_up    = DirichletBC(V, c_up,    bn_up)
#bc_down  = DirichletBC(V, c_down,  bn_down)

# Dirichlet combined boundary conditions
#bc_all   = [bc_left, bc_right, bc_up, bc_down]
bc_all   = [bc_left, bc_right]

# Neumann boundary conditions
g = Expression('near(x[1],0,eps) ? (-sin(2*x[0])) : (near(x[1],pi,eps) ? (sin(3*x[0])) : 0)', degree=3, eps=1e-6, pi=C_PI)

# Define variational problem
u = TrialFunction(V)
v = TestFunction(V)
f = Constant(0.0)
a = dot(grad(u), grad(v))*dx
L = f*v*dx + g*v*ds

# Compute solution
u = Function(V)
solve(a == L, u, bc_all)

# max/min in mesh nodes
umax = u.vector().max()
umin = u.vector().min()

# Plot solution and mesh
plot(u)
plot(mesh)

# Save solution to file in VTK format
vtkfile = File('plot/finel.pvd')
vtkfile << u

# parts of next function was borrowed from github
def plot_alongside(*args, **kwargs):
    """ Plot supplied functions in single figure with common colorbar.
        It is users responsibility to supply 'range_min' and 'range_max' in kwargs.
    """
    n = len(args)
    plt.figure(figsize=(4*n+2, 4))
    projection = "3d" if kwargs.get("mode") == "warp" else None
    for i in range(n):
        plt.subplot(1, n, i+1, projection=projection)
        p = plot(args[i], **kwargs)
    pass

    plt.tight_layout()

    if projection == None:
        n = mesh.num_vertices()
        d = mesh.geometry().dim()
        mesh_coordinates = mesh.coordinates().reshape((n, d))
        triangles = np.asarray([cell.entities(0) for cell in cells(mesh)])
        triangulation = tri.Triangulation(mesh_coordinates[:,0], mesh_coordinates[:,1], triangles)
        plt.triplot(triangulation, 'k-',lw=0.1)

    # Create colorbar
    plt.subplots_adjust(right=0.8)
    cbar_ax = plt.gcf().add_axes([0.85, 0.15, 0.05, 0.7])
    plt.colorbar(p, cax=cbar_ax)
pass

r = {"range_min": umin,"range_max": umax}

# solution 2d/3d plot
plot_alongside(u, mode='color', **r)
plt.savefig("plot/finel_plot.pdf")
plot_alongside(u, mode='warp', **r)
plt.savefig("plot/finel_plot_3d.pdf")

# exact solution
class Source(UserExpression):
    def eval(self, values, x):
        pi1 = C_PI
        pi2 = pi1*2
        pi3 = pi1*3
        u1 = sinh(2*x[0])/sinh(pi2)*cos(2*x[1])
        u2 = 1.0/2.0*sin(2*x[0])*(sinh(2*x[1])-cosh(pi2)/sinh(pi2)*cosh(2*x[1]))
        u3 = 1.0/3.0*sin(3*x[0])*cosh(3*x[1])/sinh(pi3)
        values[0] = u1+u2+u3

# exact solution 2d/3d plot
src = Source(degree=3)
val = interpolate(src,V)
plot_alongside(val, mode='color', **r)
plt.savefig("plot/finel_exact_plot.pdf")
plot_alongside(val, mode='warp', **r)
plt.savefig("plot/finel_exact_plot_3d.pdf")

# calculation error in mesh nodes
error_L2 = errornorm(src, u, 'L2')
vertex_values_exact = src.compute_vertex_values(mesh)
vertex_values_u = u.compute_vertex_values(mesh)
error_C = np.max(np.abs(vertex_values_u - vertex_values_exact))

print (error_L2)
print (error_C)

