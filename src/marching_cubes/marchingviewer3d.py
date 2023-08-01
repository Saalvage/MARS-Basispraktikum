import pyvista as pv
import random
import numpy as np
from math import *

class viewer3d:

    def __init__(self):
        self.p = pv.Plotter(window_size=[1200, 800])

    def show(self):
        self.p.add_axes()
        self.p.show()

    def get_marching_data(self, vertices, faces):
        colors = []
        verts = []
        for vert in vertices:
            colors.append((0.5 * sin(vert.x) + 0.5, 0.5 * sin(vert.y) + 0.5, 0.5 * sin(vert.z) + 0.5 ))
            verts.append((vert.x, vert.y, vert.z))
        
        return verts, faces, colors

    def display_marching_cube(self, mc, offset):
        vertices, faces, colors = self.get_marching_data(mc.vertices, mc.faces)  
        mesh = pv.PolyData(np.array([[v[0] + offset.x, v[1] + offset.y, v[2] + offset.z] for v in vertices]) , np.array(faces))
        mesh.point_data["colors"] = np.array(colors)
        self.p.add_mesh(mesh, show_edges=True, line_width=1, scalars="colors", preference='cell', rgb=True)

    # only works after implementing normals in task 5
    # shows normal of bezier patch
    def display_normals(self, bpatches, offset):
        arrow_start = []
        arrow_dir = []

        patches = bpatches.patches
        for i in range(len(patches)):
            vec = patches[i].control_points[0][0] + offset
            arrow_start.append([vec.x, vec.y, vec.z])
            vec = patches[i].normal(0, 0)
            arrow_dir.append([vec.x, vec.y, vec.z])
        self.p.add_arrows(np.array(arrow_start), np.array(arrow_dir), mag=1)

    def display_points(self, cps, offset, color):
        points = []
        for pt in cps:
            points.extend([pt.x + offset.x, pt.y + offset.y, pt.z + offset.z])
        cps = pv.PolyData(np.array(points) )
        self.p.add_points(cps, point_size=10, color=color)

    def add_text(self, text):
        self.p.add_text(text, position="upper_left", color="white", font_size=15)