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
    t.killsleep()
    
  if sig == signal.SIGCHLD:
    u.eprint("SIGCHLD!")
    signal.pause()


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
    self.sleep.wait()
    u.eprint("T done sleep")
    
    u.eprint("T run info")
    self.info.start()
    u.eprint("T wait info")
    self.info.wait()
    u.eprint("T done info")
    
    u.eprint("T done")
    
  def killsleep(self):
    u.eprint("T kill sleep")
    if self.sleep:
      self.sleep.kill()
    if self.info:
      self.info.kill()


    

if __name__ == '__main__':
	
  t = T()
  t.start()
  
  u.eprint("AAA")
  
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGCHLD, signal_handler)
  
  u.eprint("SIGNAL PAUSE")
  signal.pause()
  
  u.eprint("SIGNAL DONE")
  sys.exit(0)
  
