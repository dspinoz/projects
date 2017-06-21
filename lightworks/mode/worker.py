import sys
import optparse
import json
import signal
import threading

import lib.db.queue as db
import lib.worker as worker
import lib.db.file as fdb

desc="""
Worker mode. Process the queue!

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show queue options")
  parser.add_option("-l", "--list", dest="list", action="store_true", help="List queued items")
  parser.add_option("", "--file", dest="file", default=None, help="File for queued jobs")
  parser.add_option("", "--num", dest="num", type=int, default=1, help="Number of threads for processing")
  parser.add_option("-m", "--mode", dest="mode", help="Current mode of files to import [default: %default]", default="PROXY", choices=["RAW", "INTERMEDIATE", "PROXY"])
  return parser

def shandler(sig,frame):
  sys.stderr.write("SIG!\n {}".format(sig))
  if sig == signal.SIGCHLD:
    return

  global threads
  for t in threads:
    t.kill()
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
    
  if options.mode:
    options.mode = getattr(fdb.FileMode, options.mode)

  if options.list:
    for c in db.list(options.file):
        print ":{} #{} {} {} {}".format(c[0],c[1]['file'],c[1]['type'],c[1]['from'],c[1]['to'])
    sys.exit(0)
  
  global threads
  threads = []

  shutdown_event = threading.Event()

  for i in range(0,options.num):
    t = worker.Thread(i, options.mode, shutdown_event)
    t.start()
    sys.stderr.write("worker {} started\n".format(i))
    threads.append(t)

  sys.stderr.write("sig pause\n")
  signal.signal(signal.SIGINT, shandler)
  signal.signal(signal.SIGCHLD, shandler)
  try:
    for t in threads:
      while t.is_alive():
        t.join(timeout=1.0)
  except (KeyboardInterrupt, SystemExit):
    shutdown_event.set()

  sys.stderr.write("main done\n")
      
  sys.exit(0)
  
