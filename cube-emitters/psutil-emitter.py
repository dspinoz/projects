#!/usr/bin/env python

import psutil
import json
import socket
import time

IP = "127.0.0.1"
PORT = 1080

d = { 'type': 'cpu_times', 'time': time.strftime("%Y-%m-%dT%H:%M:%S"), 'data': psutil.cpu_times().__dict__ }

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
if sock.sendto(json.dumps(d), (IP, PORT)) > 0:
	print json.dumps(d)
else:
	print "ERROR"





