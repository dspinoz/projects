import sys
import optparse
import json

import lib.lwdb_queue as db

desc="""
Queue mode.

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show queue options")
  parser.add_option("-l", "--list", dest="list", action="store_true", help="List queued items")
  parser.add_option("", "--json", dest="json", help="Add new item to queue")
  parser.add_option("", "--delete", dest="delete", help="Delete item from queue")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
    
  if options.list:
    for c in db.list():
      print "#{} {}".format(c[0],c[1])
    sys.exit(0)
  
  if options.json:
    print "#{}".format(db.add(json.loads(options.json))) 
    sys.exit(0)

  if options.delete:
    db.delete(int(options.delete))
      
  sys.exit(0)
  
