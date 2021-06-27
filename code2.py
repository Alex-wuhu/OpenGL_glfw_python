import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import ctypes

start_angle_x=np.radians(36.264)
start_angle_y=np.radians(-45)
gCamAng = 0.
press = 0.     #switch modle
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

#assignment2 variables
v = np.array([0.,0.,0.],'float32')
vn = np.array([0.,0.,0.],'float32')
fn = np.array([0., 0.], 'float32')
iarr = np.array([0.,0.,0.])
gVertexArraySeparate = None      #assign varr
reset = None                     #reset varr to latest dropped_file
count_all_num3 = 0

H=False
wire_frame = False
gouraud = False

def render(camAng):
    global xp, yp, lightcolor, reset, gVertexArraySeparate
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    if wire_frame:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()


    # viewing camera
    camera_setting(-30)

    drawFrame()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
  #  glEnable(GL_LIGHT1)
    glEnable(GL_NORMALIZE)

    glPushMatrix()
    lightPos = (3.,4.,5.,1.) # try to change 
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
    glPopMatrix()
# light intensity for each color channel
    lightColor = (1.,1.,1.,1.)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR,lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT,ambientLightColor)
# material reflectance for each color 
    objectColor = (1.,1.,0.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR,specularObjectColor)


    if not H:
        drawObj_glDrawArray()
    else:
        draw_hierarchial_model()

    glDisable(GL_LIGHTING)



# draw primitive and frame

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([10., 0., 0.]))
   
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([0., 10., 0.]))

    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., 0., 10.]))
    glVertex3fv(np.array([0., 0., 0.]))
    glEnd()




def camera_setting(begin):
    global press,trans_store, height_store, zoom
    if(press==0):
        gluPerspective(45, 1, 1, 100)
        #print("Perspective modle")
    else:
        glOrtho(-5,5,-5,5,-10,100)
        #print("Ortho modle")
    glTranslate(0, 0, begin + zoom)
    x = height_store @ trans_store
    glMultMatrixf(x.T)



#  left button click
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


#  right button click
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

# if released, do nothing
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
    global press,wire_frame, gouraud,H
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_V:
            press=1-press
        elif key == glfw.KEY_Z:
            wire_frame = not wire_frame
        elif key == glfw.KEY_S:
            gouraud = not gouraud
        elif key==glfw.KEY_H:
            H=not H



def drop_callback(window, count, **paths):
    global vn,v, gVertexArraySeparate
    gVertexArraySeparate = None
    v = np.array([0., 0., 0.], 'float32')
    vn = np.array([0., 0., 0.], 'float32')
    gVertexArraySeparate = handle_dropped_file(count[0])

# put all v in v[] and put all vn in vn[]
# following f, put vn and v in varr
# if polygon has 3 vertices, put vn and v in varr
# elif polygon has more vertices,
# split it to several triangles and put vn and v in varr
def handle_dropped_file(count):
    global vn, v, glVertexArrayForGouraud, iarr, fn , reset, count_all_num3
    varr = np.array([0, 0, 0], 'float32')
    f = open(count, 'r')
    print("rendering~")
    face_count=0
    face_3_count = 0
    face_4_count = 0
    face_more_count = 0
    v_count = 0
    count_all_num3 = 0
    while True:
        line = f.readline()
        if not line: break
        if line == '\n':
            continue
        division = line.split()
        if division[0] == 'v':
            v = np.vstack((v, np.array([float(division[1]), float(division[2]), float(division[3])],'float32')))
            v_count += 1
        elif division[0] == 'vn':
            vn = np.vstack((vn, np.array([float(division[1]), float(division[2]), float(division[3])],'float32')))
        elif division[0] == 'f':
            face_count += 1
            f_len = len(division)
            f_division = division[1].split('/')
            f_v0 = int(f_division[0])
            f_vn0 = int(f_division[2])
            if f_len-1 > 3: # if f has more than 3 vertices
                va = f_v0
                vb = 0
                vc = 0
                if f_len == 5: # if vertices are 4
                    face_4_count += 1
                else:
                    face_more_count += 1
                for i in range(2, f_len-1):
                    varr = np.vstack((varr, vn[f_vn0]))
                    varr = np.vstack((varr, v[f_v0]))
                    fn = np.vstack((fn, np.array([float(f_v0), float(f_vn0)], 'float32')))
                    for j in range(i, i+2):
                        f_division = division[j].split('/')
                        f_v = int(f_division[0])
                        f_vn = int(f_division[2])
                        varr = np.vstack((varr, vn[f_vn]))
                        varr = np.vstack((varr, v[f_v]))
                        fn = np.vstack((fn, np.array([float(f_division[0]), float(f_division[2])], 'float32')))
                        if j == i:
                            vb = int(f_division[0])
                        elif j == i+1:
                            vc = int(f_division[0])
                    iarr = np.vstack((iarr, np.array([int(va), vb, vc])))
                    count_all_num3 += 1
            else:
                face_3_count += 1
                va = 0
                vb = 0
                vc = 0
                for i in range(1, f_len):
                    f_division = division[i].split('/')
                    f_v = int(f_division[0])
                    f_vn = int(f_division[2])
                    varr = np.vstack((varr, vn[f_vn]))
                    varr = np.vstack((varr, v[f_v]))
                    fn = np.vstack((fn, np.array([float(f_division[0]), float(f_division[2])], 'float32')))
                    if i == 1:
                        va = int(f_division[0])
                    elif i == 2:
                        vb = int(f_division[0])
                    elif i == 3:
                        vc = int(f_division[0])
                iarr = np.vstack((iarr, np.array([va,vb,vc])))
                count_all_num3 += 1
    f.close()

    iarr = np.delete(iarr, (0), axis=0)
    varr = np.delete(varr, (0), axis=0)
    path_division = count.split('/')
    print("File name: " + path_division[len(path_division)-1])
    print("Total number of faces : " , face_count)
    print("Number of faces with 3 vertices : ", face_3_count)
    print("Number of faces with 4 vertices : ", face_4_count)
    print("Number of faces with more than 4 vertices : ", face_more_count)
    reset = varr
    return varr

def handle_obj_file(path):
    
    local_v = np.array([0.,0.,0.],'float32')
    local_vn = np.array([0.,0.,0.],'float32')
    local_varr = np.array([0, 0, 0], 'float32')

    local_iarr = np.array([0, 0, 0], 'float32')
    f = open(path, 'r')
    print("obj file rendering ~")
    face_count=0
    face_3_count = 0
    face_4_count = 0
    face_more_count = 0
    v_count = 0
    count_all_num3 = 0
    while True:
        line = f.readline()
        if not line: break
        if line == '\n':
            continue
        division = line.split()
        if division[0] == 'v':
            local_v = np.vstack((local_v, np.array([float(division[1]), float(division[2]), float(division[3])],'float32')))
            v_count += 1
        elif division[0] == 'vn':
            local_vn = np.vstack((local_vn, np.array([float(division[1]), float(division[2]), float(division[3])],'float32')))
        elif division[0] == 'f':
            face_count += 1
            f_len = len(division)
            f_division = division[1].split('/')
            f_v0 = int(f_division[0])
            f_vn0 = int(f_division[2])
            if f_len-1 > 3: # if f has more than 3 vertices
                va = f_v0
                vb = 0
                vc = 0
                if f_len == 5: # if vertices are 4
                    face_4_count += 1
                else:
                    face_more_count += 1
                for i in range(2, f_len-1):
                    local_varr = np.vstack((local_varr, local_vn[f_vn0]))
                    local_varr = np.vstack((local_varr, local_v[f_v0]))
                    for j in range(i, i+2):
                        f_division = division[j].split('/')
                        f_v = int(f_division[0])
                        f_vn = int(f_division[2])
                        local_varr = np.vstack((local_varr, local_vn[f_vn]))
                        local_varr = np.vstack((local_varr, local_v[f_v]))
                        if j == i:
                            vb = int(f_division[0])
                        elif j == i+1:
                            vc = int(f_division[0])
                    count_all_num3 += 1
            else:
                face_3_count += 1
                va = 0
                vb = 0
                vc = 0
                for i in range(1, f_len):
                    f_division = division[i].split('/')
                    f_v = int(f_division[0])
                    f_vn = int(f_division[2])
                    local_varr = np.vstack((local_varr, local_vn[f_vn]))
                    local_varr = np.vstack((local_varr, local_v[f_v]))
                    if i == 1:
                        va = int(f_division[0])
                    elif i == 2:
                        vb = int(f_division[0])
                    elif i == 3:
                        vc = int(f_division[0])
                count_all_num3 += 1
    f.close()

    local_varr = np.delete(local_varr, (0), axis=0)
  
  
    return local_varr
def draw_obj(varr):
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(varr.size/6))


def for_gouraud():
    global iarr, v, count_all_num3

    if v is None:
        return
    narr = []
    normal = []
    for x in range(len(v)):
        normal.append([])

    for i in range(count_all_num3):
        p1 = v[int(iarr[i][0])]
        p2 = v[int(iarr[i][1])]
        p3 = v[int(iarr[i][2])]
        tmp_normal = np.cross(p1-p2, p1-p3)
        tmp_normal = tmp_normal / np.sqrt(np.dot(tmp_normal, tmp_normal))

        for j in range(3):
            normal[int(iarr[i][j])].append(tmp_normal)
    for i in range(len(normal)):
        tmp_sum =[0, 0, 0]
        for j in range(len(normal[i])):
            for k in range(3):
                tmp_sum[k] += np.float32(normal[i][j][k])
        tmp = np.array(tmp_sum)
        tmp = tmp / (np.sqrt(np.dot(tmp, tmp)))
        narr.append(np.float32(tmp))
    return np.array(narr)


def gouraud_shading():
    global fn,v, gVertexArraySeparate, count_all_num3
    if count_all_num3 == 0:
        return

    new_arr = np.array([0., 0., 0], 'float32')
    tmp = for_gouraud()
    for i in range(1,len(fn)):
        v_arr = v[int(fn[i][0])]
        n_arr = tmp[int(fn[i][1])]
        new_arr = np.vstack((new_arr, np.array([n_arr[0], n_arr[1], n_arr[2]],'float32')))
        new_arr = np.vstack((new_arr, np.array([v_arr[0], v_arr[1], v_arr[2]],'float32')))
    new_arr = np.delete(new_arr, (0), axis=0)
    gVertexArraySeparate = new_arr




def createVertexArraySeparate():
    varr = np.array([
            (0,0,1),         # v0 normal
            ( -1 ,  1 ,  1 ), # v0 position
            (0,0,1),         # v2 normal
            (  1 , -1 ,  1 ), # v2 position
            (0,0,1),         # v1 normal
            (  1 ,  1 ,  1 ), # v1 position

            (0,0,1),         # v0 normal
            ( -1 ,  1 ,  1 ), # v0 position
            (0,0,1),         # v3 normal
            ( -1 , -1 ,  1 ), # v3 position
            (0,0,1),         # v2 normal
            (  1 , -1 ,  1 ), # v2 position

            (0,0,-1),
            ( -1 ,  1 , -1 ), # v4
            (0,0,-1),
            (  1 ,  1 , -1 ), # v5
            (0,0,-1),
            (  1 , -1 , -1 ), # v6

            (0,0,-1),
            ( -1 ,  1 , -1 ), # v4
            (0,0,-1),
            (  1 , -1 , -1 ), # v6
            (0,0,-1),
            ( -1 , -1 , -1 ), # v7

            (0,1,0),
            ( -1 ,  1 ,  1 ), # v0
            (0,1,0),
            (  1 ,  1 ,  1 ), # v1
            (0,1,0),
            (  1 ,  1 , -1 ), # v5

            (0,1,0),
            ( -1 ,  1 ,  1 ), # v0
            (0,1,0),
            (  1 ,  1 , -1 ), # v5
            (0,1,0),
            ( -1 ,  1 , -1 ), # v4

            (0,-1,0),
            ( -1 , -1 ,  1 ), # v3
            (0,-1,0),
            (  1 , -1 , -1 ), # v6
            (0,-1,0),
            (  1 , -1 ,  1 ), # v2

            (0,-1,0),
            ( -1 , -1 ,  1 ), # v3
            (0,-1,0),
            ( -1 , -1 , -1 ), # v7
            (0,-1,0),
            (  1 , -1 , -1 ), # v6

            (1,0,0),
            (  1 ,  1 ,  1 ), # v1
            (1,0,0),
            (  1 , -1 ,  1 ), # v2
            (1,0,0),
            (  1 , -1 , -1 ), # v6

            (1,0,0),
            (  1 ,  1 ,  1 ), # v1
            (1,0,0),
            (  1 , -1 , -1 ), # v6
            (1,0,0),
            (  1 ,  1 , -1 ), # v5

            (-1,0,0),
            ( -1 ,  1 ,  1 ), # v0
            (-1,0,0),
            ( -1 , -1 , -1 ), # v7
            (-1,0,0),
            ( -1 , -1 ,  1 ), # v3

            (-1,0,0),
            ( -1 ,  1 ,  1 ), # v0
            (-1,0,0),
            ( -1 ,  1 , -1 ), # v4
            (-1,0,0),
            ( -1 , -1 , -1 ), # v7
            ], 'float32')
    return varr


def drawObj_glDrawArray():
    global gVertexArraySeparate
    varr = gVertexArraySeparate

    if gouraud:
        gouraud_shading()
    else:
        varr=reset
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(varr.size/6))
def drawBox():
    glBegin(GL_QUADS)
    glVertex3fv(np.array([1,1,0.]))
    glVertex3fv(np.array([-1,1,0.]))
    glVertex3fv(np.array([-1,-1,0.]))
    glVertex3fv(np.array([1,-1,0.]))
    glEnd()


def draw_hierarchial_model():
    global obj1,obj2,obj3
    glMatrixMode(GL_MODELVIEW)
    

    t = glfw.get_time()
    glPushMatrix()
 # minions drawing
    glPushMatrix()  
    glTranslatef(0,1.5,0)   
    glScalef(.5, .5, .5)
    glColor3ub(0, 0, 255)
    draw_obj(obj1)         
    glPopMatrix()      

    glPushMatrix()     
    glTranslatef(.5, 0, .01)
 # book drawing
    glPushMatrix()   
    glScalef(.05, .01, .05)
    glTranslatef(30,90,0)
    glRotatef(90,0,0,1)
    glRotatef(t*(180/np.pi), 0, 1, 0) 
    draw_obj(obj2)
    glPopMatrix()
# grenade drawing
    glPopMatrix()

    glTranslatef(-1.8,1.,0.)
    glScalef(.07,.07,.07)
    draw_obj(obj3)


    glPopMatrix()


def main():
    global gVertexArraySeparate,reset
    global obj1,obj2,obj3
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(640, 640, "main", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_drop_callback(window, drop_callback)
    glfw.set_key_callback(window, key_callback)
    gVertexArraySeparate = createVertexArraySeparate()
    reset = createVertexArraySeparate()
    # handle obj file
    obj1=handle_obj_file("minions.obj")
    obj2=handle_obj_file("book.obj")
    obj3=handle_obj_file("grenade.obj")
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
