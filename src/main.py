import simpy
import matplotlib.pyplot as plt
import random
from Car import Car

"""
    Project CMCS 2021 Simone Rizzo
    Modelling Car Sharing trought Discrete Event Simulation with Simpy    
    1 time-step = 1 minutes      
"""


class Customer(object):

    def __init__(self, env, avaible, dead, t_spawn, usage_time, n_max_cust, end_simulation):
        self.env = env
        self.cars_avaible = avaible
        self.cars_dead = dead
        self.action = env.process(self.run())
        self.c_customers = 0
        self.s_customers = 0
        self.p_customers = 0
        self.c_cars = 0
        self.a_customers = 0
        self.h_a_cust = []
        self.h_customers = []
        self.h_served = []
        self.h_resources = []
        self.h_p_customers = []
        self.h_cars = []
        self.t_spawn = t_spawn
        self.t_usage = usage_time
        self.n_max_cust = n_max_cust
        self.fine = end_simulation

    """
        The run method spawn Customers
    """
    def run(self):
        i = 0
        while (True and self.n_max_cust <= 0) or (self.n_max_cust > 0 and i < self.n_max_cust):
            yield self.env.timeout(random.uniform(self.t_spawn[0], self.t_spawn[1]))
            self.env.process(self.single_customer("User" + str(i)))
            i += 1
        global end_simulation
        end_simulation = True

    """
        Each customer waits for a ready car.
        If he gets the car he starts the journey
        otherwise he waits up a bit and then calls a taxi
    """
    def single_customer(self, name):
        print(name + " arrived at time: %d " % self.env.now)
        self.customer_enter_in_the_system()
        print("Cars avaibles: " + str(len(self.cars_avaible.items)))
        car_event = self.cars_avaible.get()
        self.customer_start_waiting()
        if MIN_PATIENCE > 0:
            patience = int(random.uniform(MIN_PATIENCE, MAX_PATIENCE))
            patience_event = env.timeout(patience)
            res = yield car_event | patience_event
            if car_event in res:
                self.env.process(self.customer_travel(name, car_event)) # do travel
            else:
                print(name + " si è spazientito ed ha chiamato il taxi")
                self.customer_impatient()
        else:
            yield car_event  # took car
            self.env.process(self.customer_travel(name, car_event)) # do travel

    def customer_travel(self, name, car_event):
        self.car_in_use()
        self.customer_end_waiting()
        car = car_event.value
        print(name, 'got', car.nome, 'at', int(self.env.now))
        t_travel = int(random.uniform(self.t_usage[0], self.t_usage[1]))
        yield self.env.timeout(t_travel)  # do travel
        res = car.aggiorna_capienza(t_travel) # decrease the battery in base of the amount of time of the travel
        if res:
            self.cars_avaible.put(car)
        else:
            self.cars_dead.put(car)
        self.car_released()
        self.customer_exit_from_the_system()
        self.customer_served()

    def customer_enter_in_the_system(self):
        self.c_customers += 1
        self.h_customers.append((self.env.now, self.c_customers))  # customer in the system

    def customer_exit_from_the_system(self):
        self.c_customers -= 1
        self.h_customers.append((self.env.now, self.c_customers))  # customer in the system
        self.update_customer_waiting()
        self.update_car_in_use()
        self.update_customer_served()
        self.update_customer_impatient()

    def customer_start_waiting(self):
        self.a_customers += 1
        self.h_a_cust.append((env.now, self.a_customers))  # customer waiting

    def update_customer_waiting(self):
        self.h_a_cust.append((env.now, self.a_customers))  # customer waiting

    def customer_end_waiting(self):
        self.a_customers -= 1
        self.h_a_cust.append((env.now, self.a_customers))  # customer waiting

    def car_in_use(self):
        self.c_cars += 1
        self.h_cars.append((self.env.now, self.c_cars))  # car in use by customer

    def update_car_in_use(self):
        self.h_cars.append((self.env.now, self.c_cars))  # car in use by customer

    def car_released(self):
        self.c_cars -= 1
        self.h_cars.append((self.env.now, self.c_cars))  # car in use by customer

    def customer_served(self):
        self.s_customers += 1
        self.h_served.append((self.env.now, self.s_customers))  # customer served

    def update_customer_served(self):
        self.h_served.append((self.env.now, self.s_customers))  # customer served

    def customer_impatient(self):
        self.p_customers += 1
        self.h_p_customers.append((self.env.now, self.p_customers))
        self.customer_end_waiting()
        self.customer_exit_from_the_system()

    def update_customer_impatient(self):
        self.h_p_customers.append((self.env.now, self.p_customers))

"""
    Method that represent the single Operator.
"""
def operator(env, name, avaible, dead):
    global count_auto_in_carica
    global charged_cars_list
    while True:
        yield env.timeout(1)
        charged_cars_list.append((env.now, count_auto_in_carica))
        item = yield dead.get()
        count_auto_in_carica += 1
        charged_cars_list.append((env.now, count_auto_in_carica))
        print(name + " turn: " + str(i) + " " + item.nome + " taken for charging at time: %d" % env.now)
        yield env.timeout(CHARGE_TIME)
        print(name + " " + item.nome +" charge completed time: %d" % env.now)
        item.carica()
        avaible.put(item)
        count_auto_in_carica -= 1
        charged_cars_list.append((env.now, count_auto_in_carica))


def initializer(env, cars_avaible):
    for i in range(cars_avaible.capacity):
        yield cars_avaible.put(Car("car" + str(i), AUTO_AUTONOMY))


""" Parameters list """
CAR_USAGE_TIME = (28, 35)       # Range of time of use of a car
USER_SPAWN_TIME = (1, 2)        # Arrival time range of new users
CARS_NUMBER = 20                # Number of cars
MAX_NUMB_USERS = 200            # Max number of users, if -1 it generates infinite users
MIN_PATIENCE = -1               # Min. customer patience, -1 if we would take off patience
MAX_PATIENCE = 18               # Max. customer patience
AUTO_AUTONOMY = 200             # Autonomy of a car in minutes
CHARGE_TIME = 60                # Time to recharge the car
OPERATORS_NUMBER = 20           # Number of Operators who charge the car
RUN_UNTIL = -1                  # Run until this time 0 to let the users end coming

""" RUN simulation """
end_simulation = False
cars_usage_list = []
cars_incharge_list = []
charged_cars_list = []
count_auto_in_carica = 0

env = simpy.Environment()
cars_avaible = simpy.Store(env, capacity=CARS_NUMBER)  # Defining avaible_cars as Store Resources
cars_dead = simpy.Store(env, capacity=CARS_NUMBER)	   # Defining dead_cars as Store Resources
env.process(initializer(env, cars_avaible))  # Inizialization avaible cars
for i in range(OPERATORS_NUMBER):
    env.process(operator(env, "Operator" + str(i), cars_avaible, cars_dead))
generator = Customer(env, cars_avaible, cars_dead, USER_SPAWN_TIME, CAR_USAGE_TIME, MAX_NUMB_USERS,
                     end_simulation=end_simulation)
if RUN_UNTIL <= 0:
    env.run()
else:
    env.run(until=RUN_UNTIL)
print("Simulation ended")

""" Plot functions """
x, y = list(zip(*generator.h_a_cust))
plt.plot(x, y, label='Customers waiting')
x2, y2 = (list(zip(*generator.h_customers)))
plt.plot(x2, y2, label='Customers in the system')
x3, y3 = (list(zip(*generator.h_served)))
plt.plot(x3, y3, label="Total served customers")
if generator.h_p_customers != []:
    x4, y4 = (list(zip(*generator.h_p_customers)))
    plt.plot(x4, y4, label="Impatient customers")
x6, y6 = (list(zip(*generator.h_cars)))
plt.plot(x6, y6, label="Car in use by customers")
if charged_cars_list != []:
    x7, y7 = (list(zip(*charged_cars_list)))
    plt.plot(x7, y7, label="Cars in charge")
plt.xlabel("Time step")
plt.legend()
plt.show()
