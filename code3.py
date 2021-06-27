
import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
start_angle_x=np.radians(36.264)
start_angle_y=np.radians(-45)
gCamAng = 0.
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

# bvh arguments
hierarchy=[]
motion=[]
frame_time=0
frame_count=0
joint_name=[]
joint_count=1
file_modle=False
max_len=np.array([0.,0.,0.])
local_max=np.array([0.,0.,0.])
base_time=1

channel_number=0
frame_index=0
animate=False

def render():
    global  hierarchy, file_modle,channel_number
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
  #  glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
    
    # viewing camera
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    camera_setting(-30)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    drawPlateArray()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)

    glPushMatrix()
    lightPos = (3.,4.,5.,1.) 
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
    
    if file_modle:
        channel_number = 0
        draw_hierarchy(hierarchy)

    glDisable(GL_LIGHTING)




def drawPlate():
    glBegin(GL_LINES)
    glColor3ub(255, 255, 255)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([1., 0., 0.]))

    glVertex3fv(np.array([1., 0., 0.]))
    glVertex3fv(np.array([1., 0., 1.]))

    glVertex3fv(np.array([1., 0., 1.]))
    glVertex3fv(np.array([0., 0., 1.]))

    glVertex3fv(np.array([0., 0., 1.]))
    glVertex3fv(np.array([0., 0., 0.]))
    glEnd()


def drawPlateArray():
    for i in range(20):
        for j in range(20):
            glPushMatrix()
            glTranslatef(j-10, 0, i-10)
            drawPlate()
            glPopMatrix()

def drawCube(offset, normal):
    
    glBegin(GL_QUADS)
    glNormal3f(0, normal[1], 0)
    glVertex3f(offset[0], offset[1], - offset[2])
    glVertex3f(- offset[0], offset[1], - offset[2])
    glVertex3f(- offset[0], offset[1], offset[2])
    glVertex3f(offset[0], offset[1], offset[2])

    glNormal3f(0, -normal[1], 0)
    glVertex3f(offset[0], - offset[1], offset[2])
    glVertex3f(- offset[0], - offset[1], offset[2])
    glVertex3f(- offset[0], - offset[1], - offset[2])
    glVertex3f(offset[0], - offset[1], - offset[2])

    glNormal3f(0, 0, normal[2])
    glVertex3f(offset[0], offset[1], offset[2])
    glVertex3f(- offset[0], offset[1], offset[2])
    glVertex3f(- offset[0], - offset[1], offset[2])
    glVertex3f(offset[0], - offset[1], offset[2])

    glNormal3f(0, 0, -normal[2])
    glVertex3f(offset[0], - offset[1], - offset[2])
    glVertex3f(- offset[0], - offset[1], - offset[2])
    glVertex3f(- offset[0], offset[1], - offset[2])
    glVertex3f(offset[0], offset[1], - offset[2])

    glNormal3f(-normal[0], 0, 0)
    glVertex3f(- offset[0], offset[1], offset[2])
    glVertex3f(- offset[0], offset[1], - offset[2])
    glVertex3f(- offset[0], - offset[1], - offset[2])
    glVertex3f(- offset[0], - offset[1], offset[2])

    glNormal3f(normal[0], 0, 0)
    glVertex3f(offset[0], offset[1], - offset[2])
    glVertex3f(offset[0], offset[1], offset[2])
    glVertex3f(offset[0], - offset[1], offset[2])
    glVertex3f(offset[0], - offset[1], - offset[2])
    glEnd()



def camera_setting(begin):
    global trans_store, height_store, zoom
    gluPerspective(45, 1, 1, 100)
    
    glTranslate(0, 0, begin + zoom)
    x = height_store @ trans_store
    glMultMatrixf(x.T)

def set_hierarchy(f,head):
    global joint_name,joint_count,local_max,max_len

    local_max=np.array([0.,0.,0.])
    joint=[]
    joint.append(head)
    current_head=head
    while True:
        line=f.readline()
        if not line:
            break
        line=line.strip()
        line = line.replace('\t', ' ')
        tag = line.split(' ', 1)

        if tag[0] == 'ROOT':
            current_head = 'R'
        elif tag[0] == 'JOINT':
            current_head = 'J'
            joint_count += 1
            joint_name.append(tag[1])
        elif tag[0] == 'End':
            current_head = 'E'
        elif tag[0] == 'OFFSET':
            offset = tag[1].split(' ')
            offset_arr = np.array([np.float32(offset[0]), np.float32(offset[1]), np.float32(offset[2])])
            local_max += offset_arr
            joint.append(offset_arr)
        elif tag[0] == 'CHANNELS':
            num = tag[1].split(' ', 1)
            channels = num[1].split(' ')
            joint.append(channels)
        elif tag[0] == '{':
            child = set_hierarchy(f, current_head)
            joint.append(child)
        elif tag[0] == '}':
            max_len += abs(local_max)
            return joint

# store motion part
def set_motion(f):
    motions = []
    while True:
        temp = []
        line = f.readline()
        if not line:
            break
        line = line.rstrip()
        line = line.replace('\t', ' ')
        line = line.replace('\n', ' ')
        frame_motion = line.split(' ')
        for i in range(len(frame_motion)):
            temp.append(np.float32(frame_motion[i]))
        motions.append(temp)
    return motions
def get_offset(offset):
    temp = [0., 0., 0.]
    if offset[0] > 0:
        temp[0] = offset[0] + 0.02
    elif offset[0] < 0:
        temp[0] = offset[0] - 0.02
    else:
        temp[0] = 0.02

    if offset[1] > 0:
        temp[1] = offset[1] + 0.02
    elif offset[1] < 0:
        temp[1] = offset[1] - 0.02
    else:
        temp[1] = 0.02

    if offset[2] > 0:
        temp[2] = offset[2] + 0.02
    elif offset[2] < 0:
        temp[2] = offset[2] - 0.02
    else:
        temp[2] = 0.02
    normal = [temp[0] / abs(temp[0]), temp[1] / abs(temp[1]), temp[2] / abs(temp[2])]

    return temp, normal
def draw_hierarchy(input):
    global hierarchy, channel_number, motion, frame_index, animate, frame_count, max_len, frame_time, base_time

    model_len = max_len
    tag = input[0]
    offset = input[1]
    offset = offset / model_len

    glPushMatrix()

    temp = [offset[0]/2, offset[1]/2, offset[2]/2]
    temp_offset, normal = get_offset(temp)
    glTranslate(offset[0]/2, offset[1]/2, offset[2]/2)
    drawCube(temp_offset, normal)
    glTranslate(offset[0]/2, offset[1]/2, offset[2]/2)

    frame_index = int(((glfw.get_time() - base_time) / frame_time) % frame_count)

    if tag != 'E':
        child_num = len(input) - 3
        channel = input[2]
        if animate:
            for i in range(len(channel)):
                if channel[i].upper() == 'XPOSITION':
                    xpos = motion[frame_index][channel_number]
                    xpos = xpos / model_len[0]
                    channel_number += 1
                    glTranslate(xpos, 0, 0)
                elif channel[i].upper() == 'YPOSITION':
                    ypos = motion[frame_index][channel_number]
                    ypos = ypos / model_len[1]
                    channel_number += 1
                    glTranslate(0, ypos, 0)
                elif channel[i].upper() == 'ZPOSITION':
                    zpos = motion[frame_index][channel_number]
                    zpos = zpos / model_len[2]
                    channel_number += 1
                    glTranslate(0, 0, zpos)
                elif channel[i].upper() == 'XROTATION':
                    xrot = motion[frame_index][channel_number]
                    channel_number+= 1
                    glRotate(xrot, 1, 0, 0)
                elif channel[i].upper() == 'YROTATION':
                    yrot = motion[frame_index][channel_number]
                    channel_number += 1
                    glRotate(yrot, 0, 1, 0)
                elif channel[i].upper() == 'ZROTATION':
                    zrot = motion[frame_index][channel_number]
                    channel_number += 1
                    glRotate(zrot, 0, 0, 1)
        for i in range(child_num):
            draw_hierarchy(input[i + 3])

    glPopMatrix()

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
    global animate, base_time
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_SPACE:
            if animate is True:
                animate = False
                base_time = 1
            else:
                animate = True
                base_time = glfw.get_time()

def drop_callback(window,path):
    global hierarchy,motion,frame_count,frame_time,joint_count,joint_name,\
        file_modle,max_len,max_len,base_time
    read_path=path[0].split('/')
    file_name=read_path[-1]
    f=open(path[0],'r')
   #initialise    
    file_modle=True
    hierarchy=[]
    motion=[]
    frame_count=0
    frame_time=0
    join_count=1
    joint_name=[]
    max_len=np.array([0.,0.,0.])

    while True:
        line=f.readline()
        if not line:
            break
        line=line.rstrip()
        tag=line.split(' ',1)
        if tag[0]=='HIERARCHY':
            line=f.readline()
            line=line.rstrip()
            line=line.replace('\t',' ')
            root=line.split(' ',1)
            joint_name.append(root[1])
            f.readline()
            hierarchy=set_hierarchy(f,'R')
        elif tag[0]=='MOTION':
            line=f.readline()
            line=line.rstrip()
            line=line.replace('\t',' ')
            tag=line.split(' ',1)
            frame_count=int(tag[1])

            line=f.readline()
            line=line.rstrip()
            line=line.replace("\t",' ')
            tag=line.split(' ',2)
            frame_time=np.float32(tag[2])
            motion=set_motion(f)
    print("########################")
    print("file name: ",file_name)
    print("Number of frames: ",frame_count)
    print("FPS(which is 1/FrameTime): ",1 /frame_time)
    print("Number of joints (including root): ",join_count)
    print("List of all joint names: ",joint_name)
    base_time=glfw.get_time()

def main():
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(640, 640, "main", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_drop_callback(window, drop_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)
    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Poll for and process events
        glfw.poll_events()
        render()
        # Swap front and back buffers
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
