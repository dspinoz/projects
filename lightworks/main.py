#!/usr/bin/env python
import sys
from optparse import OptionParser

import config

if __name__ == '__main__':
  parser = OptionParser(add_help_option=False)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show help message and exit")
  parser.add_option("-c", "--config-print", dest="config", action="store_true", help="Print current configuration options")
  parser.add_option("", "--config-key", dest="config_key", help="Show value for config option")
  parser.add_option("", "--config-value", dest="config_value", help="Set value for config-key")

  (options,args) = parser.parse_args()

  if options.help:
    print parser.format_help()
    sys.exit(0)

  if options.config:
    for c in config.list():
      print "{} = {}".format(c[0],c[1])

  if options.config_value and options.config_key:
    config.set(options.config_key, options.config_value)

  if options.config_key:
    (k,v) = config.get(options.config_key)
    if k is None:
      print "Invalid option, {}".format(options.config_key)
    else:
      print "{} = {}".format(k,v)
      
