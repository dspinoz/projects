import sqlite3
import os

import db

db_name = "aws_photo_library.db"
dir_name = ".apl"

def data_dir(err=True):

  searching_for = dir_name
  start_path = os.path.realpath(os.getcwd())

  last_root    = start_path
  current_root = start_path
  found_path   = None

  while found_path is None and current_root:
    if os.path.exists(os.path.join(current_root,searching_for)) and os.path.isdir(os.path.join(current_root,searching_for)):
      # found the file, stop
      found_path = os.path.join(current_root, searching_for)
      break

    if os.path.dirname(current_root) == current_root:
      break

    # Otherwise, pop up a level, search again
    last_root    = current_root
    (head,tail) = os.path.split(current_root)
    current_root = head
  
  if found_path is None and err:
    raise aplexcept.APLNotInitialisedError("Not initialised")
  return found_path

def init():
  root_path = data_dir()
  
  db.init(root_path, db_name)
