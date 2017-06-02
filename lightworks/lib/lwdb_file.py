#!/usr/bin/env python
import sys
import sqlite3
from collections import namedtuple 

import lwdb
import lwdb_queue as qdb

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
  
  def get(self,key):
    try:
      return self.metadata[key]
    except KeyError:
      f = get("",key,self.id)[0][1]
      self.set(key,f)
      return self.metadata[key]

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
 
    # TODO query for id
    for q in qdb.list():
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
  
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('INSERT INTO file (path) VALUES (?)', (path,))
    conn.commit()
    
    curr.execute('SELECT last_insert_rowid()')
    
    id = curr.fetchone()
    f = list(id=id[0])
    
    conn.close()
    return f
  except sqlite3.Error as e:
    print('file::add',path,e)
    return None

def list_by_mode(mode=0):
  data = []
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('''
      SELECT file_id, path
      FROM file,file_metadata
      WHERE file.rowid == file_metadata.file_id
            AND key == 'mode' AND CAST(value as INTEGER) = ?
      ORDER BY CAST(value as INTEGER) DESC
    ''', (mode,))
      
    file_data = curr.fetchall()
    for d in file_data:
      f = File(d[0], d[1])
      f.get_all_props(curr)
      data.append(f)
    
    conn.close()
  except sqlite3.Error as e:
    print('file::list()',filter,e)
  return data
    
def list_by_size():
  data = []
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('''
      SELECT file_id, path
      FROM file,file_metadata
      WHERE file.rowid == file_metadata.file_id
            AND key == 'size'
      ORDER BY CAST(value as INTEGER) DESC
    ''')
      
    file_data = curr.fetchall()
    for d in file_data:
      f = File(d[0], d[1])
      f.get_all_props(curr)
      data.append(f)
    
    conn.close()
  except sqlite3.Error as e:
    print('file::list()',filter,e)
  return data
    
def list_by_mtime():
  data = []
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('''
      SELECT file_id, path
      FROM file,file_metadata
      WHERE file.rowid == file_metadata.file_id
            AND key == 'mtime'
      ORDER BY CAST(value as INTEGER) DESC
    ''')
      
    file_data = curr.fetchall()
    for d in file_data:
      f = File(d[0], d[1])
      f.get_all_props(curr)
      data.append(f)
    
    conn.close()
  except sqlite3.Error as e:
    print('file::list()',filter,e)
  return data
    
def list(filter=None,id=None):
  data = []
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    if filter is None and id is None:
      curr.execute('SELECT rowid, path FROM file')
    elif filter is not None:
      curr.execute('SELECT rowid, path FROM file WHERE path LIKE ?', (filter,))
    elif id is not None:
      curr.execute('SELECT rowid, path FROM file WHERE rowid = ?', (id,))
      
    file_data = curr.fetchall()
    for d in file_data:
      f = File(d[0], d[1])
      f.get_all_props(curr)
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
      curr.execute('SELECT rowid, path FROM file WHERE rowid = ?', (id,))
    else:
      curr.execute('SELECT rowid, path FROM file WHERE path = ?', (path,))
      
    file_data = curr.fetchone()
    
    if file_data is None:
      conn.close()
      if id is not None:
        print "No file with id",id
      else:
        print "No file at path",path
      sys.exit(1)
    
    f = File(file_data[0], file_data[1])
    
    if key is None:
      curr.execute("SELECT key,value FROM file_metadata WHERE file_id = ?", (f.id,))
    else:
      curr.execute("SELECT key,value FROM file_metadata WHERE file_id = ? AND key = ?", (f.id,key))
    
    file_metadata = curr.fetchall()
    for d in file_metadata:
      data.append((d[0], d[1]))
      f.set(d[0], d[1])
    
    conn.close()
    
    return data
  except sqlite3.Error as e:
    print('file::get()',path,key,e)
  return data
  
  
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
