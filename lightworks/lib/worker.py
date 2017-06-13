import threading
import time

import lib.db.queue as db
import lib.db.file as fdb
import lib.ffmpeg as ffmpeg

class Thread(threading.Thread):

  def __init__(self,num):
    threading.Thread.__init__(self)
    self._stop_event = threading.Event()
    self.num = num
    self.ffmpeg = None
    print "worker thread {} create".format(num)

  def run(self):
    print "worker thread {} run".format(self.num)
    while not self.stopped():
      print "go {} ".format(self.num)
      try:
        c = db.pop()
        #print "{} :{} #{} {} {} {}".format(self.num, c[0],c[1]['file'],c[1]['type'],c[1]['from'],c[1]['to'])
        
        if c[1]['type'] == 'transcode':
          f = fdb.list(id=c[1]['file'])[0]
          script = None
          print "TRANSCODE {}".format(f.path)
          if c[1]['to'] is fdb.FileMode.INTERMEDIATE and c[1]['from'] is fdb.FileMode.RAW:
            script = 'scripts/intermediate-h264'

          if script is not None:
            self.ffmpeg = ffmpeg.FFMPEG(script, f.path)
 
            self.ffmpeg.start()

            self.ffmpeg.wait()
        
      except IndexError:
        for i in range(5):
          if not self.stopped():
            time.sleep(1)
    print "worker {} done".format(self.num)

  def kill(self):
    print "worker {} kill".format(self.num)
    self._stop_event.set()
    if self.ffmpeg:
      self.ffmpeg.kill()
      self.ffmpeg.wait()

  def stopped(self):
    return self._stop_event.is_set()
