from datetime import datetime
import sys
import optparse

import lib.util as util
import lib.lwdb_file as db

desc="""
List mode.

Show files imported to the workflow.
"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('', "--help", dest="help", action="store_true", help="Show ls options")
  parser.add_option("-l", "--long", dest="long", action="store_true", help="Show long listing")
  parser.add_option("-a", "--all", dest="all", action="store_true", help="List all details")
  parser.add_option("-h", "--human", dest="human", action="store_true", help="List size in human readable format")
  parser.add_option("-r", "--recursive", dest="recursive", action="store_true", help="Traverse directories")
  parser.add_option("-R", "--list-raw", dest="list_raw", action="store_true", help="List raw files")
  parser.add_option("-P", "--list-proxy", dest="list_proxy", action="store_true", help="List proxy files")
  parser.add_option("-S", "--list-scaled", dest="list_scaled", action="store_true", help="List scaled files")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)

  now = datetime.now()    

  list = db.list_by_mtime()
  for c in list:
    t = datetime.fromtimestamp(float(c.get("mtime")))
    ts = t.strftime("%b %d %H:%S")
    if now.year != t.year:
      ts = t.strftime("%b %d  %G")
    
    sz = int(c.get("size"))
    if options.human:
      sz = util.size_human(sz)

    print "{} {:>4} {:<6} {:<10} {}".format(c.status_str(), c.id, sz, ts, c.path)
  sys.exit(0)
  
