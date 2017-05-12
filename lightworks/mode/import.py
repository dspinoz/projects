import sys
import optparse

import lib.lwdb_file as db

desc="""
Import mode.

All files are imported into a Lightworks Workflow.

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show import options")
  parser.add_option("-p", "--path", dest="path", help="Path to files to import")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
    
  if options.path:
    print "Importing",options.path
    sys.exit(0)
      
  print parser.format_help()
  sys.exit(0)
  
