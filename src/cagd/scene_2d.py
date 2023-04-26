#!/usr/bin/python
from cagd.vec import vec2, vec3
from cagd.bezier import bezier_curve
from cagd.spline import spline, knots
from cagd.polyline import polyline
from PIL import Image, ImageDraw

class scene:
    def __init__(self):
        self.elements = []
        self.resolution = None
        self.margin = 10
        self.background = "white"
        self.bounding_box = None
        self.image = None
        self.transform = None
        self.num_samples = 20

    #sets the longer side of the image to length pixels
    def set_resolution(self, resolution):
        self.resolution = resolution

    def set_background(self, color):
        self.background = color
    
    def set_num_samples(self, num):
        self.num_samples = num

    def add_element(self, elem):
        self.elements.append(elem)
        bounding_box = elem.get_axis_aligned_bounding_box()
        if len(self.elements) == 1:
            self.bounding_box = bounding_box
        else:
            min_vec, max_vec = self.bounding_box
            e1, e2 = bounding_box
            if e1.x < min_vec.x:
                min_vec.x = e1.x
            if e1.y < min_vec.y:
                min_vec.y = e1.y
            if e2.x > max_vec.x:
                max_vec.x = e2.x
            if e2.y > max_vec.y:
                max_vec.y = e2.y

    def write_image(self):
        if self.elements == []:
            print("empty scene")
            return
        resolution = self.resolution
        margin = self.margin
        bb_bl, bb_tr = self.bounding_box
        scene_width = (bb_tr - bb_bl).x
        scene_height = (bb_tr - bb_bl).y
        aspect_ratio = scene_width / scene_height

        #determine which side's length is set to self.resolution pixels
        if aspect_ratio > 1:
            image_width = resolution
            image_height = int((resolution - 2*margin) / aspect_ratio) + 2 * margin
        elif aspect_ratio < 1:
            image_width = int((resolution - 2*margin) * aspect_ratio) + 2 * margin
            image_height = resolution
        else:
            image_width = resolution
            image_height = resolution

        #calculate a transformation from object space to image space.
        #in image space, the y coordinate points downwards
        #print("calculationg transform")
        #print("scene w,h,w/h", scene_width, scene_height, aspect_ratio)
        #print("image w,h", image_width, image_height)
        scale = (image_width - 2 * margin) / scene_width
        offset = -vec2(scale * bb_bl.x, -scale * bb_bl.y) + vec2(margin, image_height - margin)
        #print("scale, offset", scale, offset)
        transform = lambda v: vec2(scale * v.x, -scale * v.y) + offset
        self.transform = transform

        #generate the image
        self.image = Image.new("RGB", (image_width, image_height), self.background)
        for elem in self.elements:
            elem.draw(self, self.num_samples)

    def write_to_file(self, path):
        self.image.save(path)

    def draw_line(self, p1, p2, color):
        q1 = self.transform(p1)
        q2 = self.transform(p2)
        draw = ImageDraw.Draw(self.image)
        draw.line((q1.x, q1.y, q2.x, q2.y), fill=color)

    def show(self):
        self.image.show()
