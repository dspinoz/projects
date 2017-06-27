#!/usr/bin/env python
import sqlite3
import json

import init as lwdb

def add(file, event):
  
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('INSERT INTO queue(file_id,json) VALUES (?,?)',(file,json.dumps(event),))
    conn.commit()
    
    curr.execute('SELECT last_insert_rowid()')
    
    id = curr.fetchone()
      
    conn.close()
    return id[0]
  except sqlite3.Error as e:
    print('queue::add',e)
    return None


def list(file=None,complete=None,limit=None,curr=None):
  data = []
  #try:
  mycurr = False
  if curr is None:
    conn = lwdb.init()
    curr = conn.cursor()
    mycurr = True
 
  if file is not None: 
    if limit is not None: 
      curr.execute('SELECT rowid,json FROM queue WHERE file_id = ? LIMIT ?', (file,limit,))
    else:
      curr.execute('SELECT rowid,json FROM queue WHERE file_id = ?', (file,))
  elif complete is not None: 
    if limit is not None: 
      curr.execute('SELECT rowid,json FROM queue WHERE complete = ? LIMIT ?', (complete,limit,))
    else:
      curr.execute('SELECT rowid,json FROM queue WHERE complete = ?', (complete,))
  else:
    if limit is not None: 
      curr.execute('SELECT rowid,json FROM queue LIMIT ?',(limit,))
    else:
      curr.execute('SELECT rowid,json FROM queue')

  config_data = curr.fetchall()
  for d in config_data:
      data.append((d[0],json.loads(d[1])))
  
  if mycurr:
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

def complete(id,curr=None):
  print "comp {}".format(id)
  try:
    mycurr = False
    if curr is None:
      conn = lwdb.init()
      curr = conn.cursor()
      mycurr = True
    
    curr.execute('UPDATE queue SET complete = 1 WHERE rowid IN (?)',[id])
    
    if mycurr:
      conn.commit()
      conn.close()
    return True
  except sqlite3.Error as e:
    print('queue::complete',e)
    return False

def pop():
  conn = lwdb.init()
  conn.isolation_level = None

  curr = conn.cursor()

  i = None

  try:
    curr.execute("BEGIN")

    l = list(curr=curr,complete=0,limit=1)
    i = l[0]
    complete(i[0], curr=curr)

    curr.execute("COMMIT")
    
  except sqlite3.Error:
    curr.execute("ROLLBACK")

  conn.close()
  return i

