import sys
import optparse

desc="""Additional help!
"""

from optparse import HelpFormatter as fmt
def decorate(fn):
  def wrapped(self=None, desc=""):
    return '\n'.join( [ fn(self, s).rstrip() for s in desc.split('\n') ] )
  return wrapped
fmt.format_description = decorate(fmt.format_description)

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage="%prog help [help-options]")
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show help options")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
  
  print parser.format_help()
  sys.exit(0)
  
