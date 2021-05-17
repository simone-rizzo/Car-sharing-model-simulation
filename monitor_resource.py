import simpy
"""
    Extention of Resource class, to keep track of uses of resources
    to plot charts.
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