import os
import sys
import optparse

import lib.lwdb_file as db

desc="""
Import mode.

All files are imported into a Lightworks Workflow.

The following metadata fields are available:
  
  size      number of bytes contained in the file
  mtime     last time file was modified
  mode      0 RAW, 1 PROXY, 2 SCALED

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show import options")
  parser.add_option("-p", "--path", dest="path", help="Path to files to import")
  parser.add_option("-m", "--mode", dest="mode", help="Current mode of files to import", default="RAW", choices=["RAW", "PROXY", "SCALED"])
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)

  if options.mode:
    options.mode = getattr(db.FileMode, options.mode)
    
  if options.path:
    if not os.path.exists(options.path):
      print "Could not find",options.path,"for importing"
      sys.exit(1)
    if os.path.isdir(options.path):
      print "Importing directory",options.path
      import_directory(options.path, options.mode)
    else:
      print "Importing file", options.path
      import_file(options.path, options.mode)
    
    sys.exit(0)
      
  print parser.format_help()
  sys.exit(0)
  
def import_file(path,mode):

  st = os.stat(path)
  
  stats = []
  stats.append(('size',st.st_size))
  stats.append(('mtime',st.st_mtime))
  stats.append(('mode',mode))

  list = db.add(path)
  if list is not None and len(list) is 1:
    f = list[0]
    print "{:<4} {}".format(f.id, f.path)
    
    for s in stats:
      db.set(f.path,s[0],s[1],id=f.id)
    
  else:
    print "ERROR importing",path

def import_directory(path,mode):

  for root,dirs,files in os.walk(path):
    for f in files:
      if f.startswith("."):
        continue
      
      p = os.path.join(root,f)
      import_file(p, mode)
    