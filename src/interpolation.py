#!/usr/bin/python

from cagd.polyline import polyline
from cagd.spline import spline, knots
from cagd.vec import vec2
import cagd.scene_2d as scene_2d

#create an example spline to demonstrate how to create a spline
#you can use this to test your implementation of the de-boor algorithm 
#    and the knot_index function
example_spline = spline(3)
example_spline.control_points = [vec2(0,0), vec2(0,1), vec2(1,1), vec2(1, 0), vec2(2,0)]
example_spline.knots = knots(9)
example_spline.knots.knots = [0, 0, 0, 0, 1, 2, 2, 2, 2]
p = example_spline.get_polyline_from_control_points()
p.set_color("red")

#interpolate six points with the four different interpolation options to
#    draw a small letter "e"
#uncomment these lines once you implemented the spline interpolation
#pts = [vec2(0,.4), vec2(.8,.8), vec2(.5,1.2), vec2(-.03,.4), vec2(.4,0), vec2(1,.2)]
#s1 = spline.interpolate_cubic(spline.INTERPOLATION_EQUIDISTANT, pts, knots(1))
#s2 = spline.interpolate_cubic(spline.INTERPOLATION_CHORDAL, pts, knots(1))
#s3 = spline.interpolate_cubic(spline.INTERPOLATION_CENTRIPETAL, pts, knots(1))
#s4 = spline.interpolate_cubic(spline.INTERPOLATION_FOLEY, pts, knots(1))
#s1.set_color("#000066")
#s2.set_color("#0000aa")
#s3.set_color("#6666ff")
#s4.set_color("#aaaaff")
#p = polyline()
#p.points = pts
#p.set_color("red")

#generate a scene and add elements to it
sc = scene_2d.scene()
sc.set_resolution(900)
sc.add_element(example_spline)
sc.add_element(p)
#sc.add_element(s1)
#sc.add_element(s2)
#sc.add_element(s3)
#sc.add_element(s4)
sc.write_image()    #compose all elements in the scene
sc.show()           #tries to show the image with a default viewer
sc.write_to_file("test.png")    #saves the image to a file
