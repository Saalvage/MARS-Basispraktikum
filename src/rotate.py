#!/usr/bin/python

from cagd.polyline import polyline
from cagd.spline import spline, spline_surface, knots
from cagd.bezier import bezier_surface, bezier_patches
from cagd.vec import vec2, vec3
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
#you can activate these lines to view the input spline
#spl.set_color("#0000ff")
#sc = scene_2d.scene()
#sc.set_resolution(900)
#sc.add_element(spl)
#sc.write_image()
#sc.show()

surface = spl.generate_rotation_surface(6)

bezier_patches = surface.to_bezier_patches()

bezier_patches.refine(2)
path = "surfaces.off"
f = open(path, 'w')
f.write(bezier_patches.export_standard_off())
f.close()
