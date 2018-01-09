
# Left Mouse Button  + move: rotate
# Right Mouse Button + move: pan
# Scroll wheel: zoom in/out

import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *
from HeatModel import *
from HeatSolve import *

pygame.init()
pygame.display.set_caption('Preview')
viewport = (800,600)
#hx = viewport[0]/2
#hy = viewport[1]/2
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

modelTime = 0
modelTimeEnd = 10.0
modelTimeStep = 0.5

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

while 1:
    clock.tick(30)
    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            if showState == 1:
                sys.exit()
            else:
                showState = 1
                pygame.display.set_caption('Integrating')
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

    # RENDER OBJECT

    glTranslate(tx/20., ty/20., - zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)
    glCallList(model.gl_list)

    pygame.display.flip()

    if showState == 1:
        solveHeat(model,modelTime,modelTime+modelTimeStep)
        modelTime += modelTimeStep
        model.drawModel()
