
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
				
