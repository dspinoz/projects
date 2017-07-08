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

class WeirdError(Exception):
  def __init__(self,description):
    Exception.__init__(self)
    self.description = description
  def __str__(self):
    return Exception.__str__(self) + " " + str(self.description)

class ProjectFileDoesNotHaveModeError(Exception):
  def __init__(self,path,mode):
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

  def src_path(self,mode): 
    # todo support more modes
    if mode == fdb.FileMode.PROXY:
      modestr = "proxy"
    elif mode == fdb.FileMode.INTERMEDIATE:
      modestr = "intermediate"
    else:
      raise lwfexcept.UnsupportedFileModeError

    copyfile = u.str2bool(cfg.get("{}copy".format(modestr))[1])
    datadir = os.path.join(lwf.data_dir(),cfg.get("{}dir".format(modestr))[1])

    f = self.p.get(mode)
    
    if f is None:
      raise ProjectFileDoesNotHaveModeError(self.p.path,mode)
    
    rpath = u.strip_path_components(f.path,safe_root=True)
    fpath = os.sep.join([datadir,rpath])
    
    if not copyfile:
      u.eprint("get src {}, orig path".format(f.path))
      if not os.path.exists(f.path):
        raise FileNotFoundError(f.path,mode)
        
      else:
        fpath = f.path
    else:
      u.eprint("get src {}, copy path".format(fpath))
      if not os.path.exists(fpath):
        raise FileNotFoundError(fpath,mode)
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
    
  def check_already_set(self,mode):
    
    if not os.path.exists(self.p.path):
      return False
      
    u.eprint ("project file already exists {} {}".format(self.p.mode, self.p.path))
    
    if self.p.mode == mode:
      try:
        # todo support more modes
        src = self.src_path(self.p.mode)
        dst = self.dst_path()
        
        self.verify(self.p.mode, src, dst)
        # tick 2714
        # cross 2715
        #print  u'\u2714',os.path.relpath(dst)
        print  "y",os.path.relpath(dst)
        return True
      except Exception as e:
        raise e
    
  def cleanup_existing(self):
    
    if not os.path.exists(self.p.path):
      return
    
    if self.p.mode is None:
      raise WeirdError("Project file {} exists, but mode not set".format(self.p.path))
      
    
    f = self.p.get(self.p.mode)
    
    if f is None:
      raise WeirdError("Project is set to mode {}, but does not have the file info".format(self.p.mode))
    
    try:
      
      src = self.src_path(self.p.mode)
      dst = self.dst_path()
      
      self.verify(self.p.mode,src,self.p.path)
      
      print self.p.path,"verified as mode",self.p.mode,"safely remove"
      shutil.move(self.p.path, self.p.path+".deleted")
      self.p.set_mode(None)
      
    except Exception as e:
      raise e
    
        
  def verify(self,mode,src,dst):
    
    if not os.path.exists(dst):
      raise ProjectFileNotFoundError(dst)
      
    if not os.path.exists(src):
      raise FileNotFoundError(src,mode)
      
    sst = os.stat(dst)
    fst = os.stat(src)

    if sst.st_size != fst.st_size:
      raise ProjectFileDifferentError(dst, "size")

    if sst.st_mtime != fst.st_mtime:
      raise ProjectFileDifferentError(dst, "mtime")
    
    u.eprint("{} verified for {}".format(dst,mode))

  def set(self,mode):
    
    if self.check_already_set(mode):
      return
      
    self.cleanup_existing()
    
    
    src = self.src_path(mode)
    dst = self.dst_path()
    
    #print u'\u2714',"copying",mode,"files from",src,"to",dst
    print "y","copying",mode,"files from",src,"to",dst
    if not os.path.exists(os.path.dirname(dst)):
      os.makedirs(os.path.dirname(dst))
    
    shutil.copy2(src,dst)
    self.p.set_mode(mode)

  
