import sys
import optparse

import lib.lwdb_file as db

desc="""
File mode.

== Filtering
Uses SQL LIKE-expressions, eg. use % as a wildcard

Examples:

  --filter="%.mov"    Only show '.mov' files
  --filter="abc%"     Show all files that start with 'abc'

Refer to http://sqlite.org/lang_expr.html#like for additional information.

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show file options")
  parser.add_option("-l", "--list", dest="list", action="store_true", help="List known files")
  parser.add_option("-a", "--add", dest="path", help="Add file at path")
  parser.add_option("-f", "--filter", dest="filter", default=None, help="Filter list of files")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
    
  if options.list:
    for c in db.list(options.filter):
      print "{}".format(c[0])
    sys.exit(0)
    
  if options.path:
    if db.add(options.path):
      sys.exit(0)  
    sys.exit(1)
      
  print parser.format_help()
  sys.exit(0)
  
