#!/usr/bin/python

from cagd.polyline import polyline
from cagd.spline import spline, knots
from cagd.vec import vec2
import cagd.scene_2d as scene_2d

pts = [vec2(0,.4), vec2(.8,.8), vec2(.5,1.2), vec2(-.03,.4), vec2(.4,0), vec2(1,.2)]
s1 = spline.interpolate_cubic(spline.INTERPOLATION_CHORDAL, pts, knots(1))

#pts = [vec2(0, 2.5), vec2(-1, 1), vec2(1, -1), vec2(0, -2.5), vec2(-1, -1), vec2(1, 1)]
#s1 = spline.interpolate_cubic_periodic(pts)

s1.set_color("#0000ff")

sc = scene_2d.scene()
sc.set_resolution(900)

for i in [-1, 1]:
    para = s1.generate_parallel(i * 0.025, 0.005)
    para.set_color("#999999")
    sc.add_element(para)

sc.write_image()
sc.show()
