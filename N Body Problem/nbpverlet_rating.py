import numpy as np
import time
import nbpodeint as nbpode
import nbpverlet as nbpver
import nbpverlet_mp as nbpver_mp
import nbpverlet_cl as nbpver_cl
import nbpverlet_cy as nbpver_cy
from matplotlib import pyplot as plt


if __name__ == '__main__':

    massa = 0.1
    linsize = 100000.0
    vel = 1.0
    eTime = 1.0
    nTics = 25.0

    X = []
    Y_vv = []
    Y_mt = []
    Y_mp = []
    Y_cl = []
    Y_cy = []
    Y_od = []
    DP_vv = []
    DP_mt = []
    DP_mp = []
    DP_cl = []
    DP_cy = []
    DP_od = []


    for n, nPoints in enumerate((10, 10, 50, 100, 200, 500, 1000)): #, 1000)):
        Ro = np.empty((nPoints,2))
        Vo = np.empty((nPoints,2))
        M  = np.empty(nPoints)
        dx = linsize/nPoints
        x  = 0
        y  = 0
        s  = 1
        for i in range(nPoints):
            Ro[i,0] = x
            Ro[i,1] = y
            Vo[i,0] = 0
            Vo[i,1] = vel*s
            M[i] = massa
            x += dx
            s = -s

        if n == 0:
            nbpver.solve(M,Ro,Vo,eTime,nTics,0,0)
            nbpver.solve(M,Ro,Vo,eTime,nTics,0,1)
            nbpver_mp.solve(M,Ro,Vo,eTime,nTics,0)
            nbpver_cl.solve(M,Ro,Vo,eTime,nTics,0)
            nbpver_cy.solve(M,Ro,Vo,eTime,nTics,0)
            nbpode.solve(M,Ro,Vo,eTime,nTics,0)
            continue

        sT = time.time()
        P_vv = nbpver.solve(M,Ro,Vo,eTime,nTics,0,0)
        eT = time.time()
        Y_vv.append(eT-sT)

        sT = time.time()
        #P_mt = nbpver.solve(M,Ro,Vo,eTime,nTics,0,1)
        eT = time.time()
        Y_mt.append(eT-sT)

        sT = time.time()
        P_mp = nbpver_mp.solve(M,Ro,Vo,eTime,nTics,0)
        eT = time.time()
        Y_mp.append(eT-sT)

        sT = time.time()
        P_cl = nbpver_cl.solve(M,Ro,Vo,eTime,nTics,0)
        eT = time.time()
        Y_cl.append(eT-sT)

        sT = time.time()
        P_cy = nbpver_cy.solve(M,Ro,Vo,eTime,nTics,0)
        eT = time.time()
        Y_cy.append(eT-sT)

        sT = time.time()
        P_od = nbpode.solve(M,Ro,Vo,eTime,nTics,0)
        eT = time.time()
        Y_od.append(eT-sT)

        X.append(nPoints)

        DP_vv.append(np.amax(np.fabs(P_od-P_vv))*1000)
        DP_cl.append(np.amax(np.fabs(P_od-P_cl))*1000)
        DP_cy.append(np.amax(np.fabs(P_od-P_cy)))

    plt.figure('Time')
    plt.plot(X, Y_vv,label='verlet_vv')
    plt.plot(X, Y_mt,label='verlet_mt')
    plt.plot(X, Y_mp,label='verlet_mp')
    plt.plot(X, Y_cl,label='verlet_cl')
    plt.plot(X, Y_cy,label='verlet_cy')
    plt.plot(X, Y_od,label='scipy_ode')
    plt.legend(loc='best')
    plt.show()

    plt.figure("Error*1000")
    plt.plot(X, DP_vv,label='verlet_vv')
    plt.plot(X, DP_cl,label='verlet_cl')
    plt.plot(X, DP_cy,label='verlet_cy')
    plt.legend(loc='best')
    plt.show()

    #print(DP_cl)
