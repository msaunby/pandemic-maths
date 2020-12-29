
# Check garden.collider for better performance.

from math import cos, sin, pi, sqrt
from random import random, randint
from random import choice as randchoice
from itertools import combinations

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

class Arena(Widget):

    def on_pos(self, instance, pos):
        print("arena on_pos")
        self.pos = pos

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


class RegularShape(Widget):

    # shape properties
    name = StringProperty('')
    shape = ObjectProperty()
    infected = False

    '''Starting from center and creating edges around for i.e.:
    regular triangles, squares, regular pentagons, up to "circle".
    '''

    def __init__(self, **kwargs):
        super(RegularShape, self).__init__(**kwargs)

        color = [1.0,0.0,0.0]

        with self.canvas:
            Color(rgba=(color[0], color[1], color[2], 0.6))
            self.shape = Ellipse(
                pos=self.pos,
                size=(20,20)
            )
            self.change_x = randchoice([-3, -2, -1, 0, 1, 2, 3])
            self.change_y = randchoice([-3, -2, -1, 0, 1, 2, 3])


    def on_shape(self, instance, value):
        print("on_shape")

    def on_pos(self, instance, pos):
        self.shape.pos = [self.x, self.y]

    def infect(self):
        if self.infected:
            return
        self.infected = True
        with self.canvas:
            Color(rgba=(0, 0, 1.0, 0.6))
            self.shape = Ellipse(
                size=(20,20)
            )


class PongGame(Widget):

    arena = ObjectProperty(None)
    player1 = ObjectProperty(None)

    def __init__(self, shapes, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self.register_event_type('on_collision') 
        self.shapes = shapes

    def on_collision(self, pair, *args):
        '''Dispatched when objects collide, gives back colliding objects
        as a "pair" argument holding their instances.
        '''
        print('Collision {} x {}'.format(pair[0].name, pair[1].name))
        print('Infected {} x {}'.format(pair[0].infected, pair[1].infected))
        if pair[1].infected: pair[0].infect()
        if pair[0].infected: pair[1].infect()

    def update_shapes(self,delay):
        self.arena.x += 10
        for shape in self.shapes:
            shape.x += shape.change_x
            shape.y -= shape.change_y    
            

        # get all combinations from all available shapes
        if not hasattr(self, 'combins'):
            self.combins = list(combinations(self.shapes, 2))


    def update(self, dt):
        # bounce ball off bottom or top
        
        for ball in self.shapes:
            ball.color = [0.0,1.0,0.0]

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

        for com in self.combins:
            x = (com[0].center_x - com[1].center_x) ** 2
            y = (com[0].center_y - com[1].center_y) ** 2
            if sqrt(x + y) <= 5:
                # dispatch a custom event if the objects collide
                self.dispatch('on_collision', (com[0], com[1]))

               

class Collisions(App):
    #player1 = ObjectProperty(None)
    #player2 = ObjectProperty(None)
   
    
    def __init__(self, **kwargs):
        super(Collisions, self).__init__(**kwargs)

    def build(self):
        # list of shapes
        self.shapes = [
            RegularShape(
                name='{}'.format(x)
            ) for x in range(10)
        ]
        self.shapes[0].infect()    
        
        scene = PongGame(self.shapes)

        # move shapes to some random position
        for shape in self.shapes:
            shape.pos = [randint(50, i - 50) for i in Window.size]
            scene.add_widget(shape)

        Clock.schedule_interval(scene.update, 1.0 / 20.0)
        return scene


if __name__ == '__main__':
    Collisions().run()
