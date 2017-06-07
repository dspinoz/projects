#!/usr/bin/env python
import sys
import sqlite3
from collections import namedtuple 

import init as lwdb
import queue as qdb
from .. import lwfexcept

FileStatus = namedtuple('FileStatus', 'diff raw intermediate proxy')

class FileMode:
  RAW = 0
  INTERMEDIATE = 1
  PROXY = 2
  

class File:
  def __init__(self,id,path):
    self.id = id
    self.path = path
    self.metadata = {}
    self.status = FileStatus(diff = "-", raw = "-", intermediate = "-", proxy = "-")
  
  def __str__(self):
    return "F#{:<4} {}".format(self.id, self.path)
  
  def get(self,key):
    try:
		
      if key == "mode":
        value = int(self.metadata[key])
        return value
		
      return self.metadata[key]
    except KeyError:
      return None

  def set(self, key, value):
    self.metadata[key] = value
    
    if key == "mode":
      value = int(value)
      if value == FileMode.RAW:
        self.set_raw()
      elif value == FileMode.INTERMEDIATE:
        self.set_intermediate()
      elif value == FileMode.PROXY:
        self.set_proxy()
    
  def status_str(self):
    return "".join([self.status.diff, self.status.raw, self.status.intermediate, self.status.proxy])

  def get_all_props(self,curr):
    curr.execute('''
      SELECT key, value
      FROM file_metadata
      WHERE file_metadata.file_id == ?
    ''', (self.id,))
      
    props = curr.fetchall()
    for p in props:
      self.set(p[0],p[1])
 
    for q in qdb.list(self.id):
      q = q[1]
      if q['type'] == 'transcode' and q['file'] == self.id:
        if q['to'] == FileMode.INTERMEDIATE:
          self.set_intermediate_queued()
        if q['to'] == FileMode.PROXY:
          self.set_proxy_queued()
  
  def set_raw(self):
    self.status = FileStatus(diff = self.status.diff, raw = "R", intermediate = self.status.intermediate, proxy = self.status.proxy)
  
  def set_intermediate(self):
    self.status = FileStatus(diff = self.status.diff, raw = self.status.raw, intermediate = "I", proxy = self.status.proxy)
  
  def set_proxy(self):
    self.status = FileStatus(diff = self.status.diff, raw = self.status.raw, intermediate = self.status.intermediate, proxy = "P")
  
  def set_diff(self):
    self.status = FileStatus(diff = "*", raw = self.status.raw, intermediate = self.status.intermediate, proxy = self.status.proxy)


  def set_intermediate_queued(self):
    self.status = FileStatus(diff = self.status.diff, raw = self.status.raw, intermediate = "+", proxy = self.status.proxy)
  
  def set_proxy_queued(self):
    self.status = FileStatus(diff = self.status.diff, raw = self.status.raw, intermediate = self.status.intermediate, proxy = "+")
 



def add(path):
  conn = lwdb.init()
  curr = conn.cursor()
  try:
    
    curr.execute('INSERT INTO file (path) VALUES (?)', (path,))
    conn.commit()
    
    curr.execute('SELECT last_insert_rowid()')
    
    id = curr.fetchone()
    f = File(id[0],path)
    
    conn.close()
    return f
  except sqlite3.IntegrityError as e:
    conn.close()
    raise lwfexcept.FileAlreadyImportedError(path)
  except sqlite3.Error as e:
    conn.close()
    raise e
    
    
def list_from_metadata(key,filter=None,id=None,path=None):
  conn = lwdb.init()
  curr = conn.cursor()
  try:
    
    if filter is None and id is None and path is None:
      
      curr.execute('''
        SELECT file.rowid, path
        FROM file,file_metadata
        WHERE file.rowid == file_metadata.file_id
              AND key == ?
        ORDER BY CAST(value as INTEGER) DESC
      ''', (key,))
      
    elif filter is not None and id is None and path is None:
      
      curr.execute('''
        SELECT file.rowid, path
        FROM file,file_metadata
        WHERE file.rowid == file_metadata.file_id
              AND key == ?
              AND file.path LIKE ?
        ORDER BY CAST(value as INTEGER) DESC
      ''', (key,filter,))
      
    elif path is not None and id is None:
      
      curr.execute('''
        SELECT file.rowid, path
        FROM file,file_metadata
        WHERE file.rowid == file_metadata.file_id
              AND key == ?
              AND file.path = ?
        ORDER BY CAST(value as INTEGER) DESC
      ''', (key,path,))
      
    elif id is not None:
      curr.execute('''
        SELECT file.rowid, path
        FROM file,file_metadata
        WHERE file.rowid == file_metadata.file_id
              AND key == ?
              AND file.rowid = ?
        ORDER BY CAST(value as INTEGER) DESC
      ''', (key,id,))
      
    file_data = curr.fetchall()
    
    if len(file_data) is 0:
      raise lwfexcept.FileNotFoundError
    
    data = []
    for d in file_data:
      f = File(d[0], d[1])
      f.get_all_props(curr)
      data.append(f)
    
    conn.close()
    return data
  except sqlite3.Error as e:
    conn.close()
    raise e
  
  
def list(filter=None,id=None,path=None):
  conn = lwdb.init()
  curr = conn.cursor()
  try:
    
    if filter is None and id is None and path is None:
      curr.execute('SELECT rowid, path FROM file')
    elif filter is not None and id is None and path is None:
      curr.execute('SELECT rowid, path FROM file WHERE path LIKE ?', (filter,))
    elif path is not None and id is None:
      curr.execute('SELECT rowid, path FROM file WHERE path = ?', (path,))
    elif id is not None:
      curr.execute('SELECT rowid, path FROM file WHERE rowid = ?', (id,))
      
    file_data = curr.fetchall()
    
    if len(file_data) is 0:
      raise lwfexcept.FileNotFoundError
    
    data = []
    for d in file_data:
      f = File(d[0], d[1])
      f.get_all_props(curr)
      data.append(f)
    
    conn.close()
    return data
  except sqlite3.Error as e:
    conn.close()
    raise e
  
def get(path=None,id=None):
  if path is None and id is None:
    raise lwfexcept.FileNotFoundError(None)
  
  coll = list(path=path,id=id)
  
  if len(coll) is 1:
    return coll[0]
  raise lwfexcept.FileNotFoundError(path)
  
  
  
def set(path,key,value,id=None):
  data = []
  try:
    conn = lwdb.init()
    curr = conn.cursor()

    f = None
    
    if id is None:
      curr.execute('SELECT rowid, path FROM file WHERE path = ?', (path,))
        
      file_data = curr.fetchone()
    
      f = File(file_data[0], file_data[1])
      
    else:
      #object is incomplete!
      f = File(id,path) 
    
    try:
      curr.execute('INSERT INTO file_metadata (file_id,key,value) VALUES (?,?,?)',(f.id,key,value))
    except sqlite3.IntegrityError:
      curr.execute('UPDATE file_metadata SET value = ? WHERE file_id = ? AND key = ?',(value,f.id,key))
    
    f.get_all_props(curr)
    
    conn.commit()
    conn.close()
    
    return True
  except sqlite3.Error as e:
    print('file::set()',path,key,value,e)
  return False
