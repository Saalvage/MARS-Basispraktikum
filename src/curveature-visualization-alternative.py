#!/usr/bin/python

from cagd.spline import spline, spline_surface, knots
from cagd.bezier import bezier_surface, bezier_patches
from cagd.vec import vec2, vec3
from cagd.viewer3d import viewer3d
import multiprocessing 
import os
from cagd.point import point2D





# if True only show a single object otherwise show all objects
show_single = True
# if True use figure from task 3 otherwise use deformed plane
figure = False

# parallel compute curvature visualization 
def visualize_curvature(data):
    data[0].visualize_curvature(data[1], data[2])
    return data

def get_surface():
    if figure:
        pts = [ vec2(0.05,5.5),
        vec2(1.5,5),
        vec2(2,4),
        vec2(1.7,2.5),
        vec2(0.7,1.8),
        vec2(2,1.3),
        vec2(2,0.9),
        vec2(1.2,0.8),
        vec2(.7,0.4),
        vec2(.7,-1),
        vec2(.7,-2.8),
        vec2(2,-4),
        vec2(2,-4.6),]

        spl = spline.interpolate_cubic(spline.INTERPOLATION_CHORDAL, pts, knots(1))
        surface = spl.generate_rotation_surface(6)
    else: 
        f = lambda x,y: x*x/5 + x*y/4 + 10/(1+x*x+y*y) + y/2
        ctrl_pts = [[vec3(x, y, f(x,y)) for x in range(-5, 5)] for y in range(-5, 5)]

        d = 3
        m = d + len(ctrl_pts) + 1
        ku = knots(m)
        kv = knots(m)
        for i in range(d):
            ku[i] = 0
            kv[i] = 0
        for i in range(m - d - d):
            ku[i + d] = i
            kv[i + d] = i
        for i in range(d):
            ku[i + m - d] = m - d - d - 1
            kv[i + m - d] = m - d - d - 1

        surface = spline_surface((d,d))
        surface.control_points = ctrl_pts
        surface.knots = (ku, kv)

    return surface


if __name__ == "__main__":
    surface = get_surface()

    v = viewer3d()
    bezier_patches = surface.to_bezier_patches()
    bezier_patches.refine(1)

    if (not show_single):
        v.add_text("                                        CURVATURE_GAUSSIAN          CURVATURE_AVERAGE          CURVATURE_PRINCIPAL_MAX          CURVATURE_PRINCIPAL_MIN \
            \n\n\n\n\n\n\n\nCOLOR_MAP_LINEAR\n\n\n\n\n\n\n\nCOLOR_MAP_CUT\n\n\n\n\n\n\n\nCOLOR_MAP_CLASSIFICATION")

        threads = []
        bpatches = []
        indexes = []
        inputData = []
        for i in range(4):
            for j in range(4, 7):
                inputData.append((bezier_patches, i, j))

        p = multiprocessing.Pool(os.cpu_count())
        data = p.map(visualize_curvature, inputData)

        for d in data:
            i = d[1]
            j = d[2]
            v.display_object(d[0], vec3(-10 * i + 10 * j, 10 * i + 10 * j,0))

        p.close()
        v.show()

    else:
        cps = []
        for i in range(128, 129): 
            for pt in bezier_patches.patches[i].control_points[0]:
                cps.append(pt)

        v.display_points(cps, vec3(0,0,0), "black")
        bezier_patches.visualize_curvature(bezier_patches.CURVATURE_GAUSSIAN, bezier_patches.COLOR_MAP_LINEAR)
        v.display_normals(bezier_patches, vec3(0,0,0))

        v.display_object(bezier_patches, vec3(0,0,0))
        v.show()