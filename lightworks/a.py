#!/usr/bin/env python

import sys
import signal
import threading

import lib.util as u
import lib.execute as e

def signal_handler(sig,frame):
  u.eprint("SIG {} {}".format(sig,frame))
  
  if sig == signal.SIGINT:
    u.eprint("SIGINT!")
    stop_event.set()
    t.killsleep()
    
  if sig == signal.SIGCHLD:
    u.eprint("SIGCHLD!")


class T(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    u.eprint("T init")
    self.sleep = e.Executer(["sleep","1"])
    self.info = e.Executer(["sleep","2"])
    
  def run(self):
    threading.Thread.run(self)
    u.eprint("T run")
    
    u.eprint("T run sleep")
    self.sleep.start()
    u.eprint("T wait sleep")
    if self.sleep.wait():
      self.sleep = None
    u.eprint("T done sleep")
    
    u.eprint("T run info")
    self.info.start()
    u.eprint("T wait info")
    if self.info.wait():
      self.info = None
    u.eprint("T done info")
    
    u.eprint("T done")
    stop_event.set()
    
  def killsleep(self):
    u.eprint("T kill sleep")
    if self.sleep:
      self.sleep.kill()
    if self.info:
      self.info.kill()


    

if __name__ == '__main__':
	
  stop_event = threading.Event()
    
  t = T()
  t.start()
  
  u.eprint("AAA")
  
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGCHLD, signal_handler)
  
  u.eprint("MAIN PAUSE")
#  while not stop_event.is_set() and t.is_alive():
#    signal.pause()
  

  try:
    while t.is_alive():
      t.join(timeout=1.0)
  except (KeyboardInterrupt, SystemExit):
    stop_event.set()


 
  u.eprint("MAIN DONE")
  sys.exit(0)
  
