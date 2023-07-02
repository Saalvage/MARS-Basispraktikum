#!/usr/bin/python
import math

import cagd.scene_2d as scene
from cagd.vec import vec2
from cagd.spline import spline, knots
from cagd.polyline import polyline


# returns a list of num_samples points that are uniformly distributed on the unit circle
def unit_circle_points(num_samples):
    section_length = 2 * math.pi / num_samples
    angles = [i * section_length for i in range(num_samples)]

    points = []
    for angle in angles:
        points.append(vec2(math.cos(angle), math.sin(angle)))
    return points


# calculates the deviation between the given spline and a unit circle
def calculate_circle_deviation(spline):
    deviations = []

    a, b = spline.support()
    iterations = 10000
    for knot in [x / float(iterations) for x in range(iterations * a, iterations * b + 1)]:
        coord = spline(knot)
        deviation = abs(math.sqrt(coord.x ** 2 + coord.y ** 2) - 1)
        deviations.append(deviation)

    mean = sum(deviations) / len(deviations)
    print("mean absolute deviation:", mean)

    # this value is actually interesting to observe,
    # a relatively large value means the approximation is struggling to fit the shape of a circle
    # a relatively small value means the approximation correctly fits a circle, but the radius is incorrect
    std = sum((x - mean) ** 2 for x in deviations) / len(deviations)
    print("standard deviation:", std)

    max_v = max(deviations)
    print("maximum deviation:", max_v)


# interpolate 6 points with a periodic spline to create the number "8"
pts = [vec2(0, 2.5), vec2(-1, 1), vec2(1, -1), vec2(0, -2.5), vec2(-1, -1), vec2(1, 1)]
pts_line = polyline()
# pts_line.points = pts
# pts_line.set_color("red")
s = spline.interpolate_cubic_periodic(pts)
p = s.get_polyline_from_control_points()
p.set_color("blue")
sc = scene.scene()
sc.set_resolution(900)
#sc.add_element(s)
#sc.add_element(p)

# generate a spline that approximates the unit circle
n = 8
circle_pts = unit_circle_points(n)
pts_line2 = polyline()
pts_line2.points = circle_pts.copy()
pts_line2.points.append(pts_line2.points[0])
pts_line2.set_color("red")
#sc.add_element(pts_line2)


# original interpolation
circle = spline.interpolate_cubic_periodic(circle_pts)


print(len(circle_pts), "circle_pts")
print(len(circle.control_points), "OG control points")
for point in circle.control_points:
    print("(", round(point.x, 2), ",", round(point.y, 2), ")")
print(len(circle.knots), "knots before:", *circle.knots)

control_before = circle.get_polyline_from_control_points()
control_before.set_color("red")
#sc.add_element(control_before)

circle.periodic = True

# knot insertion
circle.insert_knot(3)

print(len(circle.control_points), "resulting control points:")
for point in circle.control_points:
    print("(", round(point.x, 2), ",", round(point.y, 2), ")")
print(len(circle.knots), "knots after:", *circle.knots)
control_after = circle.get_polyline_from_control_points()
control_after.set_color("green")
#sc.add_element(control_after)


sc.add_element(circle)
# calculate_circle_deviation(circle)

sc.write_image()
sc.show()
