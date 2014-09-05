#!/usr/bin/env python

import sys
import os
import socket
import platform
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
    'hostname': socket.gethostname(),
    'platform': platform.platform(),
    'system': sys.platform,
    'machine': platform.machine(),
    'cpu': platform.processor(),
    'system': platform.system(),
    'version': platform.version()
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
  
  linux = platform.linux_distribution()
  system['value']['dist'] = {}
  system['value']['dist']['name'] = linux[0]
  system['value']['dist']['version'] = linux[1]
  system['value']['dist']['id'] = linux[2]
  
elif os.name == 'nt':
  system['value']['boot_time'] = psutil.boot_time()
  
  win = platform.win32_ver()
  system['value']['dist'] = {}
  system['value']['dist']['release'] = win[0]
  system['value']['dist']['version'] = win[1]
  system['value']['dist']['csd'] = win[2]
  system['value']['dist']['ptype'] = win[3]

events.append(system);

sys.stderr.write('INFO 1/7 System\n')

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
 
sys.stderr.write('INFO 2/7 CPU\n')

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
  
sys.stderr.write('INFO 3/7 Disks\n')
  
####################### USERS
i=0
if os.name == 'nt':
  for user in psutil.users():
    events.append({'plugin': 'user', 'index': i, 'value': user._asdict() })
    i += 1
  

sys.stderr.write('INFO 4/7 Users\n')

####################### MEMORY
events.append({'plugin': 'swap_memory', 'value': psutil.swap_memory()._asdict() })
events.append({'plugin': 'virtual_memory', 'value': psutil.virtual_memory()._asdict() })
  
sys.stderr.write('INFO 5/7 Memory\n')

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
  
sys.stderr.write('INFO 6/7 Network\n')

####################### PROCESSES

class SkippedException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

for proc in psutil.process_iter():
  try:
    if os.name == 'nt' and proc.name() == 'ndrvs.exe':
      # psutil just hangs
      raise SkippedException('skipping ' + proc.name())
    p = {};
    for n,i in proc.as_dict().iteritems():
      if i is None:
        continue
    
      # handle os-specific values
      if os.name == 'posix':
        if n in ('ionice'): #dict values
          p[n] = i._asdict()
      
      # consistent across os-es
      if n in ('cpu_times', 'io_counters', 'ext_memory_info', 'uids', 'gids', 'memory_info',  'num_ctx_switches', 'memory_info_ex'): #dict values
        p[n] = i._asdict()
      elif n in ('threads', 'memory_maps', 'connections', 'open_files'): #array values
        if not hasattr(p, n):
          p[n] = []
        for t in i:
          p[n].append(t._asdict())
      else: #others
        p[n] = i
        
  except psutil.NoSuchProcess:
    sys.stderr.write('INFO Process gone: ' + str(proc) + '\n')
  except psutil.AccessDenied:
    #sys.stderr.write('INFO Access denied on process: ' + str(proc) + '\n')
    pass
  except SkippedException:
    sys.stderr.write('INFO Skipped process: ' + str(proc) + '\n')
  except Exception as e:
    sys.stderr.write('FATAL on processing: ' + str(proc) + '\n')
    sys.stderr.write(str(e))
    sys.stderr.write('\n')
    sys.exit(1)
  else:
    events.append({'plugin': 'process', 'value': p })

sys.stderr.write('INFO 7/7 Processes\n')
 
####################### PRINT
  
d = []
for e in events:
  d.append({'type': 'psutil', 'data': e })
  
print json.dumps(d, sort_keys = False, indent = 2)

####################### SUBMIT EVENTS

c = httplib.HTTPConnection(CUBEHOST, CUBEPORT)
#c.set_debuglevel(2)

c.request("POST", "/1.0/event/put", json.dumps(d, sort_keys=False), {"Content-type": "application/json"})

r = c.getresponse()

sys.stderr.write(str(r.status) + ': ' + r.reason + '\n')
sys.stderr.write(r.read() + '\n')

c.close()



