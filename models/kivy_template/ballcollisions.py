
# Check garden.collider for better performance.

from math import cos, sin, pi, sqrt
from random import random, randint
from random import choice as randchoice

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import (Color, Ellipse)
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import (StringProperty, ObjectProperty)
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
)

class PongPaddle(Widget):
    score = NumericProperty(0)
    can_bounce = BooleanProperty(True)

    def bounce_ball(self, ball):
        if self.collide_widget(ball) and self.can_bounce:
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset
            self.can_bounce = False
        elif not self.collide_widget(ball) and not self.can_bounce:
            self.can_bounce = True


class BaseShape(Widget):
    '''(internal) Base class for moving with touches or calls.'''

    # shape properties
    name = StringProperty('')
    shape = ObjectProperty()

    def __init__(self, **kwargs):
        '''Create a shape with size [100, 100]
        and give it a label if it's named.
        '''
        super(BaseShape, self).__init__(**kwargs)
        self.size_hint = (1000, 1000)


    def on_shape(self, instance, value):
        print("on_shape")

    def on_pos(self, instance, pos):

        self.shape.pos = [self.x, self.y]


class RegularShape(BaseShape):
    '''Starting from center and creating edges around for i.e.:
    regular triangles, squares, regular pentagons, up to "circle".
    '''

    def __init__(self, edges=3, color=None, **kwargs):
        super(RegularShape, self).__init__(**kwargs)
        
        color = color or [1.0,0.0,0.0]

        with self.canvas:
            Color(rgba=(color[0], color[1], color[2], 0.6))
            self.shape = Ellipse(
                pos=self.pos,
                size=(20,20)
            )
            self.change_x = randchoice([-3, -2, -1, 0, 1, 2, 3])
            self.change_y = randchoice([-3, -2, -1, 0, 1, 2, 3])

class PongGame(Widget):

    def __init__(self, shapes, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self.shapes = shapes

    def update_shapes(self,delay):
        for shape in self.shapes:
            shape.x += shape.change_x
            shape.y -= shape.change_y    

    def update(self, dt):
        # bounce ball off bottom or top
        for ball in self.shapes:
            if ball.y < 0:
                ball.y = 0
                ball.change_y *= -1
            if ball.y > 200:
                ball.y = 200
                ball.change_y *= -1
            if ball.x < 0:
                ball.x = 0
                ball.change_x *= -1
            if ball.x > 300:
                ball.x = 300
                ball.change_x *= -1
        self.update_shapes(self)
               

class Collisions(App):
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Collisions, self).__init__(**kwargs)
        # register an event for collision
        self.register_event_type('on_collision')

    def on_collision(self, pair, *args):
        '''Dispatched when objects collide, gives back colliding objects
        as a "pair" argument holding their instances.
        '''
        print('Collision {} x {}'.format(pair[0].name, pair[1].name))

    def update_shapes(self,delay):
        for shape in self.shapes:
            shape.x += shape.change_x
            shape.y -= shape.change_y

    
    def build(self):

        # list of shapes
        self.shapes = [
            RegularShape(
                name='{}'.format(x), edges=10
            ) for x in range(10)
        ]

        scene = PongGame(self.shapes)

        # move shapes to some random position
        for shape in self.shapes:
            shape.pos = [randint(50, i - 50) for i in Window.size]
            scene.add_widget(shape)

        Clock.schedule_interval(scene.update, 1.0 / 60.0)
        return scene


if __name__ == '__main__':
    Collisions().run()
