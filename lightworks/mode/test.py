from datetime import datetime
import sys
import os
import optparse

import lib.util as util
import lib.db.file as db

desc="""
Test mode.
"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('', "--help", dest="help", action="store_true", help="Show ls options")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
  
  sys.exit(0)
  
