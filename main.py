import simpy
import matplotlib.pyplot as plt
import random
from monitor_resource import MonitoredResource

"""
    Proggetto CMCS 2021 Simone Rizzo
    Modellazione Car Sharing tramite Discrete Event Simulation con Simpy
    Risorse:    N di automobili
    Processi:   Utenti che richiedono le automobili
                Operatori che ricaricano le auto
                 
"""

class User(object):

    def __init__(self, env, automobili, t_spawn, t_utilizzo, n_max_user, fine):
        self.env            = env
        self.automobili     = automobili
        self.action         = env.process(self.run())
        self.c_utenti       = 0
        self.s_utenti       = 0
        self.p_utenti       = 0
        self.c_auto         = 0
        self.a_utenti       = 0
        self.h_attesa_ut    = []
        self.h_utenti       = []
        self.h_served       = []
        self.h_risorse      = []
        self.h_putenti      = []
        self.h_auto         = []
        self.t_spawn        = t_spawn
        self.t_utilizzo     = t_utilizzo
        self.n_max_utenti   = n_max_user
        self.fine = fine

    def run(self):
        i = 0
        while (True and self.n_max_utenti <= 0) or (self.n_max_utenti > 0 and i < self.n_max_utenti):
            yield self.env.timeout(random.uniform(self.t_spawn[0], self.t_spawn[1]))
            self.env.process(self.single_user("User"+str(i)))
            i += 1
        global Fine
        Fine = True

    def single_user(self, name):
        print(name + " arrivato %d " % self.env.now)
        self.c_utenti += 1
        self.h_utenti.append((self.env.now, self.c_utenti))
        print("Risorse: " + str(self.automobili.count))
        spazientito = False
        with self.automobili.request() as req:
            self.a_utenti += 1
            self.h_attesa_ut.append((env.now, self.a_utenti))
            if(MIN_PATIENCE >= 0):
                patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
                results = yield req | self.env.timeout(patience)
                self.a_utenti -= 1
                self.h_attesa_ut.append((env.now, self.a_utenti))
                if req in results:
                    print(name + " auto presa time: %d" % self.env.now)
                    self.c_auto += 1
                    self.h_auto.append((self.env.now, self.c_auto))
                    yield self.env.timeout(random.uniform(self.t_utilizzo[0], self.t_utilizzo[1]))
                else:
                    spazientito = True
            else:
                yield req
                self.a_utenti -= 1
                self.h_attesa_ut.append((env.now, self.a_utenti))
                print(name + " auto presa time: %d" % self.env.now)
                self.c_auto += 1
                self.h_auto.append((self.env.now, self.c_auto))
                yield self.env.timeout(random.uniform(self.t_utilizzo[0], self.t_utilizzo[1]))


        if spazientito:
            print(name + " si è spazientito ed ha chiamato il taxi")
            self.p_utenti += 1

        else:
            print(name + " macchina rilasciata time: %d" % self.env.now)
            self.s_utenti += 1
            self.c_auto -= 1
            self.h_auto.append((self.env.now, self.c_auto))

        self.c_utenti -= 1
        self.h_served.append((self.env.now, self.s_utenti))
        self.h_putenti.append((self.env.now, self.p_utenti))
        self.h_utenti.append((self.env.now, self.c_utenti))


def operatore_ricarica(envirorment, automobili, t_autonomia, t_ricarica, numero_oper):
    macchine_per_operatore = int(n_auto/numero_oper)
    car_list = [macchine_per_operatore]*numero_oper
    car_list[-1] = n_auto - (numero_oper-1)*macchine_per_operatore
    contatore = 0
    while True and not Fine:
        yield envirorment.timeout(t_autonomia)
        if not Fine:
            for i in range(numero_oper):
                envirorment.process(carica_auto(envirorment, "Operatore"+str(i), t_ricarica, automobili, car_list[i]))


def carica_auto(env, nome, time, automobili, auto_da_prendere):
    global count_auto_in_carica
    global ricarica_auto_list
    for i in range(auto_da_prendere):
        with automobili.request() as req:
            yield req
            print(nome+" turno "+str(i) +" presa veicolo per la ricarica time: %d" %env.now)
            count_auto_in_carica += 1
            ricarica_auto_list.append((env.now, count_auto_in_carica))
            yield env.timeout(time)
        print(nome+" caricata veicolo completata time: %d" %env.now)
        count_auto_in_carica -= 1
        ricarica_auto_list.append((env.now, count_auto_in_carica))


def controlla_n_auto(env, automobili, lst):
    while True and not Fine:
        yield env.timeout(1)
        lst.append((env.now, len(automobili.queue)))


""" Parameters list """
t_utilizzo_auto = (28, 35)  # Tempo di utilizzo medio di un utente
t_user_spawn = (1, 4)       # Tempo di arrivo dei nuovi utenti
n_auto = 10              # Numero di automobili disponibili
n_max_utenti = 400         # Numero massimo di utenti se -1 genera gli utenti all'infinito
MIN_PATIENCE = -1           # Min. customer patience -1 se vogliamo togliere la pazienza
MAX_PATIENCE = 13           # Max. customer patience
AUTONOMIA_AUTO = 200        # Tempo massimo di autonomia della macchina
T_CARICA = 60               # Tempo per ricaricare l'automobile
N_Operatori = 5             # Numero Operatori che effettuano la ricarica dell'automobile
Fine = False                # Variabile globale per segnalare la terminazione della simulazione
RUN_UNTIL = -1               # Run until this time 0 to let the users end coming

env = simpy.Environment()
automobili = MonitoredResource(env, capacity=n_auto)
generator = User(env, automobili, t_user_spawn, t_utilizzo_auto, n_max_utenti, fine=Fine)
env.process(operatore_ricarica(env, automobili, AUTONOMIA_AUTO, T_CARICA, N_Operatori))
utilizzo_auto_list = []
ricarica_auto_list = []
count_auto_in_carica=0
env.process(controlla_n_auto(env, automobili, utilizzo_auto_list))
if RUN_UNTIL <= 0:
    env.run()
else:
    env.run(until=RUN_UNTIL)
print("Simulazione terminata")

x, y = list(zip(*generator.h_attesa_ut))
plt.plot(x, y, label='Clienti in attesa')
x2, y2 = (list(zip(*generator.h_utenti)))
plt.plot(x2, y2, label='Clienti totali')
x3, y3 = (list(zip(*generator.h_served)))
# plt.plot(x3, y3, label="Serviti")
x4, y4 = (list(zip(*generator.h_putenti)))
plt.plot(x4, y4, label="Clienti Spazientiti")
x6, y6 = (list(zip(*generator.h_auto)))
plt.plot(x6, y6, label="Auto in uso dai clienti")
x7, y7 = (list(zip(*ricarica_auto_list)))
plt.plot(x7, y7, label="Auto in carica")
plt.xlabel("Time step")
plt.legend()
plt.show()
print(automobili.data)