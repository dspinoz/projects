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

class LWFFile:
  def __init__(self,mode):
    if mode == fdb.FileMode.PROXY:
      self.mode = fdb.FileMode.PROXY
      self.modestr = "proxy"
    else:
      raise lwfexcept.UnsupportedFileModeError
    
  def set(self):
 
    list = []

    try:
      list = pdb.list()
    except lwfexcept.ProjectFileNotFoundError:
      pass

    for p in list:
      p.fetch()

      f = p.get(self.mode)

      if os.path.exists(p.path):
        print "remove existing file, mode",p.mode,"path",p.path
        # todo unlink if safe
        
      p.set_mode(None)

      if f is None:
        print p.path,"????"
        continue

      print p.path,f.path

      copyfile = u.str2bool(cfg.get("{}copy".format(self.modestr))[1])
      datadir = os.path.join(lwf.data_dir(),cfg.get("{}dir".format(self.modestr))[1])

      rpath = u.strip_path_components(f.path,safe_root=True)
      fpath = os.sep.join([datadir,rpath])
      
      if not copyfile:
        if not os.path.exists(f.path):
          print "File has gone! No copy available"
          continue
        else:
          fpath = f.path
      else:
        if not os.path.exists(fpath):
          print "File copy has gone!"
          continue
        else:
          fpath = fpath


      savepath = os.path.join(os.path.dirname(lwf.data_dir()), p.path)
      u.eprint ("savepath full {}".format(savepath))
      savepath = os.path.relpath(savepath)
      u.eprint ("savepath rel {}".format(savepath))
      savepath = os.path.realpath(savepath)
      u.eprint ("savepath real {}".format(savepath))

      if os.path.exists(savepath):
        sst = os.stat(savepath)
        fst = os.stat(fpath)

        if sst.st_size != fst.st_size:
          print "not the {} file, size diff!".format(self.modestr)
          continue

        if sst.st_mtime != fst.st_mtime:
          print "not the {} file, mtime diff!".format(self.modestr)
          continue

        if os.path.exists(savepath):
          print "{}".format(self.modestr),savepath,"already here"
          continue
      
      print "copying",fpath,savepath
      if not os.path.exists(os.path.dirname(savepath)):
        os.makedirs(os.path.dirname(savepath))
      
      shutil.copy2(fpath,savepath)
      p.set_mode(self.mode)

  
