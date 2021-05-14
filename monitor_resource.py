import simpy
"""
    Estenzione della classe Resource, per tenere traccia dell'utilizzo delle risorse
    per poter visualizzazre i grafici.
"""

class MonitoredResource(simpy.Resource):
 def __init__(self, *args, **kwargs):
     super().__init__(*args, **kwargs)
     self.data = []

 def request(self, *args, **kwargs):
     self.data.append((self._env.now, len(self.queue)))
     return super().request(*args, **kwargs)

 def release(self, *args, **kwargs):
     self.data.append((self._env.now, len(self.queue)))
     return super().release(*args, **kwargs)


def test_process(env, res):
 with res.request() as req:
     yield req
     yield env.timeout(1)