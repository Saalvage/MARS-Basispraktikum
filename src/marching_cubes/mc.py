#!/usr/bin/python
import os
import math
from vec3 import vec3, vec_from_list
import cube
import off

ISOVAL = 1  # iso-value
SUBDIV = 32  # resolution

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

def march_cubes():
    pass

march_cubes()

