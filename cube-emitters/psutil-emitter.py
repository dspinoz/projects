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

system = {
  'plugin': 'system',
  'value': {
    'name': os.name,
    'platform': sys.platform
  }
}

if os.name == 'posix':
  
  f = open('/proc/stat', 'r')
  for line in f:
    tok = line.split(" ")
    if tok[0] == 'btime':
      tok = tok[1].split("\n")
      system['value']['boot_time'] = tok[0]
      break
  f.close()
  
elif os.name == 'nt':
  
  system['value']['boot_time'] = psutil.boot_time()

events.append(system);


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
 
if os.name == 'nt': 
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
  d = { 'plugin':'disk', 'index':i, 'value': part._asdict() }
  d['value']['usage'] = psutil.disk_usage(part.mountpoint)._asdict()
  events.append(d)
  i += 1
  
# split on per-device level
  
i=0
diskio = psutil.disk_io_counters(perdisk=True)
for name,disk in diskio.iteritems():
  events.append({'plugin': 'disk_io', 'index': i, 'value': {'device': name, 'counters': disk._asdict()}})
  i += 1
  
  
####################### USERS
i=0
if os.name == 'nt':
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
if os.name == 'nt':
  for net in psutil.net_connections(kind='all'):
    events.append({'plugin': 'network_connection', 'index': i, 'value': net._asdict() })
    i += 1
  
  
####################### PROCESSES

for proc in psutil.process_iter():
  try:
    p = {};
    for n,i in proc.as_dict().iteritems():
      if n in ('cpu_times', 'io_counters', 'ext_memory_info', 'uids', 'gids', 'memory_info', 'ionice', 'num_ctx_switches'): #dict values
        if i is not None:
          p[n] = i._asdict()
      elif n in ('threads', 'memory_maps', 'connections'): #array values
        if i is not None:
          if not hasattr(p, n):
            p[n] = []
          for t in i:
            p[n].append(t._asdict())
      else: #others
        p[n] = i
  except psutil.NoSuchProcess:
    pass
  else:
    events.append({'plugin': 'process', 'value': p })
  
 
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



