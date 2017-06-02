import os
import sys
import shutil
import optparse

import lib.lwf as lwf
import lib.util as util
import lib.lwdb_config as cfg
import lib.lwdb_file as fdb
import lib.lwdb_queue as qdb

desc="""
Import mode.

All files are imported into a Lightworks Workflow.

The following metadata fields are available:
  
  size      number of bytes contained in the file
  mtime     last time file was modified
  mode      RAW, INTERMEDIATE, PROXY

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('-h', "--help", dest="help", action="store_true", help="Show import options")
  parser.add_option("-p", "--path", dest="path", help="Path to files to import")
  parser.add_option("-m", "--mode", dest="mode", help="Current mode of files to import [default: %default]", default="RAW", choices=["RAW", "INTERMEDIATE", "PROXY"])
  parser.add_option('-T', "--no-transcode", dest="transcode", action="store_false", default=True, help="Disable auto transcoding of intermediate +/ proxy files")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)

  if options.mode:
    options.mode = getattr(fdb.FileMode, options.mode)
    
  if options.path:
    if not os.path.exists(options.path):
      print "Could not find",options.path,"for importing"
      sys.exit(1)
    if os.path.isdir(options.path):
      print "Importing directory",options.path
      import_directory(options.path, options.mode, options.transcode)
    else:
      print "Importing file", options.path
      import_file(options.path, options.mode, options.transcode)
    
    sys.exit(0)
      
  print parser.format_help()
  sys.exit(0)
  
def import_file(path,mode,transcode):

  st = os.stat(path)
  
  path = os.path.realpath(path)
  
  cfgdir = "rawdir"
  if mode == fdb.FileMode.RAW:
    cfgdir = "rawdir"
  if mode == fdb.FileMode.INTERMEDIATE:
    cfgdir = "intermediatedir"
  if mode == fdb.FileMode.PROXY:
    cfgdir = "proxydir"
  
  datadir = os.path.join(lwf.data_dir(),cfg.get(cfgdir)[1])
  rpath = util.strip_path_components(path,safe_root=True)
  fpath = os.sep.join([datadir,rpath])
  
  stats = []
  stats.append(('size',st.st_size))
  stats.append(('mtime',st.st_mtime))
  stats.append(('mode',mode))

  list = fdb.add(path)

  if list is not None and len(list) is 1:
    f = list[0]
    print "{:<4} {}".format(f.id, f.path)
    
    for s in stats:
      fdb.set(f.path,s[0],s[1],id=f.id)

    if not os.path.exists(os.path.dirname(fpath)):
      os.makedirs(os.path.dirname(fpath))

    shutil.copy2(path,fpath)
    if transcode:
      jobs = []
      if mode == fdb.FileMode.RAW:
        jobs.append({'type':'transcode', 'file': f.id, 'from': fdb.FileMode.RAW, 'to': fdb.FileMode.INTERMEDIATE})
        jobs.append({'type':'transcode', 'file': f.id, 'from': fdb.FileMode.INTERMEDIATE, 'to': fdb.FileMode.PROXY})
      elif mode == fdb.FileMode.INTERMEDIATE:
        cfgdir = "intermediatedir"
        jobs.append({'type':'transcode', 'file': f.id, 'from': fdb.FileMode.INTERMEDIATE, 'to': fdb.FileMode.PROXY})
      elif mode == fdb.FileMode.PROXY:
        cfgdir = "proxydir"
    
      for j in jobs:
        qdb.add(j)    
  else:
    print "ERROR importing",path

def import_directory(path,mode,transcode):

  for root,dirs,files in os.walk(path):
    for f in files:
      if f.startswith("."):
        continue
      
      p = os.path.join(root,f)
      import_file(p, mode, transcode)
    
