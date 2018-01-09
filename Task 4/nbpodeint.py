# N-body problem scipy solver

import numpy as np
from scipy.integrate import odeint
from matplotlib import pyplot as plt

Gr             = 0.8     # gravity constant
TimeVectorSize = 1001

Mass = None            # mass vector (Nm)
Nm   = 0               # number of bodies

def solve(M, Ro, Vo, eTime):

    global Nm, Mass

    Nm = len(M)
    Mass = M

    time_vector = np.linspace(0, eTime, TimeVectorSize)
    Zinit = np.zeros(Nm*4)
    for i in range(Nm):
        Zinit[i*4+0] = Ro[i,0]
        Zinit[i*4+1] = Vo[i,0]
        Zinit[i*4+2] = Ro[i,1]
        Zinit[i*4+3] = Vo[i,1]

    Zarray = odeint(calc_derivative, Zinit, time_vector)

    plt.figure()
    for i in range(Nm):
        plt.plot(Zarray[:,i*4+0], Zarray[:,i*4+2], label='xy')
    
    plt.show()

def calc_derivative(zvec, time):

    rvec = np.zeros(Nm*4)
    for i in range(Nm):
        ax = 0
        ay = 0
        xi = zvec[i*4+0]
        yi = zvec[i*4+2]
        for j in range(Nm):
            if i == j : continue
            xj = zvec[j*4+0]
            yj = zvec[j*4+2]
            dx = xj-xi
            dy = yj-yi
            rr = Gr*Mass[j]/(dx**2+dy**2)**(3/2)
            ax += dx*rr
            ay += dy*rr
        rvec[i*4+0] = zvec[i*4+1]
        rvec[i*4+1] = ax
        rvec[i*4+2] = zvec[i*4+3]
        rvec[i*4+3] = ay

    return rvec
