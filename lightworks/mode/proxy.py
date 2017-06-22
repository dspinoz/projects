import os
import sys
import optparse

import lib.util as util
import lib.lwfexcept as lwfexcept
import lib.db.file as fdb
import lib.db.project_file as pdb

desc="""
Switch to proxy files.

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('', "--help", dest="help", action="store_true", help="Show proxy options")
  parser.add_option("-S", "--list-proxy", dest="list_proxy", action="store_true", help="List proxy files")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
 
  list = []

  try:
    list = pdb.list()
  except lwfexcept.ProjectFileNotFoundError:
    pass

  for c in list:
    c.fetch()

    f = c.get(fdb.FileMode.PROXY)
    print c.path,c.get(fdb.FileMode.PROXY)

  sys.exit(0)
  
