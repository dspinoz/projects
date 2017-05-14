import sys
import os
import optparse

import lib.util as util
import lib.lwdb_file as db

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

  searching_for = ".lwf"
  start_path = os.path.realpath(os.getcwd())

  last_root    = start_path
  current_root = start_path
  found_path   = None

  while found_path is None and current_root:
    print "a",current_root
    if os.path.exists(os.path.join(current_root,searching_for)) and os.path.isdir(os.path.join(current_root,searching_for)):
      # found the file, stop
      found_path = os.path.join(current_root, searching_for)
      break

    if current_root == "/":
      print "*"
      break

    # Otherwise, pop up a level, search again
    last_root    = current_root
    (head,tail) = os.path.split(current_root)
    current_root = head

  print found_path


  if found_path is None:
    print "new"
  else:
    print found_path,os.path.relpath(found_path)


  sys.exit(0)
  
