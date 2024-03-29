#! /usr/bin/python

import math

import numpy as np
from cagd.vec import vec2, vec3
from cagd.polyline import polyline
from cagd.bezier import bezier_surface, bezier_patches
import cagd.utils as utils
import copy
from math import *


class spline:
    # Interpolation modes
    INTERPOLATION_GIVEN_KNOTS = 0
    INTERPOLATION_EQUIDISTANT = 1
    INTERPOLATION_CHORDAL = 2
    INTERPOLATION_CENTRIPETAL = 3
    INTERPOLATION_FOLEY = 4

    def __init__(self, degree):
        assert (degree >= 1)
        self.degree = degree
        self.periodic = False
        self.knots = None
        self.control_points = []
        self.color = "black"

    # checks if the number of knots, control points and degree define a valid spline
    def validate(self):
        knots = self.knots.validate()
        points = len(self.knots) == len(self.control_points) + self.degree + 1
        return knots and points

    def evaluate(self, t):
        a, b = self.support()
        assert (a <= t <= b)
        if t == self.knots[len(self.knots) - self.degree - 1]:
            # the spline is only defined on the interval [a, b)
            # it is useful to define self(b) as lim t->b self(t)
            t = t - 0.000001
        return self.de_boor(t, 1)[0]

    # returns the interval [a, b) on which the spline is supported
    def support(self):
        return self.knots[self.degree], self.knots[len(self.knots) - self.degree - 1]

    def __call__(self, t):
        return self.evaluate(t)

    def tangent(self, t):
        diff = 0.01
        a, b = self.support()
        left = max(a, t - diff)
        right = min(b, t + diff)
        return (self.evaluate(right) - self.evaluate(left)) * (1 / (right - left))

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

    # calculates the de_boor scheme at a given value t
    # stops when the column is only "stop" elements long
    # returns that column as a list
    def de_boor(self, t, stop):
        n = self.degree
        index = self.knots.knot_index(t)
        control = self.control_points[index - n: index + 1]
        knot_vector = self.knots[index - n: index + n + 1]

        result = control
        k = 1
        while len(result) > stop:
            new_result = []
            for i in range(len(result) - 1):
                a_ik = (t - knot_vector[i + k]) / (knot_vector[i + n + 1] - knot_vector[i + k])
                d_ik = (1.0 - a_ik) * result[i] + a_ik * result[i + 1]

                new_result.append(d_ik)

            result = new_result
            k += 1

        return result

    # adjusts the control points such that it represents the same function,
    # but with an added knot
    def insert_knot(self, t):
        index = self.knots.knot_index(t)
        new_control = []
        new_knots = []
        len_new_knots = len(self.knots) + 1
        period = 0

        # calculate control points up to the last element of the second column in de boor
        for i in range(index - self.degree + 1):
            new_control.append(self.control_points[i])
        new_control.extend(self.de_boor(t, self.degree))

        if self.periodic:
            # determine period
            for i in range(1, len(self.control_points)):
                if self.control_points[0:self.degree] == self.control_points[i:i + self.degree]:
                    period = i
                    break

            # find the first newly calculated control point
            last_new_elem = None
            for i in range(len(self.control_points)):
                if abs(self.control_points[i] - new_control[i]) >= 0.000000001:
                    last_new_elem = i + self.degree - 1
                    break

            # wrap the new control points around the control polygon
            if last_new_elem <= period:
                new_control.extend(self.control_points[last_new_elem:period])
                new_control.extend(new_control[:self.degree])
            else:
                new_control.extend(self.control_points[last_new_elem:])
                new_control[:self.degree] = new_control[period + 1:]

            # adjust control points and insert the new knot
            self.control_points = new_control
            self.knots.insert(t)

            # find index of the knot that is repeated first
            # to add knots with appropriate intervals to maintain periodicity
            new_knots.extend(self.knots[:self.degree + period + 2])
            current_len = len(new_knots)
            for i in range(len_new_knots - current_len):
                diff = self.knots[self.degree + i + 1] - self.knots[self.degree + i]
                new_knot = new_knots[-1] + diff
                new_knots.append(new_knot)

            # check if a knot needs to be inserted in the period before t
            period_knot_value = self.knots[period] - self.knots[0]
            t_period = t % period_knot_value
            if (t_period >= new_knots[0]) & (new_knots.count(t_period) < new_knots.count(t)):
                new_knots = new_knots[1:]
                knot_obj = knots(len(new_knots))
                knot_obj.knots = new_knots
                knot_obj.insert(t_period)
                self.knots = knot_obj
                return

            # assign new knots to the spline
            knot_obj = knots(len(new_knots))
            knot_obj.knots = new_knots

            self.knots = knot_obj

        else:
            new_control.extend(self.control_points[index:])

            # adjust control points and insert the new knot
            self.control_points = new_control
            self.knots.insert(t)

    def get_axis_aligned_bounding_box(self):
        min_vec = copy.copy(self.control_points[0])
        max_vec = copy.copy(self.control_points[0])
        for p in self.control_points:
            # print("comparing {0} to {1} and {2}".format(p, min_vec, max_vec))
            if p.x < min_vec.x:
                min_vec.x = p.x
            if p.y < min_vec.y:
                min_vec.y = p.y
            if p.x > max_vec.x:
                max_vec.x = p.x
            if p.y > max_vec.y:
                max_vec.y = p.y
        return min_vec, max_vec

    def draw(self, scene, num_samples):
        i = self.degree - 1
        while i < len(self.knots) - self.degree - 2:
            i += 1
            k0 = self.knots[i]
            k1 = self.knots[i + 1]
            if k0 == k1:
                continue
            p0 = self(k0)
            for j in range(1, num_samples + 1):
                t = k0 + j / num_samples * (k1 - k0)
                p1 = self(t)
                scene.draw_line(p0, p1, self.color)
                p0 = p1

    def get_polyline_from_control_points(self):
        pl = polyline()
        for p in self.control_points:
            pl.append_point(p)
        return pl

    # generates a spline that interpolates the given points using the given mode
    # kts is only used as given knots in the mode: INTERPOLATION_GIVEN_KNOTS
    # returns that spline object
    def interpolate_cubic(mode, points, kts):
        spline_obj = spline(3)
        spline_obj.knots = knots(1)

        if mode == spline.INTERPOLATION_GIVEN_KNOTS:
            spline_obj.knots = kts

        if mode == spline.INTERPOLATION_EQUIDISTANT:
            spline_obj.knots.knots = [0, 0, 0] + list(range(len(points)))

        if mode == spline.INTERPOLATION_CHORDAL:
            spline_obj.knots.knots = [0, 0, 0] + [0]
            temp = spline_obj.knots.knots

            for i in range(len(points) - 1):
                distance = abs(points[i + 1] - points[i])
                spline_obj.knots.knots.append(temp[i + 3] + distance)

        if mode == spline.INTERPOLATION_CENTRIPETAL:
            spline_obj.knots.knots = [0, 0, 0] + [0]
            temp = spline_obj.knots.knots

            for i in range(len(points) - 1):
                distance = sqrt(abs(points[i + 1] - points[i]))
                spline_obj.knots.knots.append(temp[i + 3] + distance)

        if mode == spline.INTERPOLATION_FOLEY:
            spline_obj.knots.knots = [0.0, 0.0, 0.0] + [0.0]

            # d_i from -1 to m
            d_i = [None for _ in range(len(points))]
            for i in range(len(d_i) - 1):
                d_i[i] = abs(points[i + 1] - points[i])
            d_i.insert(0, 0.0)
            d_i.pop()
            d_i.append(0.0)

            # from 1 to m - 1
            theta_hat = [0.0 for _ in range(len(points))]

            for i in range(1, len(points) - 1):
                vec_one = points[i] - points[i - 1]
                vec_two = points[i + 1] - points[i]

                theta = math.acos(vec_one.dot(vec_two) / (abs(vec_one) * abs(vec_two)))
                theta_hat[i] = min(math.pi - theta, math.pi / 2.0)

            for i in range(1, len(points)):
                t_hat = d_i[i] * (1.0 + (3.0 / 2.0 * (theta_hat[i - 1] * d_i[i - 1]) / (d_i[i - 1] + d_i[i]))
                                  + (3.0 / 2.0 * (theta_hat[i] * d_i[i + 1]) / (d_i[i + 1] + d_i[i])))
                t_hat += spline_obj.knots.knots[-1]
                spline_obj.knots.knots.append(t_hat)

        if mode != spline.INTERPOLATION_GIVEN_KNOTS:
            spline_obj.knots.knots.append(spline_obj.knots.knots[-1])
            spline_obj.knots.knots.append(spline_obj.knots.knots[-1])
            spline_obj.knots.knots.append(spline_obj.knots.knots[-1])

        res = [points[0]] + [vec2(0.0, 0.0)] + points[1:-1] + [vec2(0.0, 0.0)] + [points[-1]]

        a = [-1]
        b = [1]
        c = [0]

        t = spline_obj.knots.knots

        for i in range(1, len(points) + 1):
            a.append((t[i + 2] - t[i]) / (t[i + 3] - t[i]))
            b.append((t[i + 2] - t[i + 1]) / (t[i + 3] - t[i + 1]))
            c.append((t[i + 2] - t[i + 1]) / (t[i + 4] - t[i + 1]))

        a.append(0.0)
        b.append(1.0)
        c.append(-1.0)

        # first row
        alpha = [0.0]
        beta = [1.0]
        gamma = [0.0]

        # second row
        alpha.append(-1.0)
        beta.append(1.0 + a[2])
        gamma.append(-a[2])

        # inner rows
        for i in range(2, len(a) - 2):
            alpha.append((1 - b[i]) * (1 - a[i]))
            beta.append((1 - b[i]) * a[i] + b[i] * (1 - c[i]))
            gamma.append(b[i] * c[i])

        # second last row
        alpha.append(-1.0 + c[len(a) - 3])
        beta.append(2.0 - c[len(a) - 3])
        gamma.append(-1.0)

        # last row
        alpha.append(0.0)
        beta.append(1.0)
        gamma.append(0.0)

        spline_obj.control_points = utils.solve_tridiagonal_equation(alpha, beta, gamma, res)
        return spline_obj

    # generates a spline that interpolates the given points and fulfills the definition
    # of a periodic spline with equidistant knots
    # returns that spline object
    def interpolate_cubic_periodic(points):
        m = len(points) - 1
        degree = 3
        spline_obj = spline(degree)
        spline_obj.knots = knots(1)
        spline_obj.knots.knots = list(range(m + 2 * degree + 2))

        diag1 = diag3 = [1 / 6] * (m + 1)
        diag2 = [4 / 6] * (m + 1)

        spline_obj.control_points = utils.solve_almost_tridiagonal_equation(diag1, diag2, diag3, points)

        for i in range(degree):
            spline_obj.control_points.append(spline_obj.control_points[i])

        return spline_obj

    # for splines of degree 3, generate a parallel spline with distance dist
    # the returned spline is off from the exact parallel by at most eps
    def generate_parallel(self, dist, eps):
        assert (self.degree == 3)
        if dist == 0:
            return self

        a, b = self.support()
        new_knots = True

        prev_no_of_knots = len(self.knots)

        spline_copy = copy.deepcopy(self)

        while new_knots:
            pts = []
            n = []
            para_pts = []
            for knot in spline_copy.knots:
                if a <= knot <= b:
                    new_pt = spline_copy.evaluate(knot)
                    t = spline_copy.tangent(knot)
                    new_n = 1 / sqrt(t.x ** 2 + t.y ** 2) * vec2(-t.y, t.x)
                    pts.append(new_pt)
                    n.append(new_n)
                    para_pts.append(new_pt + dist * new_n)

            para_pts = list(dict.fromkeys(para_pts))  # remove duplicates

            para_spline = spline.interpolate_cubic(spline.INTERPOLATION_GIVEN_KNOTS, para_pts, spline_copy.knots)

            for i in range(spline_copy.degree, len(spline_copy.knots) - spline_copy.degree - 1):
                midpoint = (spline_copy.knots[i] + spline_copy.knots[i + 1]) / 2

                vec_difference = spline_copy.evaluate(midpoint) - para_spline.evaluate(midpoint)
                euclidean_dist = sqrt(vec_difference.x ** 2 + vec_difference.y ** 2)
                dist_difference = abs(dist) - euclidean_dist

                if abs(dist_difference) > eps:
                    spline_copy.insert_knot(midpoint)
                    break

            if prev_no_of_knots == len(spline_copy.knots):
                new_knots = False
            prev_no_of_knots = len(spline_copy.knots)

        return para_spline

    # generates a rotational surface by rotating the spline around the z axis
    # the spline is assumed to be on the xz-plane
    # num_samples refers to the number of interpolation points in the rotational direction
    # returns a spline surface object in three dimensions
    def generate_rotation_surface(self, num_samples):
        surface = spline_surface((self.degree, self.degree))
        surface_control_points = []
        for d_i in self.control_points:
            z = d_i.y
            c_i = []

            for j in range(num_samples):
                x = d_i.x * cos(2.0 * pi * j / num_samples)
                y = d_i.x * sin(2.0 * pi * j / num_samples)
                c_i.append(vec2(x, y))
            periodic = spline.interpolate_cubic_periodic(c_i)
            new_control = []
            for point in periodic.control_points:
                new_control.append(vec3(point.x, point.y, z))
            surface_control_points.append(new_control)
        surface.control_points = surface_control_points

        v_knots = knots(len(surface_control_points[0]) + self.degree + 1)
        for index in range(len(v_knots.knots)):
            v_knots.knots[index] = index

        surface.knots = (self.knots, v_knots)
        surface.periodic = (False, True)

        return surface


class spline_surface:
    # the two directions of the parameter space
    DIR_U = 0
    DIR_V = 1

    # creates a spline of degrees n,m
    # degree is a tuple (n,m)
    def __init__(self, degree):
        du, dv = degree
        assert (du >= 1 and dv >= 1)
        self.degree = degree
        self.periodic = (False, False)
        self.knots = (None, None)  # tuple of both knot vectors
        self.control_points = [[]]  # 2dim array of control points

    # checks if the number of knots, control points and degree define a valid spline
    def validate(self):
        if len(self.control_points) == 0:
            return False
        k1, k2 = self.knots
        d1, d2 = self.degree
        knots12 = k1.validate() and k2.validate()
        p1 = len(self.control_points)
        p2 = len(self.control_points[0])
        points1 = len(k1) == p1 + d1 + 1
        points2 = len(k2) == p2 + d2 + 1

        return knots12 and points1 and points2

    def evaluate(self, u, v):
        s1, s2 = self.support()
        a, b = s1
        c, d = s2
        assert (a <= u <= b and c <= v <= d)
        if u == b:
            u = u - 0.000001
        if v == d:
            v = v - 0.000001
        t = (u, v)
        return self.de_boor(t, (1, 1))[0][0]

    # return nested tuple ((a,b), (c,d))
    # the spline is supported in (u,v) \in [a,b)x[c,d]
    def support(self):
        k1, k2 = self.knots
        d1, d2 = self.degree
        s1 = (k1[d1], k1[len(k1) - d1 - 1])
        s2 = (k2[d2], k2[len(k2) - d2 - 1])
        return (s1, s2)

    def __call__(self, u, v):
        return self.evaluate(u, v)

    # calculates the de boor scheme at t = (u,v)
    # until there are only stop = (s1, s2) elements left
    def de_boor(self, t, stop):
        d1, d2 = self.degree
        k1, k2 = self.knots
        s1, s2 = stop
        u, v = t
        m1 = len(self.control_points)
        m2 = len(self.control_points[0])

        new_rows = [None for i in range(m1)]
        for row in range(m1):
            spl = spline(d2)
            spl.knots = k2
            spl.control_points = self.control_points[row]
            new_rows[row] = spl.de_boor(v, s2)

        new_pts = [None for i in range(s2)]
        for col in range(s2):
            spl = spline(d1)
            spl.knots = k1
            ctrl_pts = [new_rows[i][col] for i in range(m1)]
            spl.control_points = ctrl_pts
            new_pts[col] = spl.de_boor(u, s1)

        return new_pts

    def insert_knot(self, direction, t):
        if direction == self.DIR_U:
            self.__insert_knot_u(t)
        elif direction == self.DIR_V:
            self.__insert_knot_v(t)
        else:
            assert (False)

    def __insert_knot_v(self, t):
        du, dv = self.degree
        pu, pv = self.periodic
        ku, kv = self.knots
        nu = len(self.control_points)
        nv = len(self.control_points[0])
        for i in range(nu):
            row = self.control_points[i]
            spl = spline(dv)
            spl.control_points = copy.copy(row)
            spl.knots = copy.deepcopy(kv)
            spl.periodic = pv
            spl.insert_knot(t)
            self.control_points[i] = spl.control_points
            self.knots = (ku, spl.knots)

    def __insert_knot_u(self, t):
        du, dv = self.degree
        pu, pv = self.periodic
        ku, kv = self.knots
        nu = len(self.control_points)
        nv = len(self.control_points[0])
        new_control_points = [[None for i in range(nv)] for j in range(nu + 1)]
        for i in range(nv):
            col = [self.control_points[j][i] for j in range(nu)]
            spl = spline(du)
            spl.control_points = col
            spl.knots = copy.deepcopy(ku)
            spl.periodic = pu
            spl.insert_knot(t)
            for j in range(nu + 1):
                new_control_points[j][i] = spl.control_points[j]
            self.knots = (spl.knots, kv)
        self.control_points = new_control_points

    # build bezier patches based on the spline with multiple knots
    # and control points sitting also as bezier points.
    def to_bezier_patches(self):
        patches = bezier_patches()
        m, n = self.degree
        u_knots, v_knots = self.knots

        inner_u_knots = u_knots[m:len(u_knots) - m]
        for i in range(len(inner_u_knots)):
            knot = inner_u_knots[i]
            p = self.knots[spline_surface.DIR_U].knots.count(knot)
            for x in range(m - p):
                self.insert_knot(spline_surface.DIR_U, knot)

        inner_v_knots = v_knots[n:len(v_knots) - n - 1]
        for i in range(len(inner_v_knots)):
            knot = inner_v_knots[i]
            p = self.knots[spline_surface.DIR_V].knots.count(knot)
            for x in range(n - p):
                self.insert_knot(spline_surface.DIR_V, knot)

        for i in range(0, len(self.control_points) - m, m):
            for j in range(0, len(self.control_points[i]) - n, n):
                new_patch = bezier_surface(self.degree)
                new_control = [[None] * (n + 1) for _ in range(m + 1)]
                for k in range(m + 1):
                    for l in range(n + 1):
                        new_control[k][l] = self.control_points[(i + k) % len(self.control_points)][
                            (j + l) % len(self.control_points[i])]

                new_patch.control_points = new_control
                patches.append(new_patch)
        return patches


class knots:
    # creates a knots array with n elements
    def __init__(self, n):
        self.knots = [None for i in range(n)]

    def validate(self):
        prev = None
        for k in self.knots:
            if k is None:
                return False
            if prev is not None:
                if k < prev:
                    return False
            prev = k
        return True

    def __len__(self):
        return len(self.knots)

    def __getitem__(self, i):
        return self.knots[i]

    def __setitem__(self, i, v):
        self.knots[i] = v

    def __delitem__(self, i):
        del self.knots[i]

    def __iter__(self):
        return iter(self.knots)

    def insert(self, t):
        i = 0
        while self[i] < t:
            i += 1
        self.knots.insert(i, t)

    def knot_index(self, v):
        for i in range(len(self.knots) - 1):
            if self.knots[i] <= v < self.knots[i + 1]:
                return i
        return len(self.knots) - 1
