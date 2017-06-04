import threading
import time

class Thread(threading.Thread):

  def __init__(self,num):
    threading.Thread.__init__(self)
    self._stop_event = threading.Event()
    print "worker thread create {}".format(num)

  def run(self):
    print "worker thread run"
    while not self.stopped():
      print "go"
      time.sleep(1)
    print "worker done"

  def kill(self):
    self._stop_event.set()

  def stopped(self):
    return self._stop_event.is_set()
