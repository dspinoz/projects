import os
import sys
import shutil
import optparse

import lib.lwf as lwf
import lib.lwfexcept
import lib.util as u
import lib.db.config as cfg
import lib.db.file as fdb
import lib.db.project_file as pfdb
import lib.db.queue as qdb


def import_file(root,userel,path,mode,transcode,project_path=None,recursive=False):

  st = os.stat(path)
  
  root = os.path.realpath(root)
  path = os.path.realpath(path)
  
  if project_path is None:
    if userel:
      project_path = os.path.relpath(path,root)
    else:
      project_path = u.strip_path_components(path,safe_root=True)
      project_path = os.sep.join([os.curdir, project_path])
      project_path = os.path.relpath(project_path,os.curdir)
  
  u.eprint("import {} as {} {}".format(path,mode,project_path))
  
  pf = None
  try:
    pf = pfdb.add(project_path)
  except lib.lwfexcept.ProjectFileAlreadyExistsError:
    pf = pfdb.get(path=project_path)

  cfgdir = "rawdir"
  copyfile = "rawcopy"
  if mode == fdb.FileMode.RAW:
    cfgdir = "rawdir"
    copyfile = "rawcopy"
  if mode == fdb.FileMode.INTERMEDIATE:
    cfgdir = "intermediatedir"
    copyfile = "intermediatecopy"
  if mode == fdb.FileMode.PROXY:
    cfgdir = "proxydir"
    copyfile = "proxycopy"

  copyfile = u.str2bool(cfg.get(copyfile)[1])
  
  datadir = os.path.join(lwf.data_dir(),cfg.get(cfgdir)[1])
  rpath = u.strip_path_components(path,safe_root=True)
  fpath = os.sep.join([datadir,rpath])
  
  stats = []
  stats.append(('size',st.st_size))
  stats.append(('mtime',st.st_mtime))
  stats.append(('mode',mode))

  added = None
  
  try:
    added = fdb.add(path)
    u.eprint("new file {}".format(added))
  except lib.lwfexcept.FileAlreadyImportedError:
    added = fdb.get(path=path)
    u.eprint("ref existing file {}".format(added))

  if not recursive:
    if os.path.exists(path + ".int"):
      import_file(root,userel,path+".int",fdb.FileMode.INTERMEDIATE,False,project_path,True)
    if os.path.exists(path + ".pxy"):
      import_file(root,userel,path+".pxy",fdb.FileMode.PROXY,False,project_path,True)
  
  pf.fetch()
  save(pf,added,stats,fpath,transcode,copyfile)

  pf.set(added)

  pf.fetch()
  
  print pf

def save(pf,f,stats,savepath,transcode,copy):
  u.eprint("save {}".format(f))
  
  for s in stats:
    fdb.set(path="",id=f.id,key=s[0],value=s[1])
    f.set(key=s[0],value=s[1])

  if copy:
    if not os.path.exists(os.path.dirname(savepath)):
      os.makedirs(os.path.dirname(savepath))

    shutil.copy2(f.path,savepath)
  
  if transcode:
    jobs = []
    if f.get("mode") == fdb.FileMode.RAW:
      if pf.get(fdb.FileMode.INTERMEDIATE) is None:
        jobs.append({'type':'transcode', 'file': f.id, 'from': fdb.FileMode.RAW, 'to': fdb.FileMode.INTERMEDIATE})
      if pf.get(fdb.FileMode.PROXY) is None:
        jobs.append({'type':'transcode', 'file': f.id, 'from': fdb.FileMode.INTERMEDIATE, 'to': fdb.FileMode.PROXY})
    elif f.get("mode") == fdb.FileMode.INTERMEDIATE:
      cfgdir = "intermediatedir"
      if pf.get(fdb.FileMode.PROXY) is None:
        jobs.append({'type':'transcode', 'file': f.id, 'from': fdb.FileMode.INTERMEDIATE, 'to': fdb.FileMode.PROXY})
    elif f.get("mode") == fdb.FileMode.PROXY:
      cfgdir = "proxydir"
  
    for j in jobs:
      qdb.add(f.id, j)

def import_directory(path,mode,transcode):

  for root,dirs,files in os.walk(path):
    for f in files:
      if f.startswith("."):
        continue
      
      p = os.path.join(root,f)
      
      import_file(root, True, p, mode, transcode, os.path.relpath(p,path))
    
