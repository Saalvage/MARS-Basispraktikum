import pyvista as pv
import random
import numpy as np


class viewer3d:

    def __init__(self):
        self.p = pv.Plotter(window_size=[1200, 800])

    def show(self):
        self.p.add_axes()
        self.p.show()

    def get_data(self, patches):
        def avg_color(f_cs):
            avg_f_c = [0, 0, 0]
            for f_c in f_cs:
                avg_f_c[0] += f_c[0]
                avg_f_c[1] += f_c[1]
                avg_f_c[2] += f_c[2]
            return (round(255 * avg_f_c[0] / 4),
                    round(255 * avg_f_c[1] / 4),
                    round(255 * avg_f_c[2] / 4))

        vertices = []
        faces = []
        colors = []

        for patch in patches:
            for v_row in patch.control_points:
                for vertex in v_row:
                    vertices.append([vertex.x, vertex.y, vertex.z])

        start_v = 0
        for patch in patches:
            cps = patch.control_points
            row_num = len(cps)
            col_num = len(cps[0])
            for row in range(row_num - 1):
                for col in range(col_num - 1):
                    first_v = start_v + row * col_num + col
                    f_vertices = [4, first_v, first_v + 1, first_v + 1 + col_num, first_v + col_num]
                    faces.extend(f_vertices)
                    colors.append(avg_color(patch.color))
            start_v += 16

        return vertices, faces, colors

    def display_object(self, obj, offset):
        vertices, faces, colors = self.get_data(obj.patches)
        mesh = pv.PolyData(np.array([[v[0] + offset.x, v[1] + offset.y, v[2] + offset.z] for v in vertices]),
                           np.array(faces))
        mesh.add_field_data(np.array(colors), "colors")
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
        cps = pv.PolyData(np.array(points))
        self.p.add_points(cps, point_size=10, color=color)

    def add_text(self, text):
        self.p.add_text(text, position="upper_left", color="white", font_size=15)
