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

  c.execute('''
            CREATE TABLE IF NOT EXISTS glacier_job (
              id TEXT PRIMARY KEY NOT NULL, 
              account TEXT,
              vault TEXT,
              parameters TEXT,
              description TEXT,
              output TEXT)''')
  
  conn.commit()
  
  return conn


def has_inventory_job(conn):
  try:
    curr = conn.cursor()
    
    curr.execute('select id from glacier_job where parameters LIKE "%inventory-retrieval%" and output = ""')
 
    row = curr.fetchone()
    
    jobid = None
    if row is not None:
      jobid = row[0]
    
    return jobid
  except sqlite3.Error as e:
    print("has_inventory_job: {}".format(e))
    return False

def get_last_inventory_job(conn):
  try:
    curr = conn.cursor()
    
    curr.execute('select id from glacier_job where parameters LIKE "%inventory-retrieval%" and output != "" ORDER BY ID DESC LIMIT 1')
 
    row = curr.fetchone()
    
    jobid = None
    if row is not None:
      jobid = row[0]
    
    return jobid
  except sqlite3.Error as e:
    print("has_inventory_job: {}".format(e))
    return False

def set_inventory_output(conn,id,output):
  try:
    curr = conn.cursor()
    
    curr.execute('update glacier_job set output = ? where id = ?',(output, id))
 
    conn.commit()
    
    return True
  except sqlite3.Error as e:
    print("set_inventory_output: {}".format(e))
    return False

def get_inventory_output(conn,id):
  try:
    curr = conn.cursor()
    
    curr.execute('select output from glacier_job where id = ?',(id,))
 
    row = curr.fetchone()
    
    return row[0]
  except sqlite3.Error as e:
    print("get_inventory_output: {}".format(e))
    return False

def add_glacier_job(conn,id=None,account=None,vault=None,parameters=None,description=None,output=None):
  
  try:
    curr = conn.cursor()
    
    curr.execute('INSERT INTO glacier_job VALUES (?,?,?,?,?,?)',(id,account,vault,parameters,description,output))
      
    conn.commit()
    
    return True
  except sqlite3.Error as e:
    print('add_glacier_job',e)
    return False
