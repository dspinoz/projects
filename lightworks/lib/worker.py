import os
import sys
import threading
import time

import lib.util as u
import lib.add as add
import lib.db.queue as db
import lib.db.file as fdb
import lib.db.project_file as pfdb
import lib.ffmpeg as ffmpeg

class Thread(threading.Thread):

  def __init__(self,num,mode,shutdown):
    threading.Thread.__init__(self)
    self._stop_event = threading.Event()
    self.num = num
    self.ffmpeg = None
    self.shutdown = shutdown
    self.mode = mode
    print "worker thread {} create".format(num)

  def run(self):
    u.eprint ("worker thread {} run".format(self.num))
    while not self.shutdown.is_set() and not self.stopped():
      try:
        c = db.pop()
        u.eprint ("{} :{} #{} {} {} {}".format(self.num, c[0],c[1]['file'],c[1]['type'],c[1]['from'],c[1]['to']))
        
        if c[1]['type'] == 'transcode':
          if self.mode is not c[1]['to']:
            sys.stderr.write("Not transcoding {}".format(c[1]['file']))
            next

          f = fdb.list(id=c[1]['file'])[0]
          script = None
          u.eprint ("TRANSCODE {}".format(f.path))
          transcoded = f.path

          if self.mode is fdb.FileMode.INTERMEDIATE and c[1]['from'] is fdb.FileMode.RAW:
            transcoded = transcoded + ".int"
            script = 'scripts/intermediate-h264'
          if self.mode is fdb.FileMode.PROXY:
            transcoded = transcoded + ".pxy"
            script = 'scripts/proxy-h264'

          if script is not None:
            self.ffmpeg = ffmpeg.FFMPEG(script, f.path, transcoded)
 
            self.ffmpeg.start()

            if self.ffmpeg.wait():
              self.ffmpeg = None
            
            u.eprint ("FFMPEG done? {}".format(self.ffmpeg))

            pfs = pfdb.find(f.id)
            for pf in pfs:
              add.import_file(os.curdir, False, transcoded, c[1]['to'], False, pf.path)


          else:
            sys.stderr.write("Unable to transcode {}".format(f.path))
      except IndexError:
        for i in range(5):
          if not self.stopped():
            time.sleep(1)
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
