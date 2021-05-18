import simpy
import matplotlib.pyplot as plt
import random

from simpy import AllOf

from monitor_resource import MonitoredResource

"""
    Project CMCS 2021 Simone Rizzo
    Modelling Car Sharing trought Discrete Event Simulation with Simpy    
    1 time-step = 1 minutes      
"""
class Car:

    def __init__(self, nome, capienza):
        self.nome = nome
        self.capienza_max = capienza
        self.capienza = capienza

    def aggiorna_capienza(self, tempo):
        self.capienza -= tempo
        if self.capienza>0:
            return True
        else:
            return False

    def carica(self):
        self.capienza=self.capienza_max


def initializer(env, cariche):
    for i in range(cariche.capacity):
        yield cariche.put(Car("car"+str(i), 9))
    print(f'Inseriti tutti a %d', env.now)


def consumer(name, env, cariche, scariche):
    print(name, 'requesting car at', env.now)
    t1 = cariche.get()
    t2 = env.timeout(30)
    item = yield t1 | t2
    if t1 in item:
        try:
            car = t1.value
            print(name, 'got', car.nome, 'at', env.now)
            yield env.timeout(5)
            res = car.aggiorna_capienza(5)
            if res:
                cariche.put(car)
            else:
                scariche.put(car)

        except AttributeError:
            print("attribute error")

        # parcheggia la macchina

    elif t2 in item:
        print(name, "si è scocciato at ", env.now)


def ricarcia(env,cariche, scariche):
    while True:
        item = yield scariche.get()
        print("ottenuta auto scarica: "+item.nome)
        yield env.timeout(10)
        print("caricata")
        item.carica()
        cariche.put(item)
        print("rimessa nella pool delle cariche")

env = simpy.Environment()
cariche = simpy.Store(env, capacity=1)
scariche = simpy.Store(env, capacity=1)
prod = env.process(initializer(env, cariche))
cons = env.process(ricarcia(env, cariche, scariche))
for i in range(6):
    env.process(consumer("User" + str(i), env, cariche, scariche))

env.run()