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

    """   
    # calculate deviation from perfect circle at every control point
    # all deviations are consequently the same obviously
    control = spline.control_points
     
    for i in range(len(control)):
        deviation = math.sqrt(control[i].x ** 2 + control[i].y ** 2) - 1  # should be 0 in a perfect circle
        deviations.append(deviation)"""

    # calculate deviation from unit circle at each knot in the supported interval
    a, b = spline.support()
    for knot in spline.knots.knots:
        if a <= knot <= b:
            coord = spline(knot)
            deviation = math.sqrt(coord.x ** 2 + coord.y ** 2) - 1
            print("knot:", knot)
            print("deviation:", deviation)
            deviations.append(deviation)

    print("deviations:", deviations)
    mean_error = sum(deviations) / len(deviations)
    print("mean error:", mean_error)

    abs_deviations = [abs(d) for d in deviations]
    max_deviation = max(abs_deviations)
    print("maximum deviation (absolute):", max_deviation)

    pass


# interpolate 6 points with a periodic spline to create the number "8"
pts = [vec2(0, 2.5), vec2(-1, 1), vec2(1, -1), vec2(0, -2.5), vec2(-1, -1), vec2(1, 1)]
pts_line = polyline()
pts_line.points = pts
pts_line.set_color("red")
s = spline.interpolate_cubic_periodic(pts)
p = s.get_polyline_from_control_points()
p.set_color("blue")
sc = scene.scene()
sc.set_resolution(900)
sc.add_element(s)
sc.add_element(p)

# generate a spline that approximates the unit circle
n = 8
circle_pts = unit_circle_points(n)
circle = spline.interpolate_cubic_periodic(circle_pts)
sc.add_element(circle)
calculate_circle_deviation(circle)

sc.write_image()
sc.show()
