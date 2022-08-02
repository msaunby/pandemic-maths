# This is a simple demo for advanced collisions and mesh creation from a set
# of points. Its purpose is only to give an idea on how to make complex stuff.

# Check garden.collider for better performance.

from math import cos, sin, pi, sqrt
from random import random, randint
from itertools import combinations

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Color, Mesh, Point, Ellipse
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import (
    ListProperty,
    StringProperty,
    ObjectProperty,
    NumericProperty
)


class BaseShape(Widget):
    '''(internal) Base class for moving with touches or calls.'''

    # keep references for offset
    _old_pos = ListProperty([0, 0])
    _old_touch = ListProperty([0, 0])
    _new_touch = ListProperty([0, 0])

    # shape properties
    name = StringProperty('')
    poly = ListProperty([])
    shape = ObjectProperty()
    poly_len = NumericProperty(0)
    shape_len = NumericProperty(0)
    debug_collider = ObjectProperty()
    debug_collider_len = NumericProperty(0)

    def __init__(self, **kwargs):
        '''Create a shape with size [100, 100]
        and give it a label if it's named.
        '''
        super(BaseShape, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.add_widget(Label(text=self.name))

    def move_label(self, x, y, *args):
        '''Move label with shape name as the only child.'''
        self.children[0].pos = [x, y]

    def move_collider(self, offset_x, offset_y, *args):
        '''Move debug collider when the shape moves.'''
        points = self.debug_collider.points[:]

        for i in range(0, self.debug_collider_len, 2):
            points[i] += offset_x
            points[i + 1] += offset_y
        self.debug_collider.points = points

    def on_debug_collider(self, instance, value):
        '''Recalculate length of collider points' array.'''
        self.debug_collider_len = len(value.points)

    def on_poly(self, instance, value):
        '''Recalculate length of polygon points' array.'''
        self.poly_len = len(value)

    def on_shape(self, instance, value):
        '''Recalculate length of Mesh vertices' array.'''
        # self.shape_len = len(value.vertices)
        print("on_shape")

    def on_pos(self, instance, pos):
        '''Move polygon and its Mesh on each position change.
        This event is above all and changes positions of the other
        children-like components, so that a simple::

            shape.pos = (100, 200)

        would move everything, not just the widget itself.
        '''

        # position changed by touch
        offset_x = self._new_touch[0] - self._old_touch[0]
        offset_y = self._new_touch[1] - self._old_touch[1]

        # position changed by call (shape.pos = X)
        if not offset_x and not offset_y:
            offset_x = pos[0] - self._old_pos[0]
            offset_y = pos[1] - self._old_pos[1]
            self._old_pos = pos

        # move polygon points by offset
        for i in range(0, self.poly_len, 2):
            self.poly[i] += offset_x
            self.poly[i + 1] += offset_y

        # stick label to bounding box (widget)
        if self.name:
            self.move_label(*pos)

        # move debug collider if available
        if self.debug_collider is not None:
            self.move_collider(offset_x, offset_y)

        # return if no Mesh available
        if self.shape is None:
            return

        # move Mesh vertices by offset
        #points = self.shape.vertices[:]
        #for i in range(0, self.shape_len, 2):
        #    points[i] += offset_x
        #    points[i + 1] += offset_y
        #self.shape.vertices = points
        #self.shape.pos =  (self.shape.pos[0]+offset_x,self.shape.pos[1]+offset_y)
        self.shape.pos = [self.x+40, self.y+40]


    def on_touch_move(self, touch, *args):
        '''Move shape with dragging.'''

        # grab single touch for shape
        if touch.grab_current is not self:
            return

        # get touches
        x, y = touch.pos
        new_pos = [x, y]
        self._new_touch = new_pos
        self._old_touch = [touch.px, touch.py]

        # get offsets, move & trigger on_pos event
        offset_x = self._new_touch[0] - self._old_touch[0]
        offset_y = self._new_touch[1] - self._old_touch[1]
        self.pos = [self.x + offset_x, self.y + offset_y]

    def shape_collide(self, x, y, *args):
        '''Point to polygon collision through a list of points.'''

        # ignore if no polygon area is set
        poly = self.poly
        if not poly:
            return False

        n = self.poly_len
        inside = False
        p1x = poly[0]
        p1y = poly[1]

        # compare point pairs via PIP algo, too long, read
        # https://en.wikipedia.org/wiki/Point_in_polygon
        for i in range(0, n + 2, 2):
            p2x = poly[i % n]
            p2y = poly[(i + 1) % n]

            if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= xinters:
                    inside = not inside

            p1x, p1y = p2x, p2y
        return inside


class RegularShape(BaseShape):
    '''Starting from center and creating edges around for i.e.:
    regular triangles, squares, regular pentagons, up to "circle".
    '''

    def __init__(self, edges=3, color=None, **kwargs):
        super(RegularShape, self).__init__(**kwargs)
        
        #color = color or [random() for i in range(3)]
        color = color or [1.0,0.0,0.0]
        rad_edge = (pi * 2) / float(edges)
        r_x = self.width / 2.0
        r_y = self.height / 2.0
        poly = []
        vertices = []
        for i in range(edges):
            # get points within a circle with radius of [r_x, r_y]
            x = cos(rad_edge * i) * r_x + self.center_x
            y = sin(rad_edge * i) * r_y + self.center_y
            poly.extend([x, y])

            # add UV layout zeros for Mesh, see Mesh docs
            vertices.extend([x, y, 0, 0])

        # draw Mesh shape from generated poly points
        with self.canvas:
            Color(rgba=(color[0], color[1], color[2], 0.6))
            #self.shape = Mesh(
            #    pos=self.pos,
            #    vertices=vertices,
            #    indices=list(range(edges)),
            #    mode='triangle_fan'
            #)
            self.shape = Ellipse(
                pos=self.pos,
                size=(20,20)
            )
        self.poly = poly

    def on_touch_down(self, touch, *args):
        if self.shape_collide(*touch.pos):
            touch.grab(self)


class Collisions(App):
    def __init__(self, **kwargs):
        super(Collisions, self).__init__(**kwargs)
        # register an event for collision
        self.register_event_type('on_collision')

    def collision_circles(self, shapes=None, distance=100, debug=False, *args):

        '''Simple circle <-> circle collision between the shapes i.e. there's
        a simple line between the centers of the two shapes and the collision
        is only about measuring distance -> 1+ radii intersections.
        '''

        # get all combinations from all available shapes
        if not hasattr(self, 'combins'):
            self.combins = list(combinations(shapes, 2))

        for com in self.combins:
            x = (com[0].center_x - com[1].center_x) ** 2
            y = (com[0].center_y - com[1].center_y) ** 2
            if sqrt(x + y) <= distance:
                # dispatch a custom event if the objects collide
                self.dispatch('on_collision', (com[0], com[1]))

        # draw collider only if debugging
        if not debug:
            return

        # add circle collider only if the shape doesn't have one
        for shape in shapes:
            if shape.debug_collider is not None:
                continue

            d = distance / 2.0
            cx, cy = shape.center
            points = [(cx + d * cos(i), cy + d * sin(i)) for i in range(44)]
            points = [p for ps in points for p in ps]
            with shape.canvas:
                Color(rgba=(0, 1, 0, 1))
                shape.debug_collider = Point(points=points)

    def on_collision(self, pair, *args):
        '''Dispatched when objects collide, gives back colliding objects
        as a "pair" argument holding their instances.
        '''
        print('Collision {} x {}'.format(pair[0].name, pair[1].name))

    def build(self):
        # the environment for all 2D shapes
        scene = FloatLayout()

        # list of shapes
        shapes = [
            RegularShape(
                name='{}'.format(x), edges=10
            ) for x in range(10)
        ]

        # move shapes to some random position
        for shape in shapes:
            shape.pos = [randint(50, i - 50) for i in Window.size]
            scene.add_widget(shape)

        # check for simple collisions between the shapes
        Clock.schedule_interval(
            lambda *t: self.collision_circles(shapes, debug=True), 0.1)
        return scene


if __name__ == '__main__':
    Collisions().run()
