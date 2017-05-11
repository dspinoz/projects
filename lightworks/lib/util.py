
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


