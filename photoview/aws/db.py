import sqlite3
import os

def init(data_dir,db_name):

  path = os.path.join(data_dir,db_name)

  conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
  
  c = conn.cursor()

  c.execute('''
            CREATE TABLE IF NOT EXISTS config (
              key TEXT PRIMARY KEY NOT NULL, 
              value TEXT)''')
  
  conn.commit()
  
  return conn

