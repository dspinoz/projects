#!/usr/bin/env python

import psutil
import json
import httplib

CUBEHOST = "localhost"
CUBEPORT = 1080

mycpu_times = [];
for cpu in psutil.cpu_times(percpu=True):
  # TBD more on linux
  mycpu_times.append({'user': cpu.user, 'system': cpu.system, 'idle': cpu.idle})

mycpu_times_percent = []
for cpu in psutil.cpu_times_percent(interval=None, percpu=True):
  # TBD more on linux
  mycpu_times_percent.append({
    'user': cpu.user,
    'system': cpu.system,
    'idle': cpu.idle
  })

d = [{'type': 'psutil', 
      'data': { 
        'plugin' : 'cpu_times',
        'value': mycpu_times
      }
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'cpu_times_percent',
	'value': mycpu_times_percent
      }
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'cpu_percent',
	'value': psutil.cpu_percent(interval=None, percpu=True)
      }
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'cpu_count',
	'value': psutil.cpu_count()
      }
    }]

c = httplib.HTTPConnection(CUBEHOST, CUBEPORT)
#c.set_debuglevel(2)

print json.dumps(d, sort_keys = False, indent = 2)

c.request("POST", "/1.0/event/put", json.dumps(d, sort_keys=False), {"Content-type": "application/json"})

r = c.getresponse()
print r.status, r.reason

print r.read()

c.close()



