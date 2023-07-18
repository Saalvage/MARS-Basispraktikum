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
SHOW_SINGLE = True

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
        
    net = [[[None for _ in range(2 * length * subdiv)] for _ in range(2 * length * subdiv)] for _ in range(2 * length * subdiv)]
    
    for i in range(len(net)):
        for j in range(len(net[i])):
            for k in range(len(net[j])):
                net[i][j][k] = function((1/subdiv) * vec3(i - length, j - length, k - length)) - isoval

    
    bitflags = [[[None for _ in range(2 * length * subdiv - 1)] for _ in range(2 * length * subdiv - 1)] for _ in range(2 * length * subdiv - 1)]
    
    for i in range(len(bitflags)):
        for j in range(len(bitflags[i])):
            for k in range(len(bitflags[j])):
                flag = [0 for i in range(8)]
                
                if net[i    ][j    ][k    ] > 0: flag[0] = 1
                if net[i + 1][j    ][k    ] > 0: flag[1] = 1
                if net[i    ][j + 1][k    ] > 0: flag[2] = 1
                if net[i + 1][j + 1][k    ] > 0: flag[3] = 1
                
                if net[i    ][j    ][k + 1] > 0: flag[4] = 1
                if net[i + 1][j    ][k + 1] > 0: flag[5] = 1
                if net[i    ][j + 1][k + 1] > 0: flag[6] = 1
                if net[i + 1][j + 1][k + 1] > 0: flag[7] = 1
                
                bitflags[i][j][k] = flag
                
    for i in range(len(bitflags)):
        for j in range(len(bitflags[i])):
            for k in range(len(bitflags[j])):
                edge_bitflag = to_edge_bitflag(bitflag=bitflags[i][j][k])
                triangels = cube.CubeTriangles[bitflag_to_int(bitflags[i][j][k])]
                vertices = [None for _ in range(12)]
                
                for e in range(len(edge_bitflag)):
                    if edge_bitflag[e] == 1:
                        x1, y1, z1 = edge_offset(cube.CubeEdges[e][0]) 
                        x2, y2, z2 = edge_offset(cube.CubeEdges[e][1]) 
                        
                        v_1 = net[i+x1][j+y1][k+z1]
                        v_2 = net[i+x2][j+y2][k+z2]
                        
                        p_1 = (1.0 / subdiv) * vec3(i + x1 - length, j + y1 - length, k+ z1 - length)
                        p_2 = (1.0 / subdiv) * vec3(i + x2 - length, j + y2 - length, k+ z2 - length)
                        
                        vertices[e] = (v_1 * p_2) - (v_2 * p_1) * (1.0 / (v_1 - v_2))
                        # print(  f"vertex value = {vertices[e]}\n"
                        #       + f"v_1 = {v_1}\tv_2 = {v_2}\n"
                        #       + f"p_1 = {p_1}\tp_2 = {p_2}\n")

                count = 0
                while(triangels[count]!= -1):
                    v_len = len(marching.vertices)
                    temp = [3, triangels[count] + v_len, triangels[count + 1] + v_len, triangels[count + 2] + v_len]

                    marching.faces += temp
                    marching.vertices += [vertices[temp[1] - v_len]]
                    marching.vertices += [vertices[temp[2] - v_len]]
                    marching.vertices += [vertices[temp[3] - v_len]]
                    count += 3
    
    return data

def bitflag_to_int(bitflag):
    bitflag_int = 0
    for i in range(len(bitflag)):
        if bitflag[i] == 1:
            bitflag_int += 2 ** i
    return bitflag_int

def to_edge_bitflag(bitflag):
    edge_bitflag = [0 for _ in range(12)]
    count = 0
    for verts in cube.CubeEdges:
        if bitflag[verts[0]] != bitflag[verts[1]]:
            edge_bitflag[count] = 1
        count += 1
        
    return edge_bitflag

def edge_offset(point):
    if point == 0: return (0, 0, 0)
    if point == 1: return (1, 0, 0)
    if point == 2: return (1, 1, 0)
    if point == 3: return (0, 1, 0)
    
    if point == 4: return (0, 0, 1)
    if point == 5: return (1, 0, 1)
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

