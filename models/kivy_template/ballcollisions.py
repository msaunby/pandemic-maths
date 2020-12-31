
# Check garden.collider for better performance.

from math import cos, sin, pi, sqrt
from random import random, randint
from random import choice as randchoice
from itertools import combinations

from kivy.app import App
from kivy.clock import Clock
#from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
#from kivy.graphics import (Color, Ellipse)
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import (StringProperty, ObjectProperty)
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
)

class Arena(Widget):

    def on_pos(self, instance, pos):
        self.pos = pos

class Indicator(Widget):

    def __init__(self, color, **kwargs):
        self.color = color
        super().__init__(**kwargs)


class RegularShape(Widget):

    # shape properties
    name = StringProperty('')
    shape = ObjectProperty()
    infected = False
    recovered = False


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.susceptible_indicator = Indicator([1,1,0])
        self.add_widget(self.susceptible_indicator)
        self.infected_indicator = Indicator([1,0,0])
        self.infected_indicator.opacity = 0.0
        self.add_widget(self.infected_indicator)
        self.recovered_indicator = Indicator([0,0,1])
        self.recovered_indicator.opacity = 0.0
        self.add_widget(self.recovered_indicator)

        self.change_x = randchoice([-3, -2, -1, 0, 1, 2, 3])
        self.change_y = randchoice([-3, -2, -1, 0, 1, 2, 3])


    def on_shape(self, instance, value):
        print("on_shape")

    def on_pos(self, instance, pos):
        self.susceptible_indicator.pos  = [self.x, self.y]
        self.infected_indicator.pos  = [self.x, self.y]
        self.recovered_indicator.pos  = [self.x, self.y]

    def recover(self,dt):
        self.recovered = True
        self.infected = False
        self.susceptible_indicator.opacity = 0.0
        self.infected_indicator.opacity = 0.0  
        self.recovered_indicator.opacity = 1.0 

    def infect(self):
        if self.infected or self.recovered:
            return
        self.infected = True
        Clock.schedule_once(self.recover, 4.0)
        self.susceptible_indicator.opacity = 0.0
        self.infected_indicator.opacity = 1.0  
        self.recovered_indicator.opacity = 0.0  


class PongGame(Widget):

    arena = ObjectProperty(None)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_collision') 
        self.shapes = [
            RegularShape(
                name='{}'.format(x)
            ) for x in range(100)
        ]
        self.shapes[0].infect()  
        print(dir(self.arena))
        for shape in self.shapes:
            shape.pos = [randint(50, i - 50) for i in self.arena.size]
            self.arena.add_widget(shape)
        Clock.schedule_interval(self.update, 1.0 / 40.0)    

    def on_collision(self, pair, *args):
        '''Dispatched when objects collide, gives back colliding objects
        as a "pair" argument holding their instances.
        '''
        (pair[0].change_x,pair[1].change_x) = (pair[1].change_x,pair[0].change_x)
        (pair[0].change_y,pair[1].change_y) = (pair[1].change_y,pair[0].change_y)
        #print('Collision {} x {}'.format(pair[0].name, pair[1].name))
        if pair[1].infected: pair[0].infect()
        if pair[0].infected: pair[1].infect()

    def update_shapes(self,delay):
        for shape in self.shapes:
            shape.x += shape.change_x
            shape.y -= shape.change_y             

        # get all combinations, used to check for collisions
        if not hasattr(self, 'combins'):
            self.combins = list(combinations(self.shapes, 2))


    def update(self, dt):
        
        for ball in self.shapes:
            ball.color = [0.0,1.0,0.0]

            if ball.y < 0:
                ball.y = 0
                ball.change_y *= -1
            if ball.y > self.arena.top:
                ball.y = self.arena.top
                ball.change_y *= -1
            if ball.x < 0:
                ball.x = 0
                ball.change_x *= -1
            if ball.x > self.arena.right:
                ball.x = self.arena.right
                ball.change_x *= -1
        self.update_shapes(self)

        for com in self.combins:
            x = (com[0].center_x - com[1].center_x) ** 2
            y = (com[0].center_y - com[1].center_y) ** 2
            if sqrt(x + y) <= 5:
                # dispatch a custom event if the objects collide
                self.dispatch('on_collision', (com[0], com[1]))


    def build(self):
        Clock.schedule_interval(self.update, 1.0 / 40.0)    

class Collisions(App):
  
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):  
        scene = PongGame()
        return scene

if __name__ == '__main__':
    Collisions().run()