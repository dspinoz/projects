import os
import sys
import optparse
import shutil

import lib.util as u
import lib.lwf as lwf
import lib.lwfexcept as lwfexcept
import lib.db.config as cfg
import lib.db.file as fdb
import lib.db.project_file as pdb


class ProjectFileDoesNotHaveModeError(Exception):
  def __init__(self,mode,path):
    Exception.__init__(self)
    self.mode = mode
    self.path = path
  def __str__(self):
    return Exception.__str__(self) + str(self.mode) + " " + str(self.path)
    
class ProjectFileDifferentError(Exception):
  def __init__(self,path,description):
    Exception.__init__(self)
    self.path = path
    self.description = description
  def __str__(self):
    return Exception.__str__(self) + " " + str(self.path) + " " + str(self.description)
    
class ProjectFileNotFoundError(Exception):
  def __init__(self,path):
    Exception.__init__(self)
    self.path = path
  def __str__(self):
    return Exception.__str__(self) + " " + str(self.path)
    
class FileNotFoundError(Exception):
  def __init__(self,path,mode=None):
    Exception.__init__(self)
    self.mode = mode
    self.path = path
  def __str__(self):
    return Exception.__str__(self) + str(self.mode) + " " + str(self.path)
    

class LWFFile:
  def __init__(self,project_file):
    self.p = project_file

  def src_path(self,mode,modestr): 
    copyfile = u.str2bool(cfg.get("{}copy".format(modestr))[1])
    datadir = os.path.join(lwf.data_dir(),cfg.get("{}dir".format(modestr))[1])

    f = self.p.get(mode)
    
    if f is None:
      raise ProjectFileDoesNotHaveModeError(self.p.path,mode)
    
    rpath = u.strip_path_components(f.path,safe_root=True)
    fpath = os.sep.join([datadir,rpath])
    
    if not copyfile:
      if not os.path.exists(f.path):
        raise FileNotFoundError(f.path,mode)
        
      else:
        fpath = f.path
    else:
      if not os.path.exists(fpath):
        raise FileNotFoundError(f.path,mode)
      else:
        fpath = fpath

    return fpath

  def dst_path(self):

    savepath = os.path.join(os.path.dirname(lwf.data_dir()), self.p.path)
    u.eprint ("savepath full {}".format(savepath))
    savepath = os.path.relpath(savepath)
    u.eprint ("savepath rel {}".format(savepath))
    savepath = os.path.realpath(savepath)
    u.eprint ("savepath real {}".format(savepath))
    return savepath
    
  def check_already_set(self,mode,modestr):
    
    if not os.path.exists(self.p.path):
      return
      
    u.eprint ("project file already exists {}".format(self.p.path))
    
    src = self.p.get(mode)
    
    if src is None:
      raise ProjectFileDoesNotHaveModeError(self.p.path,mode)
    
    
    if self.p.mode == mode:
      u.eprint ("mode is already set, exists, verifying... {}".format(self.p.path))
      
      self.verify(src.path,self.p.path)
      
    else:
      print "what is the file, another mode? safely remove?",self.p.path
        
  def verify(self,src,dst):
    
    if not os.path.exists(dst):
      raise ProjectFileNotFoundError(dst)
      
    if not os.path.exists(src):
      raise FileNotFoundError(src)
      
    sst = os.stat(dst)
    fst = os.stat(src)

    if sst.st_size != fst.st_size:
      raise ProjectFileDifferentError(dst, "size")

    if sst.st_mtime != fst.st_mtime:
      raise ProjectFileDifferentError(dst, "mtime")
    
    print "{}".format(dst),"verified"

  def set(self,mode):
    
    if mode == fdb.FileMode.PROXY:
      modestr = "proxy"
    else:
      raise lwfexcept.UnsupportedFileModeError
    
    p = self.p
    
    
    self.check_already_set(mode,modestr)
    
      
    u.eprint ("reset {} to nothing".format(p.path))
    p.set_mode(None)
    

    src = self.src_path(mode,modestr)
    dst = self.dst_path()

    if os.path.exists(dst):
      self.verify(src,dst)
    
    print "copying",src,dst
    if not os.path.exists(os.path.dirname(dst)):
      os.makedirs(os.path.dirname(dst))
    
    shutil.copy2(src,dst)
    p.set_mode(mode)

  
