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

class Customer(object):

    def __init__(self, env, cars, t_spawn, usage_time, n_max_cust, end_simulation):
        self.env                = env
        self.cars               = cars
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
        print("Cars avaibles: " + str(self.cars.count))
        impatient = False
        with self.cars.request() as req:
            self.a_customers += 1
            self.h_a_cust.append((env.now, self.a_customers))
            if(MIN_PATIENCE >= 0):
                patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
                results = yield req | self.env.timeout(patience)
                self.a_customers -= 1
                self.h_a_cust.append((env.now, self.a_customers))
                if req in results:
                    print(name + " automobile taken at the time: %d" % self.env.now)
                    self.c_cars += 1
                    self.h_cars.append((self.env.now, self.c_cars))
                    yield self.env.timeout(random.uniform(self.t_usage[0], self.t_usage[1]))
                else:
                    impatient = True
            else:
                yield req
                self.a_customers -= 1
                self.h_a_cust.append((env.now, self.a_customers))
                print(name + " automobile taken at the time: %d" % self.env.now)
                self.c_cars += 1
                self.h_cars.append((self.env.now, self.c_cars))
                yield self.env.timeout(random.uniform(self.t_usage[0], self.t_usage[1]))


        if impatient:
            print(name + " si è spazientito ed ha chiamato il taxi")
            self.p_customers += 1

        else:
            print(name + " automobile released time: %d" % self.env.now)
            self.s_customers += 1
            self.c_cars -= 1
            self.h_cars.append((self.env.now, self.c_cars))

        self.c_customers -= 1
        self.h_served.append((self.env.now, self.s_customers))
        self.h_p_customers.append((self.env.now, self.p_customers))
        self.h_customers.append((self.env.now, self.c_customers))


def operator_generator(envirorment, cars, t_duration, t_charge, n_oper):
    car_each_oper = int(CARS_NUMBER / n_oper)
    car_list = [car_each_oper] * n_oper
    car_list[-1] = CARS_NUMBER - (n_oper - 1) * car_each_oper
    while True and not end_simulation:
        yield envirorment.timeout(t_duration)
        if not end_simulation:
            events = [envirorment.process(single_operator(envirorment, "Operator" + str(i), t_charge, cars, car_list[i])) for i in range(n_oper)]
            yield AllOf(envirorment, events)
            """for i in range(n_oper):
                yield envirorment.process(single_operator(envirorment, "Operator" + str(i), t_charge, cars, car_list[i]))"""


def single_operator(env, name, time, cars, n_cars_to_take):
    global count_auto_in_carica
    global charged_cars_list
    for i in range(n_cars_to_take):
        with cars.request() as req:
            yield req
            print(name + " turn: " + str(i) + " vehicle taken for charging at time: %d" % env.now)
            count_auto_in_carica += 1
            charged_cars_list.append((env.now, count_auto_in_carica))
            yield env.timeout(time)
        print(name + " vehicle charge completed time: %d" % env.now)
        count_auto_in_carica -= 1
        charged_cars_list.append((env.now, count_auto_in_carica))


def control_n_auto(env, cars, lst):
    while True and not end_simulation:
        yield env.timeout(1)
        lst.append((env.now, len(cars.queue)))


""" Parameters list """
CAR_USAGE_TIME = (28, 35)       # Range of time of use of a car
USER_SPAWN_TIME = (1, 4)        # Arrival time range of new users
CARS_NUMBER = 10                # Number of cars
MAX_NUMB_USERS = 400            # Max number of users, if -1 it generates infinite users
MIN_PATIENCE = 1                # Min. customer patience, -1 if we would take off patience
MAX_PATIENCE = 13               # Max. customer patience
AUTO_AUTONOMY = 10             # Autonomy of a car
CHARGE_TIME = 60                # Time to recharge the car
OPERATORS_NUMBER = 5            # Number of Operators who charge the car
RUN_UNTIL = -1                  # Run until this time 0 to let the users end coming

""" RUN simulation """
end_simulation = False
cars_usage_list = []
charged_cars_list = []
count_auto_in_carica = 0
env = simpy.Environment()
cars = MonitoredResource(env, capacity=CARS_NUMBER) # Defining the cars as Resources
generator = Customer(env, cars, USER_SPAWN_TIME, CAR_USAGE_TIME, MAX_NUMB_USERS, end_simulation=end_simulation)
env.process(operator_generator(env, cars, AUTO_AUTONOMY, CHARGE_TIME, OPERATORS_NUMBER))
env.process(control_n_auto(env, cars, cars_usage_list))
if RUN_UNTIL <= 0:
    env.run()
else:
    env.run(until=RUN_UNTIL)
print("Simulazione terminata")

""" Plot functions """
x, y = list(zip(*generator.h_a_cust))
plt.plot(x, y, label='Customers waiting')
x2, y2 = (list(zip(*generator.h_customers)))
# plt.plot(x2, y2, label='Customers in the system')
x3, y3 = (list(zip(*generator.h_served)))
# plt.plot(x3, y3, label="Total served customers")
x4, y4 = (list(zip(*generator.h_p_customers)))
plt.plot(x4, y4, label="Impatient customers")
x6, y6 = (list(zip(*generator.h_cars)))
plt.plot(x6, y6, label="Car in use by customers")
x7, y7 = (list(zip(*charged_cars_list)))
plt.plot(x7, y7, label="Cars in charge")
plt.xlabel("Time step")
plt.legend()
plt.show()