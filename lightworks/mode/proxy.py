import os
import sys
import optparse
import shutil

import lib.util as u
import lib.lwf as lwf
import lib.lwf_file as lwf_file
import lib.lwfexcept as lwfexcept
import lib.db.config as cfg
import lib.db.file as fdb
import lib.db.project_file as pdb

desc="""
Switch to proxy files.

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('', "--help", dest="help", action="store_true", help="Show proxy options")
  parser.add_option("-l", "--list", dest="list_proxy", action="store_true", help="List proxy files")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
 
  f = lwf_file.LWFFile(fdb.FileMode.PROXY)
  f.set()

  sys.exit(0)
  
