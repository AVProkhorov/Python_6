# N-body problem verlet-velocity solver (cython)

import numpy as np
from matplotlib import pyplot as plt

cdef double Gr             = 0.8   # gravity constant
cdef int    PointMaxNumber = 10001 # time steps

Mass = None            # mass vector (Nm)
cdef int Nm = 0        # number of bodies

Pos  = None            # x, y vector (Nm*2)
Vel  = None            # Vx, Vy vector (Nm*2)
Acc1 = None            # 1st acceleration vector (Nm*2)
Acc2 = None            # 2nd acceleration vector (Nm*2)
PA1  = None            # reference to n-th acceleration vector
PA2  = None            # reference to (n+1)-th acceleration vector

def solve(M, Ro, Vo, eTime, nPoints, plot):

    global Nm, Mass, Pos, Vel, Acc1, Acc2, PA1, PA2

    cdef double DT, DT2
    cdef int i

    if nPoints < 2: nPoints = 2
    if nPoints > PointMaxNumber: nPoints = PointMaxNumber

    Nm = len(M)
    Mass = M

    DT  = eTime/(nPoints-1)
    DT2 = DT*DT/2

    Pos = np.zeros((Nm*2), dtype=np.float64)
    Vel = np.zeros((Nm*2), dtype=np.float64)

    for i in range(Nm):
        Pos[i*2+0] = Ro[i,0]
        Pos[i*2+1] = Ro[i,1]
        Vel[i*2+0] = Vo[i,0]
        Vel[i*2+1] = Vo[i,1]

    Acc1 = np.zeros((Nm*2), dtype=np.float64)
    Acc2 = np.zeros((Nm*2), dtype=np.float64)

    PA1 = Acc1
    PA2 = Acc2

    if plot:
        PT = np.reshape(Pos, (1, Nm * 2))
        PosT = np.copy(PT)

    calc_derivative(PA1)

    Time = 0
    while Time < eTime:
        # phase 1
        for i in range(Nm):
            Pos[i*2+0] += Vel[i*2+0]*DT+PA1[i*2+0]*DT2   # x
            Pos[i*2+1] += Vel[i*2+1]*DT+PA1[i*2+1]*DT2   # y
        # phase 2
        calc_derivative(PA2)
        for i in range(Nm):
            Vel[i*2+0] += (PA2[i*2+0]+PA1[i*2+0])*DT/2  # Vx
            Vel[i*2+1] += (PA2[i*2+1]+PA1[i*2+1])*DT/2  # Vy
        PA1, PA2 = PA2, PA1
        Time += DT
        if plot:
            PT = np.reshape(Pos, (1, Nm*2))
            PosT = np.concatenate((PosT, PT), axis=0)

    if plot:
        plt.figure()
        for i in range(Nm):
            plt.plot(PosT[:,i*2+0], PosT[:,i*2+1])
        plt.show()
    else:
        ePos = np.empty((Nm, 2))
        for i in range(Nm):
            ePos[i,0] = Pos[i*2+0]
            ePos[i,1] = Pos[i*2+1]
        return ePos


cdef calc_derivative(PA):

    cdef int i
    cdef double ax, ay, xi, yi, xj, yj, rr
    for i in range(Nm):
        ax = 0
        ay = 0
        xi = Pos[i*2+0]
        yi = Pos[i*2+1]
        for j in range(Nm):
            if i == j : continue
            xj = Pos[j*2+0]
            yj = Pos[j*2+1]
            dx = xj-xi
            dy = yj-yi
            rr = Gr*Mass[j]/(dx*dx+dy*dy)**(3.0/2.0)
            ax += dx*rr
            ay += dy*rr
        PA[i*2+0] = ax
        PA[i*2+1] = ay

