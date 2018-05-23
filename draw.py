from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import math
import time

lines = ""
vertexes = ""

#function to find the vertexes and line
def read_data(path=None):
    if not path:
        path = "C:/Users/prave/PycharmProjects/CG-HW/house.d.txt"    #Set the path of house.d.txt file
    _sum = []
    vertexes = []
    lines = []
    _first_line = 1
    no_of_vertexes = 0
    #To find the number of vertexes from the given file
    with open(path) as f:
        for data in f.readlines():
            data = data.strip('\n')
            nums = data.split(" ")
            # Reading the first line i.e. data 10 7
            if _first_line:
                for re in nums:
                    if re:
                        _sum.append(re)
                _first_line = 0
                continue
            # _sum=[data 10 7]
            no_of_vertexes = int(_sum[1]) #storing 10 i.e. number of vetexes to vertex_line

    # read vertexes and lines
    with open(path) as f:
        i = 1
        for data in f.readlines():
            data = data.strip('\n')
            nums = data.split(" ")
            if i:
                i = 0
                continue
            if no_of_vertexes:
                vertex = []
                #storing each x,y,z coordinates into vertex
                for re in nums:
                    if re:
                        vertex.append(float(re))
                #sotring all the vertexes coordiantes into vertexes
                vertexes.append(vertex)
                no_of_vertexes-= 1
                continue

            # lines
            line = []
            for li in nums:
                if li:
                    line.append(int(li)-1) #Subtracting each coordinate by 1, since indexing starts from 0
            lines.append(line[1:])

    return vertexes, lines

#Function to find M perspective and M view
def FindPersView(c, p, v_prime, d=1.0, f=500.0, h=15.0):
    C = np.mat(c)
    P = np.mat(p)
    # N = 1/math.sqrt((P-C)*(P-C).T) * (P-C), is re-written as:
    N = (P-C) / np.linalg.norm(P - C)  # Denotes Z-axis
    N = N.tolist()[0]
    U = cross_product(N, v_prime) / np.linalg.norm(cross_product(N, v_prime))  # X-axis
    V = cross_product(U, N)  # Y-axis
    U = U.tolist()
    print "Calculated values:"
    print "V':", v_prime
    print "N:", N
    print "U:", U
    print "V:", V
    U_val = U + [0]
    V_val = V + [0]
    N_val = N + [0]
    R = np.mat([U_val, V_val, N_val, [0, 0, 0, 1]])
    T = np.mat([[1, 0, 0, -c[0]], [0, 1, 0, -c[1]], [0, 0, 1, -c[2]], [0, 0, 0, 1]])
    print "R:"
    print R
    print "T:"
    print T
    M_view = R * T
    #Calculating M view
    print "M_view:"
    print M_view
    #Calculating M perspective
    M_pers = np.mat([[d/h, 0, 0, 0], [0, d/h, 0, 0], [0, 0, f/(f-d), -d*f/(f-d)], [0, 0, 1, 0]])
    print "M_pers:"
    print M_pers
    return M_view, M_pers

#Function to perform the transformation
def transformation(c, p, v_prime, d=1.0, f=500.0, h=15.0, divide_w=False):
    M_view, M_pers = FindPersView(c, p, v_prime, d, f, h)
    vertexes, lines = read_data()
    # Mview * points
    view_vs = []
    for v in vertexes:
        v = v + [1]
        v = np.mat(v).T    #Self Transpose
        view_v = M_view * v
        view_v = view_v.T.tolist()[0]
        view_vs.append(view_v)
    print view_vs
    # To find normal of the surface
    print "Visible"
    VisibleSurface = []
    for face in lines:
        ves = []
        for v in face:
            ves.append(view_vs[v])
        i = np.mat(ves[0])
        j = np.mat(ves[1])
        k = np.mat(ves[2])
        line1 = j - i
        line2 = k - j
        line_of_sight = (np.mat(c) - np.mat(ves[0][:-1])).tolist()[0]
        vertex1 = line1.tolist()[0][0:-1]
        vertex2 = line2.tolist()[0][0:-1]
        normal = cross_product(vertex1, vertex2)
        print "Normal:", normal
        visible = vertex_dot_multiply(normal, line_of_sight)
        print "Visible:", visible
        if visible > 0:
            VisibleSurface.append(face)
        print VisibleSurface

    new_vs = []
    for v in vertexes:
        v = v + [1]
        v = np.mat(v).T
        new_v = M_pers * M_view * v
        new_v = new_v.T.tolist()[0]   # lists
        if divide_w:
            # Dividing x,y,z by W
            new_v[0] = new_v[0] / new_v[-1]
            new_v[1] = new_v[1] / new_v[-1]
            new_v[2] = new_v[2] / new_v[-1]
        print new_v
        new_vs.append(new_v)
    return new_vs, VisibleSurface


#funtion to perform cross product
def cross_product(a, b):
    """a*b cross product"""
    ax = a[0]
    ay = a[1]
    az = a[2]
    bx = b[0]
    by = b[1]
    bz = b[2]
    cx = ay*bz - az*by
    cy = az*bx - ax*bz
    cz = ax*by - ay*bx
    return [cx, cy, cz]

#function to perform dot product
def vertex_dot_multiply(a, b):
    ax = a[0]
    ay = a[1]
    az = a[2]
    bx = b[0]
    by = b[1]
    bz = b[2]
    return ax*bx + ay*by + az*bz


def init(d):
    glClearColor(0.0, 0.0, 0.0, 1.0)
    gluOrtho2D(-d, d, -d, d)


def draw_func():
    global lines
    global vertexes
    # lines
    for line in lines:
        ves = []
        for l in line:
            ves.append(vertexes[l])  # ves is the 3 vertexes in a face
        glColor3f(1.0, 0.0, 0.0)
        glLineWidth(1.0)
        glBegin(GL_LINE_LOOP)

        for v in ves:
            glVertex2f(v[0], v[1])
        glEnd()
        glFlush()
        time.sleep(1)


def draw(C, P, V_prime, d, f, h, GraphSize, divide_w):
    global lines
    global vertexes
    # init data

    vertexes, lines = transformation(C, P, V_prime, d, f, h, divide_w)
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_SINGLE)
    glutInitWindowSize(400, 400)
    glutCreateWindow("lab1")
    glutDisplayFunc(draw_func)
    init(GraphSize)
    glutMainLoop()


#Change Camera position as required by changing the vlaues of C. For example, C=[-10,-10,10] or  C = [-10, 10, -10] etc.
if __name__ == '__main__':
    # init data
    d = 3.8
    f = 1
    h = 0.5
    GraphSize = 4
    C = [-0.5,-0.22,-2.3]  # Camera position
    P = [10.0, 12.0, 40.0]
    V_prime = [0, 0.5, 0]  # V' co-ordinates, Y-direction of Camera
    draw(C, P, V_prime, d, f, h, GraphSize, True)
