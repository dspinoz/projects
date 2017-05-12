import sys
import optparse

import lib.lwdb_file as db

desc="""
File mode.

The following metadata fields are available:
  
  size      number of bytes contained in the file
  mtime     last time file was modified
  mode      0 RAW, 1 PROXY, 2 SCALED
  
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
  parser.add_option("-R", "--list-raw", dest="list_raw", action="store_true", help="List raw files")
  parser.add_option("-P", "--list-proxy", dest="list_proxy", action="store_true", help="List proxy files")
  parser.add_option("-S", "--list-scaled", dest="list_scaled", action="store_true", help="List scaled files")
  parser.add_option("", "--sort-size", dest="list_sorted_size", action="store_true", help="List known files sorted by file size")
  parser.add_option("", "--sort-mtime", dest="list_sorted_mtime", action="store_true", help="List known files sorted by last modified time")
  parser.add_option("-a", "--add", dest="add", help="Add file at path")
  parser.add_option("-f", "--filter", dest="filter", default=None, help="Filter list of files")
  parser.add_option("-p", "--path", dest="path", default=None, help="File path to modify")
  parser.add_option("-k", "--key", dest="key", default=None, help="Show/Set metadata value for file")
  parser.add_option("-v", "--value", dest="value", help="Set value for file metadata")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
    
  if (options.list or options.list_sorted_size or options.list_sorted_mtime or options.list_raw or options.list_proxy or options.list_scaled) and not options.path:
    list = []
    if options.list_sorted_size:
      list = db.list_by_size()
      for c in list:
        print "{:<4} {:<10} {}".format(c.id, c.get("size"), c.path)
    elif options.list_sorted_mtime:
      list = db.list_by_mtime()
      for c in list:
        print "{:<4} {:<10} {}".format(c.id, c.get("mtime"), c.path)
    elif options.list_raw:
      list = db.list_by_mode(db.FileMode.RAW)
      for c in list:
        print "{:<4} {:<10} {}".format(c.id, c.get("mode"), c.path)
    elif options.list_proxy:
      list = db.list_by_mode(db.FileMode.PROXY)
      for c in list:
        print "{:<4} {:<10} {}".format(c.id, c.get("mode"), c.path)
    elif options.list_scaled:
      list = db.list_by_mode(db.FileMode.SCALED)
      for c in list:
        print "{:<4} {:<10} {}".format(c.id, c.get("mode"), c.path)
    else:
      list = db.list(options.filter)
      for c in list:
        print "{:<4} {}".format(c.id, c.path)
        
    sys.exit(0)
    
  if options.add:
    if db.add(options.add):
      sys.exit(0)  
    sys.exit(1)
    
  if options.path and options.value and options.key:
    db.set(options.path, options.key, options.value)
    # continue to show key
    
  if options.path:
    print options.path
    for a in db.get(options.path, options.key):
      print "{} = {}".format(a[0],a[1])
    sys.exit(0)
      
  print parser.format_help()
  sys.exit(0)
  
