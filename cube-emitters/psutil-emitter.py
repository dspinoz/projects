#!/usr/bin/env python

import psutil
import json
import httplib

CUBEHOST = "localhost"
CUBEPORT = 1080

d = [{'type': 'psutil', 
      'data': { 
        'plugin' : 'cpu_times',
        'value': psutil.cpu_times().__dict__ 
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



