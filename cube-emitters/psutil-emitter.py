#!/usr/bin/env python

import sys
import os
import psutil
import json
import httplib

CUBEHOST = "localhost"
CUBEPORT = 1080

events = [];

####################### SYSTEM

events.append({
  'plugin': 'system',
  'value': {
    'name': os.name,
    'platform': sys.platform,
    'boot_time': psutil.boot_time()
  }
})

print events
sys.exit(0)

####################### CPU
cpus = []

for cpu in psutil.cpu_times(percpu=True):
  cpus.append({'times':cpu._asdict()})

i=0
for cpu in psutil.cpu_times_percent(interval=None, percpu=True):
  cpus[i]['times_percent'] = cpu._asdict()
  i += 1
  
i=0
for perc in psutil.cpu_percent(interval=None, percpu=True):
  cpus[i]['percent'] = perc
  i += 1
  
i=0
for c in cpus:
  events.append({'plugin': 'cpu', 'index': i, 'value': c})
  i += 1
  
events.append({'plugin': 'cpu_count', 'value': psutil.cpu_count() })
  
####################### DISK

i=0
disks = []
for part in psutil.disk_partitions():
  if os.name == 'nt':
    if 'cdrom' in part.opts or part.fstype == '':
      # skip cd-rom drives with no disk in it; they may raise
      # ENOENT, pop-up a Windows GUI error for a non-ready
      # partition or just hang.
      continue
  disks.append(part._asdict());
  disks[i]['usage'] = psutil.disk_usage(part.mountpoint)._asdict()
  i += 1
  
i=0
diskio = psutil.disk_io_counters(perdisk=True)
for name,disk in diskio.iteritems():
  disks[i]['io_counters'] = disk._asdict()
  i += 1

i=0
for d in disks:
  events.append({'plugin': 'disk', 'index': i, 'value': d})
  i += 1
  
  
####################### USERS
i=0
for user in psutil.users():
  events.append({'plugin': 'user', 'index': i, 'value': user._asdict() })
  i += 1
  

####################### MEMORY
events.append({'plugin': 'swap_memory', 'value': psutil.swap_memory()._asdict() })
events.append({'plugin': 'virtual_memory', 'value': psutil.virtual_memory()._asdict() })
  
  
####################### NETWORK

i=0
netio = psutil.net_io_counters(pernic=True)
for name, nic in netio.iteritems():
  events.append({'plugin': 'network', 'index': i, 'interface': name, 'io_counters': nic._asdict()})
  i += 1
  

i=0
for net in psutil.net_connections(kind='all'):
  events.append({'plugin': 'network_connection', 'index': i, 'value': net._asdict() })
  i += 1
  
 
####################### PRINT
  
print json.dumps(events, sort_keys = False, indent = 2)

####################### SUBMIT EVENTS

d = []
for e in events:
  d.append({'type': 'psutil', 'data': e })

c = httplib.HTTPConnection(CUBEHOST, CUBEPORT)
#c.set_debuglevel(2)

c.request("POST", "/1.0/event/put", json.dumps(d, sort_keys=False), {"Content-type": "application/json"})

r = c.getresponse()
print r.status, r.reason

print r.read()

c.close()



