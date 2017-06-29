import os
import sys
import optparse
import shutil

import lib.util as u
import lib.lwf as lwf
import lib.lwf_file as lwf_file
import lib.lwfexcept as lwfexcept
import lib.db.config as cfg
import lib.db.file as fdb
import lib.db.project_file as pdb

desc="""
Switch to proxy files.

"""

def get_parser():
  parser = optparse.OptionParser(add_help_option=False, description=desc, usage=optparse.SUPPRESS_USAGE)
  parser.add_option('', "--help", dest="help", action="store_true", help="Show proxy options")
  parser.add_option("-l", "--list", dest="list_proxy", action="store_true", help="List proxy files")
  return parser
  
def parser_hook(parser,options,args):
  if options.help:
    print parser.format_help()
    sys.exit(0)
 
  list = []

  try:
    list = pdb.list()
  except lwfexcept.ProjectFileNotFoundError:
    pass

  for p in list:
    p.fetch()
    
    err = None
    
    try:
      
      f = lwf_file.LWFFile(p)
      f.set(fdb.FileMode.PROXY)
      
    except lwf_file.ProjectFileDoesNotHaveModeError as e:
      err = "Project File {} does not have {} file available".format(e.path,e.mode)
      
    except lwf_file.ProjectFileNotFoundError as e:
      err = "Project File {} could not be found".format(e.path)
    
    except lwf_file.FileNotFoundError as e:
      err = "Project File {} could not find original file {} {}".format(p.path,e.path,e.mode)
      
    except lwf_file.ProjectFileDifferentError as e:
      err = "Project File {} was different in {}!".format(e.path,e.description)
    
    if err is not None:
      print u'\u2715',err
      
  sys.exit(0)
  
