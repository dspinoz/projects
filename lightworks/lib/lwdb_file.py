#!/usr/bin/env python
import sys
import sqlite3

import lwdb

class File:
  def __init__(self,id,path):
    self.id = id
    self.path = path
    self.metadata = {}
    
  def set(self, key, value):
    self.metadata[key] = value

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
        data.append(File(d[0], d[1]))
    
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
    
    conn.close()
    
    return data
  except sqlite3.Error as e:
    print('file::get()',path,key,e)
  return data
  
  
def set(path,key,value):
  data = []
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('SELECT rowid, path FROM file WHERE path = ?', (path,))
      
    file_data = curr.fetchone()
    
    f = File(file_data[0], file_data[1])
    
    try:
      curr.execute('INSERT INTO file_metadata (file_id,key,value) VALUES (?,?,?)',(f.id,key,value))
    except sqlite3.IntegrityError:
      curr.execute('UPDATE file_metadata SET value = ? WHERE file_id = ? AND key = ?',(value,f.id,key))
    
    conn.commit()
    conn.close()
    
    return True
  except sqlite3.Error as e:
    print('file::set()',path,key,value,e)
  return False