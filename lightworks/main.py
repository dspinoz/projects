#!/usr/bin/env python
import os
import sys
import optparse
from importlib import import_module
import re

desc="""lwworkflow

Lightworks Workflow Helper script to aid video editing.

This workflow helps to ensure the "best possible" performance while editing video, even on low-end machines.

Available commands:
  help
  config
  file
  import
"""

from optparse import HelpFormatter as fmt
def decorate(fn):
  def wrapped(self=None, desc=""):
    return '\n'.join( [ fn(self, s).rstrip() for s in desc.split('\n') ] )
  return wrapped
fmt.format_description = decorate(fmt.format_description)
	
  
class IgnoreUnknownOptionParser(optparse.OptionParser):
  def error(self,msg):
    if re.match("no such option:", msg) is None:
      optparse.OptionParser.error(self,msg)
  
if __name__ == '__main__':

  os.stat_float_times(False)

  parser = IgnoreUnknownOptionParser(add_help_option=False, description=desc, usage="%prog [options] command [command-options]")
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show help message and exit")
  
  (options,args) = parser.parse_args()

  if len(args) is 0:
    print parser.format_help()
    sys.exit(0)
      
  mode = None
  try:
    mode = import_module("mode.{}".format(args[0]))
    
    p = mode.get_parser()
    
    (options,args) = p.parse_args()
    
    mode.parser_hook(p, options, args)
    
    sys.exit(0)
    
  except ImportError as e:
    print "Invalid mode, {}: {}".format(args[0], e)
    sys.exit(1)
    
