#!/usr/bin/env python
import sqlite3
import os
import lwf

db_name = "lwf.db"

def init():

  path = os.path.join(lwf.data_dir(),db_name)

  conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
  
  c = conn.cursor()

  c.execute('''
            CREATE TABLE IF NOT EXISTS config (
              key TEXT PRIMARY KEY NOT NULL, 
              value TEXT)''')
              
  c.execute('''
            CREATE TABLE IF NOT EXISTS file (
              path TEXT PRIMARY KEY NOT NULL)''')
              
  c.execute('''
            CREATE TABLE IF NOT EXISTS file_metadata (
              file_id INTEGER NOT NULL,
              key TEXT NOT NULL, 
              value TEXT,
              PRIMARY KEY (file_id, key) )''')

  conn.commit()
  
  return conn
