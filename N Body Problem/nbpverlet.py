# N-body problem verlet-velocity solver (verlet + verlet multithreading)

import numpy as np
import threading
from matplotlib import pyplot as plt

Gr             = 0.8   # gravity constant
PointMaxNumber = 10001 # time steps

Mass = None            # mass vector (Nm)
Nm   = 0               # number of bodies

Pos  = None            # x, y vector (Nm,2)
Vel  = None            # Vx, Vy vector (Nm,2)
Acc1 = None            # 1st acceleration vector (Nm,2)
Acc2 = None            # 2nd acceleration vector (Nm,2)
PA1  = None            # reference to n-th acceleration vector
PA2  = None            # reference to (n+1)-th acceleration vector

def solve(M, Ro, Vo, eTime, nPoints, plot, multithreading):

    global Nm, Mass, Pos, Vel, Acc1, Acc2, PA1, PA2

    if nPoints < 2: nPoints = 2
    if nPoints > PointMaxNumber: nPoints = PointMaxNumber

    Nm = len(M)
    Mass = M

    DT = eTime/(nPoints-1)
    DT2 = DT*DT/2

    Pos = np.zeros((Nm,2))
    Vel = np.zeros((Nm,2))

    for i in range(Nm):
        Pos[i,0] = Ro[i,0]
        Pos[i,1] = Ro[i,1]
        Vel[i,0] = Vo[i,0]
        Vel[i,1] = Vo[i,1]

    Acc1 = np.zeros((Nm,2))
    Acc2 = np.zeros((Nm,2))

    PA1 = Acc1
    PA2 = Acc2

    if plot:
        PT = np.reshape(Pos, (1, Nm * 2))
        PosT = np.copy(PT)

    if multithreading:
        calc_derivative_mt(PA1)
    else:
        calc_derivative(PA1)

    Time = 0
    while Time < eTime:
        # phase 1
        for i in range(Nm):
            Pos[i,0] += Vel[i,0]*DT+PA1[i,0]*DT2   # x
            Pos[i,1] += Vel[i,1]*DT+PA1[i,1]*DT2   # y
        # phase 2
        if multithreading:
            calc_derivative_mt(PA2)
        else:
            calc_derivative(PA2)
        for i in range(Nm):
            Vel[i,0] += (PA2[i,0]+PA1[i,0])*DT/2  # Vx
            Vel[i,1] += (PA2[i,1]+PA1[i,1])*DT/2  # Vy
        PA1, PA2 = PA2, PA1
        Time += DT
        if plot:
            PT = np.reshape(Pos, (1,Nm*2))
            PosT = np.concatenate((PosT,PT), axis=0)

    if plot:
        plt.figure()
        for i in range(Nm):
            plt.plot(PosT[:,i*2+0], PosT[:,i*2+1])
        plt.show()
    else:
        return Pos


def calc_derivative(PA):

    for i in range(Nm):
        ax = 0
        ay = 0
        xi = Pos[i,0]
        yi = Pos[i,1]
        for j in range(Nm):
            if i == j : continue
            xj = Pos[j,0]
            yj = Pos[j,1]
            dx = xj-xi
            dy = yj-yi
            rr = Gr*Mass[j]/(dx**2+dy**2)**(3/2)
            ax += dx*rr
            ay += dy*rr
        PA[i,0] = ax
        PA[i,1] = ay


def calcDerivativeWorker(PA, even):

    if even:
        s = 0
    else:
        s = 1

    for i in range(s, Nm, 2):
        ax = 0
        ay = 0
        xi = Pos[i,0]
        yi = Pos[i,1]
        for j in range(Nm):
            if i == j : continue
            xj = Pos[j,0]
            yj = Pos[j,1]
            dx = xj-xi
            dy = yj-yi
            rr = Gr*Mass[j]/(dx**2+dy**2)**(3/2)
            ax += dx*rr
            ay += dy*rr
        PA[i,0] = ax
        PA[i,1] = ay

def calc_derivative_mt(PA):

    T1 = threading.Thread(target=calcDerivativeWorker,name='calc even bodies',args=(PA,1))
    T2 = threading.Thread(target=calcDerivativeWorker,name='calc odd bodies',args=(PA,0))

    T1.start()
    T2.start()
    T1.join()
    T2.join()
