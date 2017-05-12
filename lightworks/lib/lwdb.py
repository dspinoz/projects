#!/usr/bin/env python
import sqlite3

def init():
  conn = sqlite3.connect('lw.db', detect_types=sqlite3.PARSE_DECLTYPES)
  
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
