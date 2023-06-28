#!/usr/bin/python

from cagd.polyline import polyline
from cagd.spline import spline, spline_surface, knots
from cagd.bezier import bezier_surface, bezier_patches
from cagd.vec import vec2, vec3
from cagd.viewer3d import viewer3d
#from cagd.point import point2D

import cagd.scene_2d as scene_2d


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
spl.set_color("#0000ff")
sc = scene_2d.scene()
sc.set_resolution(900)
sc.add_element(spl)

#for pt in spl.control_points:
#    sc.add_element(point2D(pt, "green"))

surface = spl.generate_rotation_surface(8)
    
v = viewer3d()
# show controlpoints of rotated surface
# cps = [pt for pts in surface.control_points for pt in pts]
# v.display_points(cps, vec3(0,0,0), "red")


bezier_patches = surface.to_bezier_patches()
# show points of bezier patches
cps = [pt for pts in surface.control_points for pt in pts]
v.display_points(cps, vec3(0,0,0), "green")
#v.display_object(bezier_patches, vec3(0,0,0))

# bezier_patches.refine(2)
# show refined object
# v.display_object(bezier_patches, vec3(-5,5,0))
v.show()