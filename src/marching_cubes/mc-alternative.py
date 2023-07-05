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

    return data

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

