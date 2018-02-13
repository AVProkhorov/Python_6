# N-body problem verlet-velocity solver (multiprocessing)

import numpy as np
import multiprocessing as mp
from matplotlib import pyplot as plt

Gr             = 0.8   # gravity constant
PointMaxNumber = 10001 # time steps

Mass = None            # mass vector (Nm) - shared
Nm   = 0               # number of bodies

Pos  = None            # x, y vector (Nm*2)
Vel  = None            # Vx, Vy vector (Nm*2)
Acc1 = None            # 1st acceleration vector (Nm*2) - shared
Acc2 = None            # 2nd acceleration vector (Nm*2) - shared
PA1  = None            # reference to n-th acceleration vector
PA2  = None            # reference to (n+1)-th acceleration vector
PAI  = None            # PAi index (0 or 1) - shared

def solve(M, Ro, Vo, eTime, nPoints, plot):

    global Nm, Mass, Pos, Vel, Acc1, Acc2, PA1, PA2, PAI

    if nPoints < 2: nPoints = 2
    if nPoints > PointMaxNumber: nPoints = PointMaxNumber

    Nm = len(M)
    Mass = mp.RawArray('d',Nm)
    Pos  = mp.RawArray('d',Nm*2)
    Acc1 = mp.RawArray('d',Nm*2)
    Acc2 = mp.RawArray('d',Nm*2)
    PAI  = mp.RawValue('i',0)
    Vel  = np.zeros(Nm*2)

    DT = eTime/(nPoints-1)
    DT2 = DT*DT/2

    for i in range(Nm):
        Pos[i*2+0] = Ro[i,0]
        Pos[i*2+1] = Ro[i,1]
        Vel[i*2+0] = Vo[i,0]
        Vel[i*2+1] = Vo[i,1]
        Mass[i] = M[i]

    PA1 = Acc1
    PA2 = Acc2
    PAI.value = 0

    queue = mp.JoinableQueue()

    jobs = [0, 1]   # even, odd rows
    workers = []
    for job in jobs:
        worker = mp.Process(target=calc_derivative_mp, args=(queue, Nm, Mass, Pos, Acc1, Acc2, PAI))
        workers.append(worker)

    for w in workers: w.start()

    if plot:
        PT = np.reshape(Pos, (1, Nm * 2))
        PosT = np.copy(PT)

    for job in jobs: queue.put(job)     # calculate PA in processes
    queue.join()                        # wait until done

    Time = 0
    while Time < eTime:
        # phase 1
        for i in range(Nm):
            Pos[i*2+0] += Vel[i*2+0]*DT+PA1[i*2+0]*DT2   # x
            Pos[i*2+1] += Vel[i*2+1]*DT+PA1[i*2+1]*DT2   # y
        # phase 2
        PAI.value = (PAI.value+1)%2
        for job in jobs: queue.put(job)     # calculate PA in processes
        queue.join()                        # wait until done
        for i in range(Nm):
            Vel[i*2+0] += (PA2[i*2+0]+PA1[i*2+0])*DT/2  # Vx
            Vel[i*2+1] += (PA2[i*2+1]+PA1[i*2+1])*DT/2  # Vy
        PA1, PA2 = PA2, PA1
        Time += DT

        if plot:
            PT = np.reshape(Pos, (1,Nm*2))
            PosT = np.concatenate((PosT,PT), axis=0)

    for w in workers: queue.put(None)    # terminate processes
    queue.join()                         # wait until done

    for w in workers: w.join()           # wait for process termination

    if plot:
        plt.figure()
        for i in range(Nm):
            plt.plot(PosT[:,i*2+0], PosT[:,i*2+1])
        plt.show()
    else:
        ePos = np.empty((Nm,2))
        for i in range(Nm):
            ePos[i,0] = Pos[i*2+0]
            ePos[i,1] = Pos[i*2+1]
        return ePos


def calcDerivativeWorker(Nm, Mass, Pos, PA, even):

    if even:
        s = 0
    else:
        s = 1

    for i in range(s,Nm,2):
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
            rr = Gr*Mass[j]/(dx**2+dy**2)**(3/2)
            ax += dx*rr
            ay += dy*rr
        PA[i*2+0] = ax
        PA[i*2+1] = ay

def calc_derivative_mp(queue, Nm, Mass, Pos, Acc1, Acc2, PAI):

    while True:
        job = queue.get()
        if job == None:
            queue.task_done()
            break
        even = True if job == 0 else False
        PA = Acc1 if PAI.value == 0 else Acc2
        calcDerivativeWorker(Nm,Mass,Pos,PA,even)
        queue.task_done()
