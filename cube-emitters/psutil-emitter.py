#!/usr/bin/env python

import os
import psutil
import json
import httplib

CUBEHOST = "localhost"
CUBEPORT = 1080

mycpu_times = [];
for cpu in psutil.cpu_times(percpu=True):
  mycpu_times.append(cpu.__dict__)

mycpu_times_percent = []
for cpu in psutil.cpu_times_percent(interval=None, percpu=True):
  mycpu_times_percent.append(cpu.__dict__)

mydisk_partitions = []
mydisk_usage = []
for part in psutil.disk_partitions():
  if os.name == 'nt':
    if 'cdrom' in part.opts or part.fstype == '':
      # skip cd-rom drives with no disk in it; they may raise
      # ENOENT, pop-up a Windows GUI error for a non-ready
      # partition or just hang.
      continue
  mydisk_partitions.append(part.__dict__)
  mydisk_usage.append(psutil.disk_usage(part.mountpoint).__dict__)

mydisk_io_counters = []
for disk in psutil.disk_io_counters(perdisk=True):
  if os.name != 'nt':
    mydisk_io_counters.append(disk.__dict__)

mynet_io_counters = []
for nic in psutil.net_io_counters(pernic=True):
  if os.name != 'nt':
    mynet_io_counters.append(nic.__dict__)


d = [{
     'type': 'psutil',
     'data': {
       'plugin': 'os',
       'value': {
         'name': os.name
       }
     }
    },
    {'type': 'psutil', 
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
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'virtual_memory',
	'value': psutil.virtual_memory().__dict__
      }
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'swap_memory',
	'value': psutil.swap_memory().__dict__
      }
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'disk_partitions',
	'value': mydisk_partitions
      }
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'disk_usage',
	'value': mydisk_usage
      }
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'disk_io_counters',
	'value': mydisk_io_counters
      }
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'net_io_counters',
	'value': mynet_io_counters
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



