#!/usr/bin/python
from vec3 import vec3, vec_from_list
import cube
from marchingviewer3d import viewer3d
import multiprocessing 

class marching:
    # Add funtions to calculate the vertices and faces of the 3D object.
    # A 3D model consists of multiple polygons.  A polygon consists of vertices 
    # which are vec3 points and faces which are the indexes of the vertices.
    # A face of a polygon starts with the amount of points per polygon, for this task it wil always be 3.
    #
    # For example a square made of two polygons could be:
    # vertices = [vec3(0, 0, 0), vec3(1, 0, 0), vec3(1, 1, 0), vec3(0, 1, 0)]
    # faces = [3, 0, 1, 2, 3, 3, 1, 2]
    # 4 vertices as corners for the square and the faces start with a three 
    # followed by three indexes corresponding to the vertice list
    # https://docs.pyvista.org/version/stable/examples/00-load/create-poly.html

    def __init__(self):
        self.vertices = []
        self.faces = []

LENGTH = 1
ISOVAL = 1  # iso-value
SUBDIV = 32  # resolution
SHOW_SINGLE = False

def sphere(vec):
    return abs(vec)

def octahedron(vec):
    return abs(vec.x) + abs(vec.y) + abs(vec.z)

def cube_func(vec):
    return max(max(abs(vec.x), abs(vec.y)), abs(vec.z))

def torus(vec):
    x = vec.x
    y = vec.y
    z = vec.z
    c = x*x + y*y + z*z + .7*.7 - .2*.2
    d = 4 * .7*.7 * ( x*x + y*y)
    return c*c - d

# calculate vertices and faces of marching
def march_cubes(data):
    marching = data[0]
    length = data[1]
    subdiv = data[2]
    isoval = data[3]
    function = data[4]
        
    net = [[[None for _ in range(subdiv+1)] for _ in range(subdiv+1)] for _ in range(subdiv+1)]
    
    # calculate values of the function
    for i in range(subdiv+1):
        for j in range(subdiv+1):
            for k in range(subdiv+1):
                net[i][j][k] = function(vec3((2.0 * length / subdiv) * i - length,
                                             (2.0 * length / subdiv) * j - length,
                                             (2.0 * length / subdiv) * k - length))
    
    for i in range(len(net) - 1):
        for j in range(len(net) - 1):
            for k in range(len(net) - 1):
                cube_flag = [1 for _ in range(8)]
                
                # calculate cube bitflag
                for p in range(8):
                    x, y, z = corner_offset(p)
                    if net[i + x][j + y][k + z] - isoval >= 0.0: cube_flag[p] = 0
                
                # if the cube is empty, skip
                int_cube_flag = bitflag_to_int(cube_flag)
                if int_cube_flag == 0 or int_cube_flag == 255:
                    continue
                
                # init the array a and load in triangle list
                a_array = [None for _ in range(12)]
                triangle_list = cube.CubeTriangles[int_cube_flag]
                
                for v in range(len(cube.CubeEdges)):
                    vert_1 = cube.CubeEdges[v][0]
                    vert_2 = cube.CubeEdges[v][1]
                    
                    # skip edges without intersection
                    if cube_flag[vert_1] == cube_flag[vert_2]:
                        continue
                    
                    # calculate the intersection point and load it into the array a 
                    x1, y1, z1 = corner_offset(vert_1) 
                    x2, y2, z2 = corner_offset(vert_2)
                    
                    v_1 = net[i + x1][j + y1][k + z1] - isoval
                    v_2 = net[i + x2][j + y2][k + z2] - isoval
                    
                    p_1 = vec3((2.0 * length / subdiv) * (i + x1) - length, (2.0 * length / subdiv) * (j + y1) - length, (2.0 * length / subdiv) * (k + z1) - length)
                    p_2 = vec3((2.0 * length / subdiv) * (i + x2) - length, (2.0 * length / subdiv) * (j + y2) - length, (2.0 * length / subdiv) * (k + z2) - length)
                    
                    a_array[v] = ((v_1 * p_2) - (v_2 * p_1)) * (1.0 / (v_1 - v_2))               
                    
                # add vertices and faces
                count = 0
                while(triangle_list[count]!= -1):
                    v_len = len(marching.vertices)
                    temp = [3, v_len, 1 + v_len, 2 + v_len]
                    
                    marching.faces += [temp]
                    marching.vertices.append(a_array[triangle_list[count]])
                    marching.vertices.append(a_array[triangle_list[count + 1]])
                    marching.vertices.append(a_array[triangle_list[count + 2]])
                    
                    count += 3
    return data

# translates a bitflag into an integer
def bitflag_to_int(bitflag):
    bitflag_int = 0
    for i in range(len(bitflag)):
        if bitflag[i] == 1:
            bitflag_int += 2 ** i
    return bitflag_int

def corner_offset(point):
    if point == 0: return (0, 0, 0)
    if point == 1: return (1, 0, 0)
    if point == 2: return (1, 0, 1)
    if point == 3: return (0, 0, 1)
    
    if point == 4: return (0, 1, 0)
    if point == 5: return (1, 1, 0)
    if point == 6: return (1, 1, 1)
    if point == 7: return (0, 1, 1)
    
    RuntimeError("Assertion not met")

if __name__ == "__main__":
    if SHOW_SINGLE:
        mc = marching()
        march_cubes((mc, LENGTH, SUBDIV, ISOVAL, sphere))

        v = viewer3d()
        v.display_marching_cube(mc, vec3(0,0,0))
        v.show()
    else:
        mc = marching()
        inputData = [(mc, LENGTH, SUBDIV, ISOVAL, cube_func), 
                     (mc, LENGTH, SUBDIV, ISOVAL, sphere), 
                     (mc, LENGTH, SUBDIV, ISOVAL, octahedron), 
                     (mc, LENGTH, SUBDIV, 0, torus)]
        
        p = multiprocessing.Pool(4)
        data = p.map(march_cubes, inputData)

        v = viewer3d()
        v.display_marching_cube(data[0][0], vec3(0,0,0))
        v.display_marching_cube(data[1][0], vec3(-2,2,0))
        v.display_marching_cube(data[2][0], vec3(2,2,0))
        v.display_marching_cube(data[3][0], vec3(0,4,0))

        v.show()

