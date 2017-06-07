import sys
from datetime import datetime
import os
import optparse

import lib.db.config as cfg
import lib.lwf as lwf

desc="""
Home mode.

Shows the current lwf home directory
"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show init options")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)

  print os.path.relpath(os.path.dirname(lwf.data_dir()))
  
  sys.exit(0)
  
