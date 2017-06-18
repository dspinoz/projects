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

  def __init__(self,num,shutdown):
    threading.Thread.__init__(self)
    self._stop_event = threading.Event()
    self.num = num
    self.ffmpeg = None
    self.shutdown = shutdown
    print "worker thread {} create".format(num)

  def run(self):
    print "worker thread {} run".format(self.num)
    while not self.shutdown.is_set() and not self.stopped():
      print "go {} ".format(self.num)
      try:
        c = db.pop()
        #print "{} :{} #{} {} {} {}".format(self.num, c[0],c[1]['file'],c[1]['type'],c[1]['from'],c[1]['to'])
        
        if c[1]['type'] == 'transcode':
          f = fdb.list(id=c[1]['file'])[0]
          script = None
          print "TRANSCODE {}".format(f.path)
          transcoded = f.path
          if c[1]['to'] is fdb.FileMode.INTERMEDIATE and c[1]['from'] is fdb.FileMode.RAW:
            transcoded = transcoded + ".int"
            script = 'scripts/intermediate-h264'
          if c[1]['to'] is fdb.FileMode.PROXY:
            transcoded = transcoded + ".pxy"
            script = 'scripts/proxy-h264'

          if script is not None:
            u.eprint ("FFMPEG!")
            self.ffmpeg = ffmpeg.FFMPEG(script, f.path, transcoded)
 
            self.ffmpeg.start()

            u.eprint ("FFMPEG! wait")
            if self.ffmpeg.wait():
              self.ffmpeg = None
              u.eprint ("FFMPEG! wait done")
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
    print "worker {} done".format(self.num)

  def kill(self):
    print "worker {} kill".format(self.num)
    self._stop_event.set()
    if self.ffmpeg:
      print "FFMPEG! kill"
      self.ffmpeg.kill()
      print "FFMPEG! kill wait"
      if self.ffmpeg.wait():
        self.ffmpeg = None
      print "FFMPEG! kill wait done"

  def stopped(self):
    return self._stop_event.is_set()
