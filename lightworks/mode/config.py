import sys
import optparse

import lib.config

desc="""
Configuration mode.

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show config options")
  parser.add_option("-l", "--list", dest="list", action="store_true", help="List current configuration options")
  parser.add_option("-k", "--key", dest="key", help="Show value for config key")
  parser.add_option("-v", "--value", dest="value", help="Set value for config key")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
    
  if options.list:
    for c in lib.config.list():
      print "{} = {}".format(c[0],c[1])
    sys.exit(0)
  
  if options.value and options.key:
    lib.config.set(options.key, options.value)
    sys.exit(0)

  if options.key:
    (k,v) = lib.config.get(options.key)
    if k is None:
      print "Invalid option, {}".format(options.key)
      sys.exit(1)
    else:
      print "{} = {}".format(k,v)
      sys.exit(0)
      
  print parser.format_help()
  sys.exit(0)
  
