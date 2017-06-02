import os
from datetime import datetime

def eprint(*args, **kwargs):
  #print(*args, file=sys.stderr, **kwargs)
  pass

def size_human(num, suffix=''):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)

def time_str(epoch):
  t = datetime.fromtimestamp(epoch)
  str = t.strftime("%b %d %H:%S")
  
  now = datetime.now()   
  if now.year != t.year:
    str = t.strftime("%b %d  %G")
    
  return str
    
def safe_path(str):
  return "".join(c for c in str if c.isalnum() or c in (' ','.','_')).rstrip()
    
def strip_path_components(path,index=0,safe_root=False,join=True):
  
  directories = []
  
  path = os.path.realpath(path)
  
  while path:

    if os.path.dirname(path) == path:
      # got to the root
      (drive,drive_path) = os.path.splitdrive(path)
      if len(drive):
        if safe_root:
          directories.insert(0,safe_path(drive))
        else:
          directories.insert(0,drive)
      else:
        directories.insert(0,path)
      break

    # pop up a level
    (path,tail) = os.path.split(path)
    directories.insert(0,tail)

  if join:
    return os.sep.join(directories[index:])
  return directories[index:]

def stream_watcher(queue, identifier, stream):
	while not stream.closed:
		line = stream.readline()
		if not line:
			break
		queue.put((identifier, line))

def ffmpeg_print_output(queue,proc):

	while True:
		try:
			it = queue.get(True,1)
		except Empty:
			if proc.poll() is not None:
				break
		else:
			identifier,line = it
			print identifier + ':', line
				

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def find_media(search='raw', exts=['.MOV']):
	ret = []
	for root,dirs,files in os.walk(search):
		
		for f in files:
			if f.startswith("."):
				continue
			for ext in exts:
				if f.endswith(ext):
					p = os.path.join(root,f)
					if p.startswith(search+"/"):
						ret.append(p[len(search)+1:])
					elif p.startswith(search):
						ret.append(p[len(search):])
	return ret


