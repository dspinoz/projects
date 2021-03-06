#!/usr/bin/env python
import sqlite3
import os
from .. import lwf

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
  
  c.execute('''
            CREATE TABLE IF NOT EXISTS event (
              json TEXT NOT NULL)''')

  c.execute('''
            CREATE TABLE IF NOT EXISTS queue (
              file_id INTEGER NOT NULL,
              json TEXT NOT NULL,
              complete INTEGER NOT NULL DEFAULT 0)''')

  c.execute('''
            CREATE TABLE IF NOT EXISTS project_file (
              path TEXT NOT NULL,
              mode INTEGER DEFAULT NULL,
              PRIMARY KEY(path) )''')
              
  c.execute('''
            CREATE TABLE IF NOT EXISTS project_file_ref (
              project_file_id INTEGER NOT NULL,
              file_id INTEGER NOT NULL,
              mode INTEGER NOT NULL,
              PRIMARY KEY(project_file_id,mode) )''')
  
  conn.commit()
  
  return conn
