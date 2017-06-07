import sys
import optparse
import json

import lib.db.event as db

desc="""
Event mode.

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show event options")
  parser.add_option("-l", "--list", dest="list", action="store_true", help="List events")
  parser.add_option("", "--json", dest="json", help="Add new event")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
    
  if options.list:
    for c in db.list():
      print "{}".format(c)
    sys.exit(0)
  
  if options.json:
    db.add(json.loads(options.json))
      
  sys.exit(0)
  
