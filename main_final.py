import simpy
import matplotlib.pyplot as plt
import random
from simpy import AllOf

from Car import Car
from monitor_resource import MonitoredResource

"""
    Project CMCS 2021 Simone Rizzo
    Modelling Car Sharing trought Discrete Event Simulation with Simpy    
    1 time-step = 1 minutes      
"""

class Customer(object):

    def __init__(self, env, avaible, dead, t_spawn, usage_time, n_max_cust, end_simulation):
        self.env                = env
        self.cars_avaible       = avaible
        self.cars_dead          = dead
        self.action             = env.process(self.run())
        self.c_customers        = 0
        self.s_customers        = 0
        self.p_customers        = 0
        self.c_cars             = 0
        self.a_customers        = 0
        self.h_a_cust           = []
        self.h_customers        = []
        self.h_served           = []
        self.h_resources        = []
        self.h_p_customers      = []
        self.h_cars             = []
        self.t_spawn            = t_spawn
        self.t_usage            = usage_time
        self.n_max_cust       = n_max_cust
        self.fine = end_simulation

    def run(self):
        i = 0
        while (True and self.n_max_cust <= 0) or (self.n_max_cust > 0 and i < self.n_max_cust):
            yield self.env.timeout(random.uniform(self.t_spawn[0], self.t_spawn[1]))
            self.env.process(self.single_customer("User" + str(i)))
            i += 1
        global end_simulation
        end_simulation = True

    def single_customer(self, name):
        print(name + " arrived at time: %d " % self.env.now)
        self.c_customers += 1
        self.h_customers.append((self.env.now, self.c_customers))
        print("Cars avaibles: " + str(len(self.cars_avaible.items)))
        impatient = False
        self.a_customers += 1
        self.h_a_cust.append((env.now, self.a_customers))
        item = self.cars_avaible.get()
        if (MIN_PATIENCE >= 0):
            patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
            result = yield item | env.timeout(patience) #car get
            self.a_customers -= 1
            self.h_a_cust.append((env.now, self.a_customers))
            if item in result:
                print(name + " automobile taken at the time: %d" % self.env.now)
                self.c_cars += 1
                self.h_cars.append((self.env.now, self.c_cars))
                t_travel = random.uniform(self.t_usage[0], self.t_usage[1])
                yield self.env.timeout(t_travel)
            else:
                impatient = True
                print(name + " si è spazientito ed ha chiamato il taxi")
                self.p_customers += 1
                self.h_p_customers.append((self.env.now, self.p_customers))
        else:
            yield item
            print(name + " automobile taken at the time: %d" % self.env.now)
            self.c_cars += 1
            self.h_cars.append((self.env.now, self.c_cars))
            t_travel = random.uniform(self.t_usage[0], self.t_usage[1])
            yield self.env.timeout(t_travel)

        if impatient:
            print(name + " si è spazientito ed ha chiamato il taxi")
            self.p_customers += 1
            self.h_p_customers.append((self.env.now, self.p_customers))
        else:
            self.s_customers += 1
            self.c_cars -= 1
            print(name + " automobile released time: %d" % self.env.now)
            res = item.value.aggiorna_capienza(t_travel)
            if res:
                self.cars_avaible.put(item)
            else:
                self.cars_dead.put(item)
        self.c_customers -= 1
        self.h_cars.append((self.env.now, self.c_cars))
        self.h_served.append((self.env.now, self.s_customers))
        self.h_customers.append((self.env.now, self.c_customers))


def single_operator(env, name, cars_avaible, cars_dead, n_cars_to_take):
    global count_auto_in_carica
    global charged_cars_list
    for i in range(n_cars_to_take):
        item = yield cars_dead.get()
        print(name + " turn: " + str(i) + " vehicle taken for charging at time: %d" % env.now)
        count_auto_in_carica += 1
        charged_cars_list.append((env.now, count_auto_in_carica))
        yield env.timeout(CHARGE_TIME)
        print(name + " vehicle charge completed time: %d" % env.now)
        item.carica()
        cars_avaible.put(item)
        count_auto_in_carica -= 1
        charged_cars_list.append((env.now, count_auto_in_carica))


def control_n_auto(env, cars, dead, avaible, incharge):
    while True and not end_simulation:
        yield env.timeout(1)
        avaible.append((env.now, len(cars.items)))
        incharge.append((env.now, len(dead.items)))


def operator(env, avaible, dead):
    global count_auto_in_carica
    global charged_cars_list
    while True:
        item = yield dead.get()
        count_auto_in_carica += 1
        charged_cars_list.append((env.now, count_auto_in_carica))
        yield env.timeout(CHARGE_TIME)
        item.carica()
        avaible.put(item)
        count_auto_in_carica -= 1
        charged_cars_list.append((env.now, count_auto_in_carica))


def initializer(env, cars_avaible):
    for i in range(cars_avaible.capacity):
        yield cars_avaible.put(Car("car"+str(i), AUTO_AUTONOMY))

""" Parameters list """
CAR_USAGE_TIME = (28, 35)       # Range of time of use of a car
USER_SPAWN_TIME = (1, 4)        # Arrival time range of new users
CARS_NUMBER = 7                 # Number of cars
MAX_NUMB_USERS = 150            # Max number of users, if -1 it generates infinite users
MIN_PATIENCE = 1                # Min. customer patience, -1 if we would take off patience
MAX_PATIENCE = 13               # Max. customer patience
AUTO_AUTONOMY = 200             # Autonomy of a car
CHARGE_TIME = 40                # Time to recharge the car
OPERATORS_NUMBER = 5            # Number of Operators who charge the car
RUN_UNTIL = -1                  # Run until this time 0 to let the users end coming

""" RUN simulation """
end_simulation = False
cars_usage_list = []
cars_incharge_list = []
charged_cars_list = []
count_auto_in_carica = 0

env = simpy.Environment()
cars_avaible = simpy.Store(env, capacity=CARS_NUMBER) # Defining the cars as Resources
cars_dead = simpy.Store(env, capacity=CARS_NUMBER)
env.process(initializer(env, cars_avaible)) #Inizializza le auto disponibili
for i in range(OPERATORS_NUMBER):
    env.process(operator(env, cars_avaible, cars_dead)) #Inizializza le auto scariche
generator = Customer(env, cars_avaible, cars_dead, USER_SPAWN_TIME, CAR_USAGE_TIME, MAX_NUMB_USERS, end_simulation=end_simulation)
if RUN_UNTIL <= 0:
    env.run()
else:
    env.run(until=RUN_UNTIL)
print("Simulazione terminata")

""" Plot functions """
x, y = list(zip(*generator.h_a_cust))
plt.plot(x, y, label='Customers waiting')
x2, y2 = (list(zip(*generator.h_customers)))
plt.plot(x2, y2, label='Customers in the system')
x3, y3 = (list(zip(*generator.h_served)))
plt.plot(x3, y3, label="Total served customers")
x4, y4 = (list(zip(*generator.h_p_customers)))
plt.plot(x4, y4, label="Impatient customers")
x6, y6 = (list(zip(*generator.h_cars)))
plt.plot(x6, y6, label="Car in use by customers")
# x7, y7 = (list(zip(*charged_cars_list)))
# plt.plot(x7, y7, label="Cars in charge")
plt.xlabel("Time step")
plt.legend()
plt.show()