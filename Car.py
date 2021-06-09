"""
Class that represent Car object.
"""

class Car:

    def __init__(self, nome, capienza):
        self.nome = nome
        self.capienza_max = capienza
        self.capienza = capienza

    def decrease_battery(self, tempo):
        self.capienza -= tempo
        if self.capienza>0:
            return True
        else:
            return False

    def charge_battery(self):
        self.capienza=self.capienza_max