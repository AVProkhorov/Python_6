import numpy as np
from scipy.optimize import fsolve
from scipy.integrate import odeint
from hcmodel import *

# initial temperature
To = [180, 120, 180, 120, 180, 120, 180, 120, 180]

# right part
def calcFR(X, t, model):
    mN = model.mN
    Y  = np.zeros(mN)
    for i in range(mN):
        Y[i] = model.mGetQR(i,t)
        Y[i] += -(X[i]/100)**4*model.mS[i]*model.mE[i]*model.mCo
        for j in range(mN):
            Y[i] += -(X[i]-X[j])*model.mKij[i,j]
        Y[i] /= model.mC[i]
    return Y

def setInitialTemperature(model):
    model.mT = To

# intermediate funcion to calc right part
def calcDerivative(x, t, model):
    y = calcFR(x, t, model)
    return y

# find Min/Max temperature
def solveHeatMinMax(model, timeStep):

    sTime = 0
    eTime = timeStep
    Ts = To
    minTs = min(Ts)
    maxTs = max(Ts)
    while True:
        time_vector = np.linspace(sTime, eTime, 2)
        Ta = odeint(calcDerivative, Ts, time_vector, (model,))
        Te = Ta[1,:]
        minTe = min(minTs, min(Te))
        maxTe = max(maxTs, max(Te))
        Td = abs(Te-Ts)
        e  = min(Td)
        Ts = Te
        sTime, eTime = eTime, eTime+timeStep
        print('{:5.2f} {:6.4f} {:6.4f} {:6.4}'.format(sTime, minTe, maxTe, e))
        if e < 0.0001:
            print('DONE!')
            model.mMinT = minTe
            model.mMaxT = maxTe
            return eTime
        else:
            minTs, maxTs = minTe, maxTe
    pass

def solveHeat(model, sTime, eTime):

    time_vector = np.linspace(sTime, eTime, 2)
    To = model.mT
    mT = odeint(calcDerivative, To, time_vector, (model,))
    model.mT = mT[1,:]
    minT = min(model.mT)
    maxT = max(model.mT)
    #print('{:5.2f} {:6.4f} {:6.4f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} '.
    #      format(sTime,minT,maxT,mT[1,0],mT[1,1],mT[1,2],mT[1,3],mT[1,4],mT[1,5],mT[1,6],mT[1,7],mT[1,8]))
    print('{:5.2f} {:6.4f} {:6.4f}'.format(eTime, minT, maxT))
    pass

from threading import Thread

class solveHeatThread(Thread):

    def __init__(self, model, sTime, eTime):
        Thread.__init__(self)
        self.model = model
        self.sTime = sTime
        self.eTime = eTime

    def run(self):
        solveHeat(self.model, self.sTime, self.eTime)
