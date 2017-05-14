import sys
import optparse

import lib.lwdb_file as db

desc="""
List mode.

Show files imported to the workflow.
"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show ls options")
  parser.add_option("-l", "--long", dest="long", action="store_true", help="Show long listing")
  parser.add_option("-a", "--all", dest="all", action="store_true", help="List all details")
  parser.add_option("-r", "--recursive", dest="recursive", action="store_true", help="Traverse directories")
  parser.add_option("-R", "--list-raw", dest="list_raw", action="store_true", help="List raw files")
  parser.add_option("-P", "--list-proxy", dest="list_proxy", action="store_true", help="List proxy files")
  parser.add_option("-S", "--list-scaled", dest="list_scaled", action="store_true", help="List scaled files")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
    
  list = db.list_by_size()
  for c in list:
    print "{:<4} {:<10} {}".format(c.id, c.get("size"), c.path)
  sys.exit(0)
  
