# N-body problem test module

import numpy as np
import nbpodeint as nbpode
import nbpverlet as nbpver
import nbpverlet_mp as nbpver_mp
import nbpverlet_cl as nbpver_cl
import nbpverlet_cy as nbpver_cy

Nm = 3
Mass = np.array([.1,.2,.15])
Ro   = np.array([[-10,10],[0,0],[10,10]])
Vo   = np.array([[0.1,0.1],[-0.05,0.1],[0,0.2]])

if __name__ == '__main__':
#    nbpode.solve(Mass,Ro,Vo,350,1000,1)
#    nbpver.solve(Mass,Ro,Vo,350,1000,1,0)
#    nbpver.solve(Mass,Ro,Vo,350,1000,1,1)
#    nbpver_mp.solve(Mass,Ro,Vo,350,1000,1)
	nbpver_cl.solve(Mass,Ro,Vo,350,1000,1)
#     pos=nbpver_cy.solve(Mass,Ro,Vo,350,1000,1)
	print(pos)
