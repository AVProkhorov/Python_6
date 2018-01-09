from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math, numpy, sys

glWinId = 0

model_rotate = False
model_move = False
model_zpos = 7

model_rx = 0
model_ry = 0
model_tx = 0
model_ty = 0

camera_va = 0.0
camera_ha = math.pi

mousePosX = 0
mousePosy = 0

def draw_cube_cone():

    # Set the color to white
    glColor3f(1.0, 1.0, 1.0)
    # Reset the matrix
    glLoadIdentity()

    # Move left model to center it
    glTranslate(model_tx/20., model_ty/20., -model_zpos)
    glRotate(model_ry, 1, 0, 0)
    glRotate(model_rx, 0, 1, 0)
    glTranslatef(-1.5, 0.0, 0.0)

    # Begin drawing the color cube with 6 quads
    # Define vertices in counter-clockwise (CCW) order with normal pointing out

    glBegin(GL_QUADS)

    #Top face (y = 1.0)
    #glColor3f (0.0, 1.0, 0.0)       # Green
    glColor3f(1.0, 1.0, 0.0)        # Yellow
    glVertex3f( 1.0, 1.0, -1.0)
    glVertex3f(-1.0, 1.0, -1.0)
    glVertex3f(-1.0, 1.0,  1.0)
    glVertex3f( 1.0, 1.0,  1.0)

    # Bottom face (y = -1.0)
    #glColor3f (1.0, 0.5, 0.0)       # Orange
    glColor3f(1.0, 1.0, 0.0)        # Yellow
    glVertex3f( 1.0, -1.0,  1.0)
    glVertex3f(-1.0, -1.0,  1.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f( 1.0, -1.0, -1.0)

    # Front face  (z = 1.0)
    #glColor3f (1.0, 0.0, 0.0)       # Red
    glColor3f(1.0, 1.0, 0.0)        # Yellow
    glVertex3f( 1.0,  1.0, 1.0)
    glVertex3f(-1.0,  1.0, 1.0)
    glVertex3f(-1.0, -1.0, 1.0)
    glVertex3f( 1.0, -1.0, 1.0)

    # Back face (z = -1.0)
    glColor3f(1.0, 1.0, 0.0)        # Yellow
    glVertex3f( 1.0, -1.0, -1.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(-1.0,  1.0, -1.0)
    glVertex3f( 1.0,  1.0, -1.0)

    # Left face (x = -1.0)
    #glColor3f(0.0, 0.0, 1.0)        # Blue
    glColor3f (0.0, 1.0, 0.0)       # Green
    glVertex3f(-1.0,  1.0,  1.0)
    glVertex3f(-1.0,  1.0, -1.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(-1.0, -1.0,  1.0)

    # Right face (x = 1.0)
    #glColor3f(1.0, 0.0, 1.0)        # Magenta
    glColor3f (1.0, 0.0, 0.0)       # Red
    glVertex3f(1.0,  1.0, -1.0)
    glVertex3f(1.0,  1.0,  1.0)
    glVertex3f(1.0, -1.0,  1.0)
    glVertex3f(1.0, -1.0, -1.0)

    glEnd()

    SliceCount = 16
    da= 2*math.pi/SliceCount

    glBegin(GL_POLYGON)
    glColor3f (1.0, 0.0, 0.0)       # Red
    for i in range(SliceCount):
        a = i*da
        z = 1*math.cos(a)
        y = 1*math.sin(a)
        x = 2
        glVertex3f(x, y, z)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glColor3f (1.0, 1.0, 0.0)       # Yellow
    glVertex3f(4.0, 0.0, 0.0)
    for i in range(SliceCount):
        a = i*da
        z = 1*math.cos(a)
        y = 1*math.sin(a)
        x = 2
        glVertex3f(x, y, z)
    glVertex3f(2.0, 0.0, 1.0)
    glEnd()

# The display function
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    draw_cube_cone()
    glutSwapBuffers()

# The reshape function
def reshape(w, h):
    global mousePosX, mousePosY
    if h == 0: h = 1
    ratio = w*1.0/h
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glViewport(0, 0, GLsizei(w), GLsizei(h))
    gluPerspective(65.0, ratio, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    mousePosX = int(w/2)
    mousePosY = int(h/2)
    #glutWarpPointer(mousePosX, mousePosY)

def update(val):
    glutPostRedisplay()
    glutTimerFunc(30, update, 0);

# The keyboard controls
def OnKeyPress(key, x, y):
    if key == 27:
        glutDestroyWindow(glWinId)
        sys.exit(1)

def OnMousePress(button, state, x, y):
    global model_rotate, model_move, model_zpos, mousePosX, mousePosY
    if state == GLUT_UP:
        if   button == 0: model_rotate = False
        elif button == 2: model_move = False
    else:
        if   button == 0: model_rotate = True
        elif button == 2: model_move = True
        elif button == 3: model_zpos = max(2, model_zpos-1)
        elif button == 4: model_zpos += 1
        mousePosX = x
        mousePosY = y

def OnMouseMove(x, y):
    global model_rx, model_ry, model_tx, model_ty, mousePosX, mousePosY
    dx = x-mousePosX
    dy = y-mousePosY
    mousePosX = x
    mousePosY = y
    if model_rotate:
        model_rx += dx
        model_ry += dy
    if model_move:
        model_tx += dx
        model_ty -= dy

# Initialize OpenGL Graphics
def initGL():
    glClearColor(0.0, 0.0, 0.0, 1.0) # Set background color to black and opaque
    glClearDepth(1.0)                # Set background depth to farthest
    glEnable(GL_DEPTH_TEST)          # Enable depth testing for z-culling
    glDepthFunc(GL_LEQUAL)           # Set the type of depth-test
    glShadeModel(GL_SMOOTH)          # Enable smooth shading
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)  # Nice perspective corrections

def main():

    global glWinId

    # Initialize OpenGL
    glutInit(sys.argv)

    # Set display mode
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)

    # Set size and position of window size
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(100, 100)

    # Create window with given title
    glWinId = glutCreateWindow(b"Cube&Cone&mouse")

    # Set background to black
    glClearColor(0.0, 0.0, 0.0, 1.0)
    # Set the shade model to flat
    glShadeModel(GL_FLAT)

    # The callback for display function
    glutDisplayFunc(display)

    # The callback for reshape function
    glutReshapeFunc(reshape)

    # The callback function for keyboard controls
    glutKeyboardFunc(OnKeyPress)

    # The callback functions for mouse events
    glutMouseFunc(OnMousePress)
    glutMotionFunc(OnMouseMove)

    initGL()

    # Set timer to update frame
    glutTimerFunc(30, update, 0);
    # Start the main loop
    glutMainLoop()

# Call the main function

if __name__ == '__main__':
    main()
