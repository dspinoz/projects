import sys
from datetime import datetime
import os
import optparse

import lib.db.config as cfg
import lib.lwf as lwf

desc="""
Init mode.

Initialise a Lightworks Workflow
"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show init options")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)

  if lwf.data_dir(err=False) is not None:
    print "Lightworks workflow already started at", os.path.relpath(os.path.dirname(lwf.data_dir()))
    sys.exit(1)
  
  print "Initialising Lightworks Workflow..."
  os.makedirs(os.path.join(os.getcwd(),lwf.dir_name))
  cfg.set("hello", datetime.now())
  cfg.set("home", os.getcwd())
  cfg.set("rawdir", "raw")
  cfg.set("intermediatedir", "intermediate")
  cfg.set("proxydir", "proxy")
  cfg.set("rawcopy", "yes")
  cfg.set("intermediatecopy", "yes")
  cfg.set("proxycopy", "yes")
  cfg.set("writeback", "yes")

  for c in cfg.list():
    print "{:<10} = {}".format(c[0], c[1])

  sys.exit(0)
  
