import os
import sys
import threading
import time
import tempfile

import lib.util as u
import lib.add as add
import lib.lwfexcept as lwfexcept
import lib.db.config as cfg
import lib.db.queue as db
import lib.db.file as fdb
import lib.db.project_file as pfdb
import lib.ffmpeg as ffmpeg

class Thread(threading.Thread):

  def __init__(self,num,mode,max,shutdown):
    threading.Thread.__init__(self)
    self._stop_event = threading.Event()
    self.num = num
    self.ffmpeg = None
    self.shutdown = shutdown
    self.mode = mode
    self.max = max
    self.count = 0
    print "worker thread {} create".format(num)

  def run(self):
    u.eprint ("worker thread {} run".format(self.num))
    while not self.shutdown.is_set() and not self.stopped():
      if self.max is not 0 and self.count >= self.max:
        break
      try:
        c = db.pop()
        self.count = self.count + 1
        u.eprint ("{} {}/{}: {} #{} {} {} {}".format(self.num, self.count, self.max, c[0],c[1]['file'],c[1]['type'],c[1]['from'],c[1]['to']))
        
        if c[1]['type'] == 'transcode':
          if self.mode is not c[1]['to']:
            sys.stderr.write("Not transcoding {}\n".format(c[1]['file']))
            continue

          f = fdb.list(id=c[1]['file'])[0]
          script = None
          u.eprint ("TRANSCODE {}".format(f.path))
          transcoded = f.path

          writeback = u.str2bool(cfg.get("writeback")[1])
          if not writeback:
            transcoded = tempfile.NamedTemporaryFile().name
            u.eprint("writing to tmp {}".format(transcoded))

          trans_ext = ""

          if self.mode is fdb.FileMode.INTERMEDIATE and c[1]['from'] is fdb.FileMode.RAW:
            trans_ext = ".int"
            transcoded = transcoded + trans_ext
            script = 'intermediate-h264'
          if self.mode is fdb.FileMode.PROXY:
            trans_ext = ".pxy"
            transcoded = transcoded + trans_ext
            script = 'proxy-h264'

          if script is not None:
            try:
              self.ffmpeg = ffmpeg.FFMPEG(script, f.path, transcoded)
 
              self.ffmpeg.start()

              if self.ffmpeg.wait():
                self.ffmpeg = None
            
              u.eprint ("FFMPEG done? {}".format(self.ffmpeg))

              pfs = pfdb.find(f.id)
              for pf in pfs:
                add.import_file(os.curdir, False, transcoded, c[1]['to'], False, pf.path, storeas=f.path + trans_ext)

              if not writeback:
                os.remove(transcoded)
                u.eprint("removed tmp {}".format(transcoded))
            except lwfexcept.FileInfoError:
              sys.stderr.write("Unable to get file info {}".format(f.path))
            except lwfexcept.FileFFMPEGError:
              sys.stderr.write("Unable to transcode with ffmpeg {}".format(f.path))
            
          else:
            sys.stderr.write("Unable to transcode {}".format(f.path))
      except IndexError:
        for i in range(5):
          if not self.stopped():
            time.sleep(1)
      except Exception as e:
        print e
    u.eprint ("worker {} done".format(self.num))

  def kill(self):
    u.eprint ("worker {} kill".format(self.num))
    self._stop_event.set()
    if self.ffmpeg:
      self.ffmpeg.kill()
      if self.ffmpeg.wait():
        self.ffmpeg = None

  def stopped(self):
    return self._stop_event.is_set()
