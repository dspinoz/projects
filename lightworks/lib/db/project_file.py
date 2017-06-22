#!/usr/bin/env python
import sys
import sqlite3
from collections import namedtuple 

import init as lwdb
import file as dbfile
from .. import lwfexcept
from .. import util as u

class ProjectFile:
  def __init__(self,id,path):
    self.id = id
    self.path = path
    self.files = {}
  
  def __str__(self):
    
    s = "P#{:<4} {} ({})\n".format(self.id, self.path, len(self.files))
    for m in self.files:
      f = self.files[m]
      s += "  {}: {}\n".format(m, f)
    return s
    
  def set(self,file):
    
    add_file(self.id, file.id, file.get("mode"))
    self.files[file.get("mode")] = file

  def get(self,mode):
    try:
      return self.files[mode]
    except KeyError:
      return None
    
  def fetch(self):
    
    files = get_files(self)
    
    for f in files:
      try:
        if self.files[f.get("mode")] is not None and self.files[f.get("mode")].id != f.id:
          e = self.files[f.get("mode")]
          print "already has mode "+str(f.get("mode"))+" #"+ str(e.id) +" new is #"+str(f.id)
      except KeyError:
        # no file in map yet, all ok
        pass
      self.files[f.get("mode")] = f


def add(path):

  conn = lwdb.init()
  curr = conn.cursor()
  try:
    
    curr.execute('INSERT INTO project_file (path) VALUES (?)', (path,))
    conn.commit()
    
    curr.execute('SELECT last_insert_rowid()')
    
    id = curr.fetchone()
    f = ProjectFile(id[0],path)
    
    conn.close()
    return f
  except sqlite3.IntegrityError as e:
    conn.close()
    raise lwfexcept.ProjectFileAlreadyExistsError(path)
  except sqlite3.Error as e:
    conn.close()
    raise e

def add_file(projectid,fileid,fileid_mode):
  
  u.eprint("PF {} add file {} {}".format(projectid,fileid_mode,fileid))
  
  conn = lwdb.init()
  curr = conn.cursor()
  try:
    
    curr.execute('INSERT INTO project_file_ref (project_file_id,file_id,mode) VALUES (?,?,?)', (projectid,fileid,fileid_mode))
    conn.commit()
    
    conn.close()
    return True
  except sqlite3.IntegrityError as e:
    conn.close()
    raise lwfexcept.ProjectFileModeAlreadyTakenError()
  except sqlite3.Error as e:
    conn.close()
    raise e
    
def list(filter=None,id=None,path=None):
  conn = lwdb.init()
  curr = conn.cursor()
  try:
    
    if filter is None and id is None and path is None:
      curr.execute('SELECT rowid, path FROM project_file')
    elif filter is not None and id is None and path is None:
      curr.execute('SELECT rowid, path FROM project_file WHERE path LIKE ?', (filter,))
    elif path is not None and id is None:
      curr.execute('SELECT rowid, path FROM project_file WHERE path = ?', (path,))
    elif id is not None:
      curr.execute('SELECT rowid, path FROM project_file WHERE rowid = ?', (id,))
      
    file_data = curr.fetchall()
    
    if len(file_data) is 0:
      raise lwfexcept.ProjectFileNotFoundError(None)
    
    data = []
    for d in file_data:
      f = ProjectFile(d[0], d[1])
      data.append(f)
    
    conn.close()
    return data
  except sqlite3.Error as e:
    conn.close()
    raise e
  
def get(path=None,id=None):
  if path is None and id is None:
    raise lwfexcept.ProjectFileNotFoundError(None)
  
  coll = list(path=path,id=id)
  
  if len(coll) is 1:
    return coll[0]
  raise lwfexcept.ProjectFileNotFoundError(path)
	
  
def get_files(pf):
  data = []
  conn = lwdb.init()
  curr = conn.cursor()
  try:
    
    curr.execute('SELECT file_id FROM project_file_ref WHERE project_file_id = ?', (pf.id,))
      
    file_data = curr.fetchall()
    for d in file_data:
      f = dbfile.get(id=d[0])
      data.append(f)
    
    conn.close()
    
    return data
  except sqlite3.Error as e:
    conn.close()
    raise e

def find(fileid):
  data = []
  conn = lwdb.init()
  curr = conn.cursor()
  try:
    
    curr.execute('SELECT project_file_id FROM project_file_ref WHERE file_id = ?', (fileid,))
      
    file_data = curr.fetchall()
    for d in file_data:
      f = get(id=d[0])
      data.append(f)
    
    conn.close()
    
    if len(data) is 0:
      raise lwfexcept.ProjectFileNotFoundError(fileid)

    return data
  except sqlite3.Error as e:
    conn.close()
    raise e
