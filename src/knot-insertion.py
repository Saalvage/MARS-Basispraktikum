#!/usr/bin/python

from cagd.polyline import polyline
from cagd.spline import spline, knots
from cagd.vec import vec2
import cagd.scene_2d as scene_2d

s1 = spline(3)
s1.control_points = [vec2(0, 0), vec2(0, 1), vec2(1, 1), vec2(1, 0), vec2(2, 0)]
s1.knots = knots(9)
s1.knots.knots = [0, 0, 0, 0, 1, 2, 2, 2, 2]
p1 = s1.get_polyline_from_control_points()
s1.set_color("blue")
p1.set_color("red")

s2 = s1
s2.insert_knot(0.5)
s2.insert_knot(1)
s2.insert_knot(1.5)
p2 = s2.get_polyline_from_control_points()
s2.set_color("green")
p2.set_color("yellow")

sc = scene_2d.scene()
sc.set_resolution(900)

sc.add_element(s1)
sc.add_element(p1)
sc.add_element(s2)
sc.add_element(p2)

sc.write_image()
sc.show()
sc.write_to_file("inserted.png")
