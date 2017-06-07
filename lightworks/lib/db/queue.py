#!/usr/bin/env python
import sqlite3
import json

import init as lwdb

def add(file, event):
  
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('INSERT INTO queue VALUES (?,?)',(file,json.dumps(event),))
    conn.commit()
    
    curr.execute('SELECT last_insert_rowid()')
    
    id = curr.fetchone()
      
    conn.close()
    return id[0]
  except sqlite3.Error as e:
    print('queue::add',e)
    return None


def list(file=None):
  data = []
  #try:
  conn = lwdb.init()
  curr = conn.cursor()
 
  if file is None: 
    curr.execute('SELECT rowid,json FROM queue')
  else:
    curr.execute('SELECT rowid,json FROM queue WHERE file_id = ?', (file,))

  config_data = curr.fetchall()
  for d in config_data:
      data.append((d[0],json.loads(d[1])))
  
  conn.close()
  #except sqlite3.Error as e:
  #  print('event::list()',e)
  return data

def delete(id):
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('DELETE FROM queue WHERE rowid IN (?)',[id])
    conn.commit()
    
    conn.close()
    return True
  except sqlite3.Error as e:
    print('queue::delete',e)
    return False


