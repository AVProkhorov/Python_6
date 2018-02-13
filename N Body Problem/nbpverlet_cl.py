# N-body problem verlet-velocity solver (opencl)

import numpy as np
import pyopencl as cl
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

def solve(M, Ro, Vo, eTime, nPoints, plot):

    global Nm, Mass, Pos, Vel, Acc1, Acc2, PA1, PA2

    if nPoints < 2: nPoints = 2
    if nPoints > PointMaxNumber: nPoints = PointMaxNumber

    Nm = len(M)
    Mass = np.zeros(Nm, dtype=np.float64)
    for i in range(Nm):
        Mass[i] = M[i]

    DT = eTime/(nPoints-1)
    DT2 = DT*DT/2

    Pos = np.zeros(Nm*2, dtype=np.float64)
    Vel = np.zeros(Nm*2, dtype=np.float64)

    for i in range(Nm):
        Pos[i*2+0] = Ro[i,0]
        Pos[i*2+1] = Ro[i,1]
        Vel[i*2+0] = Vo[i,0]
        Vel[i*2+1] = Vo[i,1]

    Acc1 = np.zeros(Nm*2, dtype=np.float64)
    Acc2 = np.zeros(Nm*2, dtype=np.float64)
    Acc  = np.zeros(Nm*2, dtype=np.float64)

    PA1 = Acc1
    PA2 = Acc2

    if plot:
        PT = np.reshape(Pos, (1, Nm * 2))
        PosT = np.copy(PT)

    cl_platform = cl.get_platforms()[1]
    cl_cpu_devices = cl_platform.get_devices(device_type=cl.device_type.CPU)
    cl_context = cl.Context(devices=cl_cpu_devices)
    #cl_context = cl.create_some_context()
    cl_queue = cl.CommandQueue(cl_context)
    cl_program = cl.Program(cl_context, cl_kernel_code()).build()

    # Buffers on device side
    mf = cl.mem_flags
    Mass_dev = cl.Buffer(cl_context, mf.READ_ONLY  | mf.COPY_HOST_PTR, hostbuf=Mass)
    Pos_dev  = cl.Buffer(cl_context, mf.READ_ONLY  | mf.COPY_HOST_PTR, hostbuf=Pos)
    Acc_dev  = cl.Buffer(cl_context, mf.WRITE_ONLY | mf.COPY_HOST_PTR, hostbuf=Acc)

    # worker count
    Global_Size = (2,)

    # run the kernel program
    cl_program.calcDerivative(cl_queue, Global_Size, None, np.int32(Nm),np.float64(Gr),Mass_dev,Pos_dev,Acc_dev)
    # enqueue data transfer from device to host memory
    cl.enqueue_read_buffer(cl_queue, Acc_dev, PA1).wait()

    Time = 0
    while Time < eTime:
        # phase 1
        for i in range(Nm):
            Pos[i*2+0] += Vel[i*2+0]*DT+PA1[i*2+0]*DT2   # x
            Pos[i*2+1] += Vel[i*2+1]*DT+PA1[i*2+1]*DT2   # y
        # phase 2
        Pos_dev = cl.Buffer(cl_context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=Pos)
        cl_program.calcDerivative(cl_queue,Global_Size,None,np.int32(Nm),np.float64(Gr),Mass_dev,Pos_dev,Acc_dev)
        cl.enqueue_read_buffer(cl_queue, Acc_dev, PA2).wait()
        for i in range(Nm):
            Vel[i*2+0] += (PA2[i*2+0]+PA1[i*2+0])*DT/2  # Vx
            Vel[i*2+1] += (PA2[i*2+1]+PA1[i*2+1])*DT/2  # Vy
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
        ePos = np.empty((Nm,2))
        for i in range(Nm):
            ePos[i,0] = Pos[i*2+0]
            ePos[i,1] = Pos[i*2+1]
        return ePos


def cl_kernel_code():

    kernel_code = \
                  \
""" 
__kernel void calcDerivative( __const int Nm, __const double Gr,  
                            __global double* Mass, __global double* Pos, __global double* PA )
{
    // each kernel instance has a different global id
    int s = get_global_id(0);

    double ax, ay, xi, yi, xj, yj, dx, dy, rr;
    for( int i = s; i < Nm; i += 2 ){
        ax = 0;
        ay = 0;
        xi = Pos[i*2+0];
        yi = Pos[i*2+1];
        for( int j = 0; j < Nm; j++ ){
            if( i == j ) continue;
            xj = Pos[j*2+0];
            yj = Pos[j*2+1];
            dx = xj-xi;
            dy = yj-yi;
            rr = Gr*Mass[j]/pow(dx*dx+dy*dy,1.5);
            ax += dx*rr;
            ay += dy*rr;
        }
        PA[i*2+0] = ax;
        PA[i*2+1] = ay;
    }
}
"""
    return kernel_code


