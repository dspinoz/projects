import os

def data_dir():

  searching_for = ".lwf"
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

  if found_path is None:
    print "data dir None"
  else:
    print "data dir",os.path.relpath(found_path)
  
  return found_path
