import threading
import time

class Thread(threading.Thread):

  def __init__(self,num):
    threading.Thread.__init__(self)
    self._stop_event = threading.Event()
    self.num = num
    print "worker thread {} create".format(num)

  def run(self):
    print "worker thread {} run".format(self.num)
    while not self.stopped():
      print "go {} ".format(self.num)
      time.sleep(1)
    print "worker {} done".format(self.num)

  def kill(self):
    self._stop_event.set()

  def stopped(self):
    return self._stop_event.is_set()
