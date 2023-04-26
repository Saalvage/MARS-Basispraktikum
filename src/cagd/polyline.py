#!/usr/bin/python
from cagd.vec import vec2
import copy

#this class represents a chain of points linked by a line
#useful for drawing control polygons or a list of points that are
#to be interpolated by a spline
class polyline:
    def __init__(self):
        self.points = []
        self.color = "black"

    def append_point(self, point):
        self.points.append(point)

    def set_color(self, color):
        self.color = color

    def draw(self, scene, num_samples):
        for i in range(len(self.points) - 1):
            p0 = self.points[i]
            p1 = self.points[i+1]
            scene.draw_line(p0, p1, self.color)

    def get_axis_aligned_bounding_box(self):
        min_vec = copy.copy(self.points[0])
        max_vec = copy.copy(self.points[0])
        for p in self.points:
            if p.x < min_vec.x:
                min_vec.x = p.x
            if p.y < min_vec.y:
                min_vec.y = p.y
            if p.x > max_vec.x:
                max_vec.x = p.x
            if p.y > max_vec.y:
                max_vec.y = p.y
        return (min_vec, max_vec)
