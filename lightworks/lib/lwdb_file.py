#!/usr/bin/env python
import sqlite3

import lwdb

def add(path):
  
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('INSERT INTO file (path) VALUES (?)', (path,))
      
    conn.commit()
    conn.close()
    return True
  except sqlite3.Error as e:
    print('file::add',e)
    return False

def list(filter=None):
  data = []
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    if filter is None:
      curr.execute('SELECT path FROM file')
    else:
      curr.execute('SELECT path FROM file WHERE path LIKE ?', (filter,))
      
    file_data = curr.fetchall()
    for d in file_data:
        data.append((d))
    
    conn.close()
  except sqlite3.Error as e:
    print('file::list()',e)
  return data
