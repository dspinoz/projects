import os
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
  parser.add_option("-P", "--list-intermediate", dest="list_intermediate", action="store_true", help="List intermediate files")
  parser.add_option("-S", "--list-proxy", dest="list_proxy", action="store_true", help="List proxy files")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0) 

  list = db.list_by_mtime()
  for c in list:
    color_begin = ""
    color_end = ""
    status_text = []
    
    st = os.stat(c.path)
    mt = int(c.get("mtime"))
    
    if not mt == st.st_mtime:
      color_begin = "\x1b[1;31m"
      color_end = "\x1b[0m"
      status_text.append("modified after {}".format(util.time_str(mt)))
      c.set_diff()
    
    ts = util.time_str(st.st_mtime)
    
    sz = int(c.get("size"))
    
    if not sz == st.st_size:
      if len(color_begin) == 0:
        color_begin = "\x1b[1;31m"
        color_end = "\x1b[0m"
      status_text.append("was {} bytes".format(sz))
      c.set_diff()
      
    sz = st.st_size
    
    if options.human:
      sz = util.size_human(sz)

    status_str = ""
    if len(status_text) > 0:
      status_str = " (" + ", ".join(status_text) + ")"
      c.set_diff()
      
    print "{}{} #{:<4} {:>10} {:<10} {}{}{}".format(color_begin, c.status_str(), c.id, sz, ts, os.path.relpath(c.path), status_str, color_end)
  sys.exit(0)
  
