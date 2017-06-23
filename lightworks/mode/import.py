import os
import sys
import shutil
import optparse

import lib.lwf as lwf
import lib.lwfexcept
import lib.util as util
import lib.add as add
import lib.db.config as cfg
import lib.db.file as fdb
import lib.db.project_file as pfdb
import lib.db.queue as qdb


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
  parser.add_option("-a", "--as", dest="project_path", default=None, help="Path to project file")
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

    try:
      if os.path.isdir(options.path):
        print "Importing directory",options.path
        add.import_directory(options.path, options.mode, options.transcode)
      else:
        print "Importing file", options.path
        add.import_file(os.path.dirname(options.path), True, options.path, options.mode, options.transcode,options.project_path)
    except lib.lwfexcept.FileInfoError:
      print "Could not generate file info",options.path
      sys.exit(1)
    except lib.lwfexcept.FileFFMPEGError:
      print "Could not transcode with ffmpeg",options.path
      sys.exit(2)
    
    sys.exit(0)
      
  print parser.format_help()
  sys.exit(0)
  
