#!/usr/bin/env python
import sys
import sqlite3
from collections import namedtuple 

import lwdb
import lwdb_file as dbfile

class ProjectFile:
  def __init__(self,id,path):
    self.id = id
    self.path = path
    self.files = {}
  
  def __str__(self):
    s =  "#" + str(self.id) + " " + self.path + " (" + str(len(self.files)) + ")\n"
    for m in self.files:
      f = self.files[m]
      s += " " + str(m) + ": #" + str(f.id) + " " + f.path + "\n"
    return s
    
  def set(self,file):
    
    add_file(self.id, file.id)
    self.files[file.get("mode")] = file
    
  def fetch(self):
    
    files = get_files(self)
    
    for f in files:
      try:
        if self.files[f.get("mode")] is not None:
          e = self.files[f.get("mode")]
          print "already has mode "+str(f.get("mode"))+" #"+ str(e.id) +" new is #"+str(f.id)
      except KeyError:
        # no file in map yet, all ok
        pass
      self.files[f.get("mode")] = f


def add(path):
  
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('INSERT INTO project_file (path) VALUES (?)', (path,))
    conn.commit()
    
    curr.execute('SELECT last_insert_rowid()')
    
    id = curr.fetchone()
    f = ProjectFile(id[0],path)
    
    conn.close()
    return f
  except sqlite3.Error as e:
    print('file::add',path,e)
    return None

def add_file(projectid,fileid):
  
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('INSERT INTO project_file_ref (project_file_id,file_id) VALUES (?,?)', (projectid,fileid,))
    conn.commit()
    
    conn.close()
    return True
  except sqlite3.Error as e:
    print('file::add',path,e)
    return None
    
def list(filter=None,id=None):
  data = []
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    if filter is None and id is None:
      curr.execute('SELECT rowid, path FROM project_file')
    elif filter is not None:
      curr.execute('SELECT rowid, path FROM project_file WHERE path LIKE ?', (filter,))
    elif id is not None:
      curr.execute('SELECT rowid, path FROM project_file WHERE rowid = ?', (id,))
      
    file_data = curr.fetchall()
    for d in file_data:
      f = ProjectFile(d[0], d[1])
      data.append(f)
    
    conn.close()
  except sqlite3.Error as e:
    print('file::list()',filter,e)
  return data
  
def get(path,key=None,id=None):
  data = []
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    if id is not None:
      curr.execute('SELECT rowid, path FROM project_file WHERE rowid = ?', (id,))
    else:
      curr.execute('SELECT rowid, path FROM project_file WHERE path = ?', (path,))
      
    file_data = curr.fetchall()
    for d in file_data:
      f = ProjectFile(d[0], d[1])
      data.append(f)
    
    conn.close()
    
    return data
  except sqlite3.Error as e:
    print('file::get()',path,key,e)
  return data
  
def get_files(pf):
  data = []
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('SELECT file_id FROM project_file_ref WHERE project_file_id = ?', (pf.id,))
      
    file_data = curr.fetchall()
    for d in file_data:
      f = dbfile.get(None,id=d[0],wantf=True)
      data.append(f)
    
    conn.close()
    
    return data
  except sqlite3.Error as e:
    print('file::get_files()',pf,e)
  return data
