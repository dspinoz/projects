#!/usr/bin/env python
import sqlite3

def set(key=None,value=None):
  
  try:
    conn = sqlite3.connect('lw.db', detect_types=sqlite3.PARSE_DECLTYPES)
    curr = conn.cursor()
    
    try:
      curr.execute('INSERT INTO config VALUES (?,?)',(key,value))
    except sqlite3.IntegrityError:
      curr.execute('UPDATE config SET value = ? WHERE key = ?',(value,key))
      
    conn.commit()
    conn.close()
    return True
  except sqlite3.Error as e:
    print('config::set',e)
    return False

def get(key=None):
  ret = (None,None)
  try:
    conn = sqlite3.connect('lw.db', detect_types=sqlite3.PARSE_DECLTYPES)
    curr = conn.cursor()
    
    curr.execute('SELECT * FROM config WHERE key IN (?)', [(key)])
    data = curr.fetchone()

    if data is not None:
      ret = data
    
    conn.close()
  except sqlite3.Error as e:
    print('config::get()',e)
  return ret

def list():
  data = []
  try:
    conn = sqlite3.connect('lw.db', detect_types=sqlite3.PARSE_DECLTYPES)
    curr = conn.cursor()
    
    curr.execute('SELECT * FROM config')
    config_data = curr.fetchall()
    for d in config_data:
        data.append((d[0], d[1]))
    
    conn.close()
  except sqlite3.Error as e:
    print('config::list()',e)
  return data
