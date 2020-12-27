
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
        self.size_hint = (None, None)
        self.add_widget(Label(text=self.name))

    def move_label(self, x, y, *args):
        '''Move label with shape name as the only child.'''
        self.children[0].pos = [x, y]


    def on_shape(self, instance, value):
        print("on_shape")

    def on_pos(self, instance, pos):

        # stick label to bounding box (widget)
        if self.name:
            self.move_label(*pos)

        self.shape.pos = [self.x+40, self.y+40]
        print("on_pos")



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
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def update(self, dt):
        return

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y


class Collisions(App):

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

        game = PongGame()

        scene = game
        #scene = FloatLayout()

        # list of shapes
        self.shapes = [
            RegularShape(
                name='{}'.format(x), edges=10
            ) for x in range(10)
        ]

        # move shapes to some random position
        for shape in self.shapes:
            shape.pos = [randint(50, i - 50) for i in Window.size]
            scene.add_widget(shape)

        # update positions at regular intervals 
        Clock.schedule_interval(self.update_shapes,0.05)
        #return scene

        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    Collisions().run()
