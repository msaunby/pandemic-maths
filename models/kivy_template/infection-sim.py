# A simple model of viral infection.
# Bounce 100 balls and when an infected ball strikes another it is
# infected.
# A recovery time is set, and once recovered an infected subject can
# no longer be infected or infect another.
# Assumes no other consequence of infection, i.e. all infected will
# recover and be immune forever.

RECOVER_TIME = 4.0
POPULATION_SIZE = 100

from math import cos, sin, pi, sqrt
from random import random, randint
from random import choice as randchoice
from itertools import combinations

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import StringProperty

class Indicator(Widget):

    def __init__(self, color, **kwargs):
        self.color = color
        super().__init__(**kwargs)


class Person(Widget):

    name = StringProperty('')
    infected = False
    recovered = False
    recover_time = RECOVER_TIME

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

        self.change_x = randchoice([-2, -1, -0.3, 0.3, 1, 2])
        self.change_y = randchoice([-2, -1, -0.3, 0.3, 1, 2])
        self.change_x *= 2.0
        self.change_y *= 2.0

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
        Clock.schedule_once(self.recover, self.recover_time)
        self.susceptible_indicator.opacity = 0.0
        self.infected_indicator.opacity = 1.0  
        self.recovered_indicator.opacity = 0.0  


class Arena(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_collision')
        self.begin()


    def end(self, dt):
        self.sched.cancel()

    def begin(self):
        self.population = [
            Person(
                name='{}'.format(x)
            ) for x in range(POPULATION_SIZE)
        ]

        self.population[0].infect() 
        self.population[2].infect()

        for shape in self.population:
            shape.pos = [randint(50, i - 50) for i in self.size]
            self.add_widget(shape)

        self.sched = Clock.schedule_interval(self.update, 1.0 / 60.0) 


    def on_collision(self, pair, *args):
        (pair[0].change_x,pair[1].change_x) = (pair[1].change_x,pair[0].change_x)
        (pair[0].change_y,pair[1].change_y) = (pair[1].change_y,pair[0].change_y)
        if pair[1].infected: pair[0].infect()
        if pair[0].infected: pair[1].infect()

    def update_population(self,delay):
        for shape in self.population:
            shape.x += shape.change_x
            shape.y -= shape.change_y             

        # get all combinations, used to check for collisions
        if not hasattr(self, 'combins'):
            self.combins = list(combinations(self.population, 2))

    def update(self, dt):
        
        for person in self.population:
            person.color = [0.0,1.0,0.0]

            if person.y < 0:
                person.y = 0
                person.change_y *= -1
            if person.y > self.top:
                person.y = self.top
                person.change_y *= -1
            if person.x < 0:
                person.x = 0
                person.change_x *= -1
            if person.x > self.right:
                person.x = self.right
                person.change_x *= -1
        self.update_population(self)

        for com in self.combins:
            x = (com[0].center_x - com[1].center_x) ** 2
            y = (com[0].center_y - com[1].center_y) ** 2
            if sqrt(x + y) <= 5:
                self.on_collision((com[0],com[1]))

class Infection(App):
  
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):  
        scene = Arena()
        return scene

if __name__ == '__main__':
    Infection().run()