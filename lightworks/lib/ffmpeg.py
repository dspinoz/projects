import os
import sys
import json
import StringIO

import lib.util as u
import lib.execute as execute
import lib.lwfexcept as lwfexcept
import lib.db.file as fdb

PROGRESS_LEN = 10

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
      execute.Executer.__init__(self, ["{}/scripts/info".format(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), path])
      self.path = path
      self.istream = StringIO.StringIO()
      self.duration = -1
  
    def stdout(self,line):
      #u.eprint("info {}".format(line))
      self.istream.write(line)

    def json(self):
      i = self.istream.getvalue()
      #u.eprint(str(i))
      return json.loads(i)

    def wait(self):
      execute.Executer.wait(self)
      if self.returncode() is not 0:
        raise lwfexcept.FileInfoError()

      j = self.json()
      try:
        self.duration = int(float(j['format']['duration']) * 1000000)
      except KeyError:
        sys.stderr.write("Invalid info for {}".format(self.path))
        raise lwfexcept.FileInfoError()

  def __init__(self,script,path,out):
    execute.Executer.__init__(self, ["{}/scripts/{}".format(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), script), path, out])
    self.path = path
    self.out = out
    self.file = fdb.get(path)
    u.eprint("info F {} {}".format(self.file,self.file.get("info")))
    self.info = None
    if self.file.get("info") is None:
      self.info = FFMPEG.Info(path)
    self.progress = FFMPEG.Progress()

  def start(self):
    if self.info is not None:
      self.info.start()
      self.info.wait()
      self.file.set("info", json.dumps(self.info.json()))
      fdb.set(None,"info",json.dumps(self.info.json()),id=self.file.id)
      u.eprint("ffmpeg start - after info")
    execute.Executer.start(self)
  
  def wait(self):
    ret = execute.Executer.wait(self)
    if self.returncode() is not 0:
      raise lwfexcept.FileFFMPEGError()
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
      
    d = None
    if self.info is None:
      j = json.loads(self.file.get("info"))
      d = int(float(j['format']['duration']) * 1000000)
    else:
      d = self.info.duration
    u.eprint("got to the end? {} {}".format(s['out_time_ms'], d));
    return ret

  def stdout(self,line):
    self.progress.write(line)
    if self.progress.isvalid():
      d = None
      if self.info is None:
        j = json.loads(self.file.get("info"))
        d = int(float(j['format']['duration']) * 1000000)
      else:
        d = self.info.duration

      s = self.progress.getstatus()
      u.eprint(str(s))
      
      speed = s['speed'].split('x')[0]
      
      pt = int(s['out_time_ms'])
      tt = d
      
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
