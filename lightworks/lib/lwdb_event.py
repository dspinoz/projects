#!/usr/bin/env python
import sqlite3
import json

import lwdb

def add(event):
  
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('INSERT INTO event VALUES (?)',(json.dumps(event),))
      
    conn.commit()
    conn.close()
    return True
  except sqlite3.Error as e:
    print('event::add',e)
    return False


def list():
  data = []
  try:
    conn = lwdb.init()
    curr = conn.cursor()
    
    curr.execute('SELECT * FROM event')
    config_data = curr.fetchall()
    for d in config_data:
        data.append(json.loads(d[0]))
    
    conn.close()
  except sqlite3.Error as e:
    print('event::list()',e)
  return data
