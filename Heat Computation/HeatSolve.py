import numpy as np
from scipy.optimize import fsolve
from scipy.integrate import odeint
from HeatModel import *

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
    #X0 = [100.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 100.0]
    #X = fsolve(calcFR, X0, (0, model))
    #X = [50, 50, 50, 50, 50, 50, 50, 50, 50]
    X = [5, 5, 5, 5, 5, 5, 5, 5, 5]
    model.mT = X


def calcDerivative(x, t, model):
    y = calcFR(x, t, model)
    return y

def solveHeat(model, sTime, eTime):

    time_vector = np.linspace(sTime, eTime, 2)
    To = model.mT
    mT = odeint(calcDerivative, To, time_vector, (model,))
    model.mT = mT[1,:]
    minT = min(model.mT)
    maxT = max(model.mT)
    #print('{:5.2f} {:6.4f} {:6.4f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} {:6.2f} '.
    #      format(sTime,minT,maxT,mT[1,0],mT[1,1],mT[1,2],mT[1,3],mT[1,4],mT[1,5],mT[1,6],mT[1,7],mT[1,8]))
    print('{:5.2f} {:6.4f} {:6.4f}'.format(sTime, minT, maxT))
    pass



