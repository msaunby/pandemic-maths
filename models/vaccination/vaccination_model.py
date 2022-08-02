
from enum import Enum

class Status(Enum):
    VULNERABLE = 0  # Can be infected. Can be vaccinated.
    INFECTIOUS = 1  # Can infect others. Cannot be infected. Cannot be vaccinated. Will recover after infectious period.
    RECOVERED = 2 # Cannot be infected. Can be vaccinated.
    VACCINATED = 3 # Cannot be infected.

class Person():
    def __init__(self) -> None:
        self._status = Status.VULNERABLE

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value:Status) -> None:
        self._status = value
    
    def can_infect(self):
        return self._status == Status.INFECTIOUS
    
    def can_be_infected(self):
        return self._status == Status.VULNERABLE

    def infect(self) -> None:
        self.status = Status.INFECTIOUS
        self.infection_duration = 0

    def infection_incr(self) -> None:
        self.infection_duration += 1

    def recover(self) -> None:
        self.status = Status.RECOVERED

    def can_be_vaccinated(self):
        return self._status in {Status.VULNERABLE, Status.RECOVERED} 

    def vaccinate(self) -> None:
        self.status = Status.VACCINATED

class Population():
    def __init__(self,size = 100) -> None:
       self._people = []
       for i in range(size):
           self._people.append(Person())

    def data(self):
        return self._people

    def count_status(self, status:Status, data=None) -> int:
        if data == None:
            data = self._people
        return sum(p.status == status for p in data)
    
    def num_vulnerable(self,data=None):
        return self.count_status(Status.VULNERABLE,data)

    def num_infectious(self,data=None):
        return self.count_status(Status.INFECTIOUS,data)

    def num_recovered(self,data=None):
        return self.count_status(Status.RECOVERED,data)

    def num_vaccinated(self,data=None):
        return self.count_status(Status.VACCINATED,data)


import random

class SimpleModel():

    def __init__(self, pop:Population) -> None:
        self._pop = pop

    def infect(self, number=1) -> None:
        victim = random.choice(self._pop.data())
        victim.infect()

    def spread(self, cell_size=3) -> None:
        random.shuffle(self._pop.data())
        for group in range(len(self._pop.data())//cell_size):
            sub = self._pop.data()[group*cell_size:(group+1)*cell_size]
            if self._pop.num_infectious(sub) > 0:
                # infect all the vulnerable
                # print("INFECT")
                for x in sub:
                    if x.can_infect():
                        x.recover()
                    if x.can_be_infected():
                        x.infect()
                pass


a = Population()
m = SimpleModel(a)
print(a.num_vulnerable())
print(a.num_infectious())
print(a.num_recovered())
print(a.num_vaccinated())
m.infect()
print(a.num_vulnerable())
print(a.num_infectious())
print(a.num_recovered())
print(a.num_vaccinated())

for i in range(10):
    m.spread()
    print("-----------------------\nRun", i)
    print(a.num_vulnerable())
    print(a.num_infectious())
    print(a.num_recovered())
