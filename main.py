import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

start_angle_x=np.radians(36.264)
start_angle_y=np.radians(-45)
gCamAng = 0.
v = 0                      #switch model
xpos_start = 0.
ypos_start = 0.
xp = 0
yp = 0
x_for_panning = 0.
y_for_panning = 0.
trans_store=np.array([[ np.cos(start_angle_y), 0., np.sin(start_angle_y), 0.],
                                [              0., 1.,              0., 0.],
                                [-np.sin(start_angle_y), 0., np.cos(start_angle_y), 0.],
                                [              0., 0.,              0., 1.]])      # set starting postion
height_store=np.array([[1.,              0.,             0., 0.],
                              [0., np.cos(start_angle_x), -np.sin(start_angle_x), 0.],
                              [0., np.sin(start_angle_x),  np.cos(start_angle_x), 0.],
                              [0.,              0.,             0., 1.]])



zoom = 0


def drawUnitCube():
    glBegin(GL_QUADS)
    glVertex3f( 0.,0.,0.)
    glVertex3f( 1.,0.,0.)
    glVertex3f( 1.,0.,1.)
    glVertex3f( 0.,0.,1.) 
                             
    glVertex3f(1.,0.,0.)
    glVertex3f(1.,0.,1.)
    glVertex3f(1.,1.,1.)
    glVertex3f(1.,1.,0.) 
                             
    glVertex3f(0.,0.,1.)
    glVertex3f(1.,0.,1.)
    glVertex3f(1.,1.,1.)
    glVertex3f(0.,1.,1.)
                             
    glVertex3f(0.,0.,0.)
    glVertex3f(0.,0.,1.)
    glVertex3f(0.,1.,1.)
    glVertex3f(0.,1.,0.)
 
    glVertex3f(0.,0.,0.) 
    glVertex3f(0.,1.,0.)
    glVertex3f(1.,1.,0.) 
    glVertex3f(1.,0.,0.) 
                             
    glVertex3f(0.,1.,0.) 
    glVertex3f(1.,1.,0.)
    glVertex3f(1.,1.,1.)
    glVertex3f(0.,1.,1.)
    glEnd()


def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([1.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,1.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,1.]))
    glEnd()

def render(camAng):
    global xp, yp
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    glLoadIdentity()
    
    # viewing camera
    camera_setting(-10)

    drawFrame()

    glColor3ub(255, 255, 255)

    drawUnitCube()


def camera_setting(begin):
    global v
    if(v==0):
        gluPerspective(45, 1, 1, 100)
        #print("Perspective modle")
    else:
        glOrtho(-5,5,-5,5,-10,100)
        #print("Ortho modle")
    global trans_store,height_store,zoom
    glTranslate(0,0,begin+zoom)
    x=height_store@trans_store
    glMultMatrixf(x.T)


def left_callback(window, xpos, ypos):
    global xp, yp, xpos_start, ypos_start, gCamAng, trans_store, height_store

    gCamAng = -(np.radians(xpos_start - xpos))/3
    height = -(np.radians(ypos_start - ypos))/3
    rotation_matrix = np.array([[ np.cos(gCamAng), 0., np.sin(gCamAng), 0.],
                                [              0., 1.,              0., 0.],
                                [-np.sin(gCamAng), 0., np.cos(gCamAng), 0.],
                                [              0., 0.,              0., 1.]])

    height_matrix = np.array([[1.,              0.,             0., 0.],
                              [0., np.cos(height), -np.sin(height), 0.],
                              [0., np.sin(height),  np.cos(height), 0.],
                              [0.,              0.,             0., 1.]])
    xpos_start = xpos
    ypos_start = ypos
    trans_store = rotation_matrix @ trans_store
    height_store = height_matrix @ height_store



def right_callback(window, xpos, ypos):
    global x_for_panning, y_for_panning, gCamAng, trans_store, height_store

    now_panning_x = (- x_for_panning + xpos) / 100
    now_panning_y = (- y_for_panning + ypos) / 100

    panning_matrix_x = ([[1., 0., 0., now_panning_x],
                         [0., 1., 0.,            0.],
                         [0., 0., 1.,            0.],
                         [0., 0., 0.,            1.]])

    panning_matrix_y = ([[1., 0., 0.,             0.],
                         [0., 1., 0., -now_panning_y],
                         [0., 0., 1.,             0.],
                         [0., 0., 0.,             1.]])
    x_for_panning = xpos
    y_for_panning = ypos

    trans_store = panning_matrix_x @ trans_store
    height_store = panning_matrix_y @ height_store


def empty_callback(window, xpos, ypos):
    pass


def button_callback(window, button, action, mod):
    global xpos_start, ypos_start, x_for_panning, y_for_panning

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            (xpos_start, ypos_start) = glfw.get_cursor_pos(window)
            glfw.set_cursor_pos_callback(window, left_callback)
        elif action == glfw.RELEASE:
            glfw.set_cursor_pos_callback(window, empty_callback)

    if button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            (x_for_panning, y_for_panning) = glfw.get_cursor_pos(window)
            glfw.set_cursor_pos_callback(window, right_callback)
        elif action == glfw.RELEASE:
            glfw.set_cursor_pos_callback(window, empty_callback)


def scroll_callback(window, xoffset, yoffset):
    global zoom
    zoom = zoom + yoffset/3
def key_callback(window, key, scancode, action, mods):
    global v
    if key==glfw.KEY_V and action==glfw.PRESS:
        v=1-v


def main():
    # Initialize the library
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "main", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window,key_callback)
    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Poll for and process events
        glfw.poll_events()
        render(gCamAng)
        # Swap front and back buffers
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
