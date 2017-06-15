import sys
import optparse
import json
import signal

import lib.db.queue as db
import lib.worker as worker

desc="""
Worker mode. Process the queue!

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show queue options")
  parser.add_option("-l", "--list", dest="list", action="store_true", help="List queued items")
  parser.add_option("", "--file", dest="file", default=None, help="File for queued jobs")
  parser.add_option("", "--num", dest="num", type=int, default=2, help="Number of threads for processing")
  return parser

def shandler(signal,frame):
  sys.stderr.write("SIG!\n {}".format(signal))
  global threads
  for t in threads:
    t.kill()
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
    
  if options.list:
    for c in db.list(options.file):
        print ":{} #{} {} {} {}".format(c[0],c[1]['file'],c[1]['type'],c[1]['from'],c[1]['to'])
    sys.exit(0)
  
  global threads
  threads = []

  for i in range(0,options.num):
    t = worker.Thread(i)
    t.start()
    sys.stderr.write("worker {} started\n".format(i))
    threads.append(t)

  sys.stderr.write("sig pause\n")
  signal.signal(signal.SIGINT, shandler)
  signal.pause()
  sys.stderr.write("sig pause done\n")
  
  for t in threads:
    t.join()
  sys.stderr.write("main done\n")
      
  sys.exit(0)
  
