import numpy as np
import nbpodeint as nbpode
import nbpverlet as nbpver
import nbpverlet_mp as nbpver_mp
import nbpverlet_cl as nbpver_cl
import nbpverlet_cy as nbpver_cy

def hexcolor2vel(c):
    r = int(c[1:3], 16)
    g = int(c[3:5], 16)
    b = int(c[5:7], 16)
    return (r, g)

def nbpsolver(Method, Circles, eTime):

    Nm = len(Circles)
    if Nm < 2:
        print('Too few bodies. 2 or more required.')
        return
    Ro = np.zeros((Nm, 2))
    Vo = np.zeros((Nm, 2))
    M  = np.zeros(Nm)
    for i, e in enumerate(Circles):
        Ro[i,0] = e['x']
        Ro[i,1] = e['y']
        RG = hexcolor2vel(e['c'])
        Vo[i,0] = RG[1]/255.0
        Vo[i,1] = RG[0]/255.0
        M[i]    = e['s']
    if Method == 1:
        nbpode.solve(M,Ro,Vo,eTime,1001,1)
    elif Method == 2:
        nbpver.solve(M,Ro,Vo,eTime,1001,1,0)
    elif Method == 3:
        nbpver.solve(M,Ro,Vo,eTime,1001,1,1)
    elif Method == 4:
        nbpver_mp.solve(M,Ro,Vo,eTime,1001,1)
    elif Method == 5:
        nbpver_cl.solve(M,Ro,Vo,eTime,1001,1)
    elif Method == 6:
        nbpver_cy.solve(M,Ro,Vo,eTime,1001,1)

