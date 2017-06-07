import sys
import optparse
import json

import lib.db.queue as db

desc="""
Queue mode.

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show queue options")
  parser.add_option("-l", "--list", dest="list", action="store_true", help="List queued items")
  parser.add_option("", "--json", dest="json", help="Add new item to queue")
  parser.add_option("", "--file", dest="file", help="File for queued job")
  parser.add_option("", "--delete", dest="delete", help="Delete item from queue")
  parser.add_option("", "--clear", dest="clear", action="store_true", help="Delete all items from queue")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
    
  if options.json and not options.file:
    print "No file provided"
    sys.exit(1)

  if options.list or options.clear:
    for c in db.list():
      if options.clear:
        db.delete(c[0])
      else:
        print ":{} #{} {} {} {}".format(c[0],c[1]['file'],c[1]['type'],c[1]['from'],c[1]['to'])
    sys.exit(0)
  
  if options.json:
    print "#{}".format(db.add(options.file, json.loads(options.json))) 
    sys.exit(0)

  if options.delete:
    db.delete(int(options.delete))
      
  sys.exit(0)
  
