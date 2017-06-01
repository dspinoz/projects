import sys
import json
import StringIO

import lib.util as u
import lib.execute as execute

PROGRESS_LEN = 20

class FFMPEG(execute.Executer):
  
  class Progress:
  
    def __init__(self):
      self.stream = StringIO.StringIO()
      self.valid = False
      self.status = None
      self.new_status = {}
  
    def write(self,data):
      tok = data.split('=')
      self.new_status[tok[0].strip()] = tok[1].strip()
#    u.eprint("progress: {} {}".format(len(self.new_status), self.new_status))
      self.valid = len(self.new_status) == 11
      if self.valid:
        self.status = self.new_status
  
    def isvalid(self):
      return self.valid
    
    def getstatus(self):
      return self.status

  class Info(execute.Executer):
    def __init__(self,path):
      execute.Executer.__init__(self, ["./info", path])
      self.istream = StringIO.StringIO()
  
    def stdout(self,line):
      #u.eprint("info {}".format(line))
      self.istream.write(line)

    def wait(self):
      execute.Executer.wait(self)
      i = self.istream.getvalue()
      u.eprint(i)
      j = json.loads(i)
      self.duration = int(float(j['format']['duration']) * 1000000)

  def __init__(self,script,path):
    execute.Executer.__init__(self, ["./{}".format(script), path, "/tmp/a.mov"])
    self.path = path
    self.info = FFMPEG.Info(path)
    self.progress = FFMPEG.Progress()

  def start(self):
    self.info.start()
    self.info.wait()
    execute.Executer.start(self)
  
  def wait(self):
    execute.Executer.wait(self)
    s = self.progress.getstatus()

    # todo ffmpeg return code error print(self.returncode())
    
    if s['progress'] == "end":
      speed = s['speed'].split('x')[0]
      
      sys.stderr.write("{0: <10} ".format(self.path[-10:]))
      sys.stderr.write("{0: >4}x ".format(speed[0:4]))
      sys.stderr.write("{0: <8} ".format(s['out_time'][0:8]))
      sys.stderr.write(" " * 5)
      sys.stderr.write(" " * PROGRESS_LEN)
      sys.stderr.write("{0: >6}".format(u.size_human(int(s['total_size']))))
      sys.stderr.write("\n")
      
    u.eprint("got to the end? {} {}".format(s['out_time_ms'], self.info.duration));
  
  def stdout(self,line):
    self.progress.write(line)
    if self.progress.isvalid() and self.info.duration:
      s = self.progress.getstatus()
      u.eprint(s)
      
      speed = s['speed'].split('x')[0]
      
      pt = int(s['out_time_ms'])
      tt = self.info.duration
      
      ppf = float(pt)/tt
      ppi = int(ppf * 100)
      
      sys.stderr.write("{0: <10} ".format(self.path[-10:]))
      sys.stderr.write("{0: >4}x ".format(speed[0:4]))
      sys.stderr.write("{0: <8} ".format(s['out_time'][0:8]))
      sys.stderr.write("{0:3d}% ".format(ppi))
     
      cf =  int(ppf*PROGRESS_LEN)
      pb = "=" * cf
      pb = pb + ("-" * (PROGRESS_LEN - cf))
      
      sys.stderr.write(pb)
      sys.stderr.write("{0: >6}".format(u.size_human(int(s['total_size']))))
      sys.stderr.write("\r")
