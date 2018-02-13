
# Left Mouse Button  + move: rotate
# Right Mouse Button + move: pan
# Scroll wheel: zoom in/out

import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *
from hcmodel import *
from hcsolve import *

def drawColorBar():

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 1.0, 0.0, 1.0, 0.0, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    X1, X2 = 0.9, 0.95
    Y0 = 0.05
    DY = 0.9/100
    for n in range(101):
        t = 0.01*n
        c = [t, 0.0, 1 - t]
        glColor3fv(c)
        Y1 = Y0+DY*n
        Y2 = Y1+DY
        Z  = -0.1
        glBegin(GL_POLYGON)
        glVertex3fv([X1, Y1, Z])
        glVertex3fv([X2, Y1, Z])
        glVertex3fv([X2, Y2, Z])
        glVertex3fv([X1, Y2, Z])
        glEnd()

    glColor3f (1.0, 1.0, 1.0)
    glBegin(GL_POLYGON)
    glVertex3f (0.9,  0.05, -1.0)
    glVertex3f (0.95, 0.05, -1.0)
    glVertex3f (0.95, 0.95, -1.0)
    glVertex3f (0.9,  0.95, -1.0)
    glEnd()

def drawModel():
    model.drawModel()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    width, height = viewport
    gluPerspective(90.0, width / float(height), 1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glTranslate(tx / 20., ty / 20., - zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)
    glCallList(model.gl_list)

def preDrawModel():
    model.preDrawModel()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    width, height = viewport
    gluPerspective(90.0, width / float(height), 1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glTranslate(tx / 20., ty / 20., - zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)
    glCallList(model.gl_list)

pygame.init()
pygame.display.set_caption('Previewing')
viewport = (800, 600)
srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

#glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
#glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
glEnable(GL_LIGHT0)
#glEnable(GL_LIGHTING)
#glEnable(GL_COLOR_MATERIAL)
glEnable(GL_DEPTH_TEST)
glShadeModel(GL_SMOOTH)

model = hcModel()
model.loadModel('model3.obj')
model.preDrawModel()
model.calcModelParams()

modelTime = 0           # current time
modelTimeEnd = 0        # will be set by solver
modelTimeStep = 1.0

setInitialTemperature(model)

clock = pygame.time.Clock()

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
width, height = viewport
gluPerspective(90.0, width/float(height), 1, 100.0)
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)

rx, ry = (0,    0)
tx, ty = (0, -200)
zpos = 20
rotate = move = False

glTranslate(tx / 20., ty / 20., - zpos)
glRotate(ry, 1, 0, 0)
glRotate(rx, 0, 1, 0)
glCallList(model.gl_list)
pygame.display.flip()

showState = 0
solverThread = None

gl_list_colorbar = 0

while 1:
    clock.tick(30)
    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            if showState == 3 :
                sys.exit()
            elif showState == 2:
                showState = 3
                pygame.display.set_caption('Integrating & animating')
            elif showState == 0:
                showState = 1
                pygame.display.set_caption('Integrating + looking for min/max temperature')
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 4: zpos = max(1, zpos-1)
            elif e.button == 5: zpos += 1
            elif e.button == 1: rotate = True
            elif e.button == 3: move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1: rotate = False
            elif e.button == 3: move = False
        elif e.type == MOUSEMOTION:
            i, j = e.rel
            if rotate:
                rx += i
                ry += j
            if move:
                tx += i
                ty -= j

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if showState == 0:
        preDrawModel()

    elif showState == 1:
        modelTimeEnd = solveHeatMinMax(model, 10)
        showState = 2
        pygame.display.set_caption('Ready to animate')
        modelTime = 0
        modelTimeStep = modelTimeEnd / 200.0

    elif showState == 2:
        drawModel()
        drawColorBar()

    elif showState == 3:
        if solverThread is None or not solverThread.isAlive():
            if modelTime >= modelTimeEnd:
                setInitialTemperature(model)
                modelTime = 0
            solverThread = solveHeatThread(model, modelTime, modelTime+modelTimeStep)
            solverThread.start()
            modelTime += modelTimeStep
        drawModel()
        drawColorBar()

    pygame.display.flip()
