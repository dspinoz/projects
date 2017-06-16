import os
import threading
import Queue
import subprocess
import signal

import lib.util as u

class Executer:

  def __init__(self,args):
    self.args = args
    self.io_q = Queue.Queue()
    self.threads = []
    
    self.threads.append(threading.Thread(target=self.print_output, name='printer'))
    self.proc = None
    
  def start(self):
    u.eprint("Executer starting {}".format(self.args))
    self.proc = subprocess.Popen(self.args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, preexec_fn=os.setsid)
    u.eprint("popen {}".format(self.proc.pid))

    self.threads.append(threading.Thread(target=self.stream_watcher, name='stdout-watcher', args=(self.io_q, 'STDOUT', self.proc.stdout)))
    self.threads.append(threading.Thread(target=self.stream_watcher, name='stderr-watcher', args=(self.io_q, 'STDERR', self.proc.stderr)))

    for t in self.threads:
      u.eprint("t start {}".format(t.name))
      t.start();

  def wait(self, timeout=None):
    
    if self.proc:
      u.eprint ("Waiting for proc to finish {} ... {}".format(timeout,self.args))
      self.proc.wait()
    
    u.eprint("Waiting for proc to finish YEP {}".format(len(self.threads)))
    
    for t in self.threads:
      u.eprint("execute t wait {}".format(t.name))
      t.join(timeout);
      if t.isAlive():
        u.eprint("** STILL ALIVE***")
        return False
     
    u.eprint ("wait. all Done!")
    return True
    
  def returncode(self):
    return self.proc.returncode

  def poll(self):
    self.proc_ret = self.proc.poll()
    
    if self.proc_ret is not None:
      u.eprint("proc down...")
      return False
    else:
      #u.eprint("proc up...")
      return True
      

  def stream_watcher(self, queue, identifier, stream):
    #while not stream.closed:
    #  line = stream.readline()
    #  if not line:
    #    break
    #  queue.put((identifier, line))
    while not stream.closed and self.poll():
      #u.eprint("Stream {} not closed".format(identifier))
      for line in iter(stream.readline, b''):
        #queue.put((identifier, line))
        if identifier == "STDOUT":
          self.stdout(line)
    #u.eprint("t done {}".format(identifier))

  def print_output(self):
    while not self.io_q.empty() or self.poll():
      try:
        #u.eprint("print_output poll");
        it = self.io_q.get(timeout=1)
        #it = self.io_q.get_nowait()
        identifier,line = it
        #u.eprint("{}:{}".format(identifier,line))
      except Queue.Empty as e:
        #u.eprint("q empty")
        pass
    #u.eprint("t done print")

  def stdout(self,line):
    pass
        
  def kill(self,timeout=None):
    if self.proc:
      u.eprint("Killing... {}".format(self.proc.pid))
      self.proc.terminate()

