#!/usr/bin/python
from vec3 import vec3
import math

class triangle_list:
    def __init__(self):
        self.coords = {} #maps vec3 to index
        self.indices = []
        self.max_index = 0

    def append(self, t):
        v1, v2, v3 = t
        i1, i2, i3 = 0, 0, 0
        if v1 in self.coords:
            i1 = self.coords[v1]
        else:
            i1 = self.max_index
            self.max_index += 1
            self.coords[v1] = i1
        if v2 in self.coords:
            i2 = self.coords[v2]
        else:
            i2 = self.max_index
            self.max_index += 1
            self.coords[v2] = i2
        if v3 in self.coords:
            i3 = self.coords[v3]
        else:
            i3 = self.max_index
            self.max_index += 1
            self.coords[v3] = i3
        self.indices.append((i1, i2, i3))


    def write_obj(self):
        verts = sorted(self.coords.items(), key=lambda x: x[1])
        for v in verts:
            print(v)
            print("v {0} {1} {2}\n".format(v.x, v.y, v.z))
        for f in self.indices:
            print("f {0} {1} {2}\n".format(f[0], f[1], f[2]))

    def write_off(self):
        print("OFF")
        num_verts = len(self.coords)
        num_faces = len(self.indices)
        num_edges = 0 #irrelevant
        print("{0} {1} {2}".format(num_verts, num_faces, num_edges))
        verts = sorted(self.coords.items(), key=lambda x: x[1])
        for v in verts:
            v, x = v
            print_vec3(v)
        for i in self.indices:
            print_triangle_indices(i)

    def write_off_color(self):
        print("OFF")
        num_verts = len(self.coords)
        num_faces = len(self.indices)
        num_edges = 0 #irrelevant
        print("{0} {1} {2}".format(num_verts, num_faces, num_edges))
        verts = sorted(self.coords.items(), key=lambda x: x[1])
        for v in verts:
            v, x = v
            print_vec3_color(v)
        for i in self.indices:
            print_triangle_indices(i)

class dumb_triangle_list:
    def __init__(self):
        self.coords = []
    
    def append(self, t):
        v1, v2, v3 = t
        self.coords.append(v1)
        self.coords.append(v2)
        self.coords.append(v3)
    
    def write_off(self):
        print("OFF")
        num_verts = len(self.coords)
        num_faces = len(self.coords)/3
        num_edges = 0 #irrelevant
        print("{0} {1} {2}".format(num_verts, num_faces, num_edges))
        for v in self.coords:
            print_vec3(v)
        for i in range(len(self.coords)/3):
            print_triangle_indices((3*i, 3*i+2, 3*i+1))


def print_vec3(vec):
    print("{0} {1} {2}".format(vec.x, vec.y, vec.z))
def print_vec3_color(vec):
    print("{0} {1} {2} {3} {4} {5}".format(vec.x, vec.y, vec.z, 0.5 * math.sin(vec.x) + 0.5, 0.5 * math.sin(vec.y) + 0.5, 0.5 * math.sin(vec.z) + 0.5 ))
def print_triangle_indices(i):
    a,b,c = i
    print("3 {0} {1} {2}".format(a,b,c))

if __name__ == "__main__":
    t = dumb_triangle_list()
    v1 = vec3(0,0,0)
    v2 = vec3(0,1,0)
    v3 = vec3(1,1,0)
    v4 = vec3(0,0,0.5)
    t.append((v1, v2, v3))
    t.append((v1, v3, v4))
    t.append((v1, v2, v4))
    t.append((v2, v3, v4))
    t.write_off()
