from OpenGL.GL import *
import numpy as np
import math, sys

class hcModel:

    mN = 9                      # number of parts
    mT = np.zeros(mN)           # temperature of each part
    mE = None                   # Ei factor     
    mC = None                   # Ci factor     
    mS = np.zeros(mN)           # area of each part

    mLij = None                 # lambda factor  
    mKij = np.zeros((mN, mN))   # k factor
    mSij = np.zeros((mN, mN))   # common area of parts i&j

    mCo = 5.67                  # Boltzmann's constant
    mAr2 = 20.0                 # A factor in QR
    mAr8 = 30.0

    # set known model parameters

    mE = (0.05, 0.05, 0.05, 0.02, 0.1, 0.01, 0.05, 0.05, 0.05)
    #mC = (900, 900, 900, 1930, 520, 840, 900, 900, 900)
    mC = (900, 900, 900, 520, 1930, 840, 900, 900, 900)

    mLij = ( (   0,  240,    0,    0,    0,    0,    0,    0,    0 ),
             ( 240,    0,  240,    0,    0,    0,    0,    0,    0 ),
             (   0,  240,    0,  118,    0,    0,    0,    0,    0 ),
             (   0,    0,  118,    0,  9.7,    0,    0,    0,    0 ),
             (   0,    0,    0,  9.7,    0, 10.5,    0,    0,    0 ),
             (   0,    0,    0,    0, 10.5,    0,  119,    0,    0 ),
             (   0,    0,    0,    0,    0,  119,    0,  240,    0 ),
             (   0,    0,    0,    0,    0,    0,  240,    0,  240 ),
             (   0,    0,    0,    0,    0,    0,    0,  240,    0 ) )

    vertices = []       # list of all vertices
    normals = []        # list of all normals if exist
    faces = []          # list of all faces
    group = 0           # current part number while scanning obj file

    mMinT = 0           # min temperature from solver
    mMaxT = 0           # max temperature from solver


    def __init__(self): pass

    def loadModel(self, filename, swapyz=False):
        
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt': continue
            elif values[0] == 'g' : self.group += 1
            elif values[0] == 'f':
                face = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, self.changeGroup(self.group)))

    def changeGroup(self, gn):       # misspelling correction
        if   gn == 8: return 6
        elif gn == 6: return 8
        else:         return gn

    def calcModelParams(self):      # calc model params on startup
        self.mCalcPartAreas()
        self.mCalcPartConnectionAreas()
        for i in range(self.mN):
            for j in range(self.mN): self.mKij[i,j] = self.mLij[i][j]*self.mSij[i,j]
        pass

    def preDrawModel(self):
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glFrontFace(GL_CCW)
        for face in self.faces:
            vertices, normals, group = face
            #c = list(map(lambda x: x*group/self.group,(1.0,1.0,0.5)))
            if  group == 1: c = [0.3,0.0,0.0]
            if  group == 2: c = [0.6,0.0,0.0]
            if  group == 3: c = [0.9,0.0,0.0]
            if  group == 4: c = [0.0,0.3,0.0]
            if  group == 5: c = [0.0,0.6,0.0]
            if  group == 6: c = [0.0,0.9,0.0]
            if  group == 7: c = [0.0,0.0,0.3]
            if  group == 8: c = [0.0,0.0,0.6]
            if  group == 9: c = [0.0,0.0,0.9]
            glColor3fv(c)
            glBegin(GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
            glEnd()
        glEndList()

    def drawModel(self):
        maxT = self.mMaxT
        minT = self.mMinT
        dT = maxT-minT
        gC = []
        for n in range(self.mN):
            t = (self.mT[n]-minT)/dT
            c = [t, 0.0, 1-t]
            gC.append(c)
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glFrontFace(GL_CCW)
        for face in self.faces:
            vertices, normals, group = face
            c = gC[group-1]
            glColor3fv(c)
            glBegin(GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
            glEnd()
        glEndList()

    def mGetQR(self, n, t):
        if n == 1:
            #QR = self.mAr2*(22+22*math.sin(t/8))
            QR = self.mAr2*22
        elif n == 7:
            #QR = self.mAr8*(22+22*math.sin(t/6))
            QR = self.mAr8*22
        else:
            QR = 0
        return QR

    def triangle_area(self, v1, v2, v3):
        return np.linalg.norm(np.cross(v2-v1, v3-v1))*0.5

    def mCalcPartAreas(self):
        for face in self.faces:
            vertices, normals, group = face
            vs = self.vertices
            v1 = np.array(vs[vertices[0]-1])
            v2 = np.array(vs[vertices[1]-1])
            v3 = np.array(vs[vertices[2]-1])
            self.mS[group-1] += self.triangle_area(v1, v2, v3)

    def mGetSideArea(self, g, top = True):
        eps = 0.001
        vs = self.vertices
        miny = sys.float_info.max
        maxy = -miny
        for face in self.faces:
            vertices, normals, group = face
            if g != group: continue;
            v1 = vs[vertices[0]-1]
            v2 = vs[vertices[1]-1]
            v3 = vs[vertices[2]-1]
            y1 = v1[1]
            y2 = v2[1]
            y3 = v3[1]
            if top:
                maxy = max(maxy, y1, y2, y3)
            else:
                miny = min(miny, y1 ,y2, y3)
        s = 0
        for face in self.faces:
            vertices, normals, group = face
            if g != group: continue;
            v1 = vs[vertices[0]-1]
            v2 = vs[vertices[1]-1]
            v3 = vs[vertices[2]-1]
            y1 = v1[1]
            y2 = v2[1]
            y3 = v3[1]
            if top:
                dy = max(maxy-y1, maxy-y2, maxy-y3)
            else:
                dy = max(y1-miny, y2-miny, y3-miny)
            if dy < eps:
                s += self.triangle_area(np.array(v1), np.array(v2), np.array(v3))
        return s

    def mCalcPartConnectionAreas(self):
        s12 = self.mGetSideArea(1,True)
        s23 = self.mGetSideArea(2,True)
        s34 = self.mGetSideArea(3,True)
        s45 = self.mGetSideArea(4,True)
        s65 = self.mGetSideArea(6,False)
        s67 = self.mGetSideArea(6,True)
        s78 = self.mGetSideArea(7,True)
        s89 = self.mGetSideArea(8,True)
        mS = self.mS
        mS[0] -= s12
        mS[1] -= s12+s23
        mS[2] -= s23+s34
        mS[3] -= s34+s45
        mS[4] -= s45+s65
        mS[5] -= s65+s67
        mS[6] -= s67+s78
        mS[7] -= s78+s89
        mS[8] -= s89
        mSij = self.mSij
        mSij[0,1], mSij[1,0] = s12, s12
        mSij[1,2], mSij[2,1] = s23, s23
        mSij[2,3], mSij[3,2] = s34, s34
        mSij[3,4], mSij[4,3] = s45, s45
        mSij[5,4], mSij[4,5] = s65, s65
        mSij[5,6], mSij[6,5] = s67, s67
        mSij[6,7], mSij[7,6] = s78, s78
        mSij[7,8], mSij[8,7] = s89, s89


