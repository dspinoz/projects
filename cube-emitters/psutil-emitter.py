#!/usr/bin/env python

import sys
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
diskio = psutil.disk_io_counters(perdisk=True)
for name,disk in diskio.iteritems():
  mydisk_io_counters.append({'name': name, 'value': disk.__dict__ })


mynet = []
mynet_io_counters = []
netio = psutil.net_io_counters(pernic=True)
for name, nic in netio.iteritems():
  mynet.append({'name': name})
  mynet_io_counters.append(nic.__dict__)

mynet_connections = []
for net in psutil.net_connections(kind='all'):
  mynet_connections.append(net.__dict__)

myusers = []
for user in psutil.users():
  myusers.append(user.__dict__)

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
        'plugin': 'network',
	'value': {
	  'interfaces': mynet,
	  'net_io_counters': mynet_io_counters
	}
      }
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'net_connections',
	'value': mynet_connections
      }
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'users',
	'value': myusers
      }
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'boot_time',
	'value': psutil.boot_time()
      }
    },
    {
      'type': 'psutil',
      'data': {
        'plugin': 'pids',
	'value': psutil.pids()
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



