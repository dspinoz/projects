	
class LWHelperFile:
	def __init__(self, options, path):
		
		# all paths are relative within the project
		if path[0] == "/":
			path = path[1:]
			
		self.path = path	
		self.options = options
		
		self.raw = os.path.join(options.raw_dir, path)
		self.project = os.path.join(options.project_dir, path)
		self.proxy = os.path.join(options.proxy_dir, path)

		self.project_raw = os.path.join(options.project_dir, os.path.join(os.path.dirname(path), ".raw."+os.path.basename(path)))
		self.project_proxy = os.path.join(options.project_dir, os.path.join(os.path.dirname(path), ".proxy."+os.path.basename(path)))

		print "f",self.path,self.raw,self.project,self.proxy
		
	def __str__(self):
		return self.path
		
	def has_proxy(self):
		return os.path.isfile(self.proxy)

	def is_proxy(self):
		return os.path.isfile(self.project_proxy)
		
	def has_raw(self):
		return os.path.isfile(self.raw)

	def is_raw(self):
		return os.path.isfile(self.project_raw)

		
	def ensure_proxy(self):
		if self.has_proxy():
			return

		if os.path.isfile(self.project_proxy):
			return

		print "X* %s Generating 1/%d resolution proxy" %(self.path,self.options.scale)
		
		try:
			os.makedirs(os.path.dirname(self.proxy))
		except OSError as e:
			if e.errno == errno.EEXIST:
				pass

		# retrieve metadata to stdout
		# ffmpeg -loglevel error -y -i {} -f ffmetadata /dev/stdout
		# get duration in seconds
		# ffprobe  -i {} -show_entries format=duration -v quiet -of csv="p=0"
		
		try:
			len_sec = subprocess.check_output(["ffprobe", "-i", self.raw, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv='p=0'"], stderr=subprocess.STDOUT)
		
			print "********",self.raw,":",len_sec,"seconds"
		except subprocess.CalledProcessError as e:
			print e.returncode
		
		return
		
		io_q = Queue()
		
		proc = subprocess.Popen(["ffmpeg", "-stats", "-progress", "/dev/stdout", "-i", self.raw, "-c:a", "copy", "-filter:v", "scale=iw/%d:-1" %(self.options.scale), self.proxy], 
			stdout=subprocess.PIPE, stderr=subprocess.PIPE)
							
		outt = threading.Thread(target=stream_watcher, name='stdout-watcher',
				args=(io_q, 'STDOUT', proc.stdout))
				
		errt = threading.Thread(target=stream_watcher, name='stderr-watcher',
				args=(io_q, 'STDERR', proc.stderr))

		printt = threading.Thread(target=ffmpeg_print_output, name='printer',
				args=(io_q, proc))

		outt.start()
		errt.start()
		printt.start()

		print "FFMPEG THREADS STARTED"

		proc.wait()

		outt.join()
		errt.join()
		printt.join()
		
		print "FFMPEG DONE", proc.returncode
		

	def set_proxy(self):
		if os.path.isfile(self.project_proxy):
			print "X ", self.path
			return

		if not os.path.isfile(self.proxy):
			self.ensure_proxy()
		else:
			print "X+", self.path
		
		try:
			os.makedirs(os.path.dirname(self.project))
		except OSError as e:
			if e.errno == errno.EEXIST:
				pass

		shutil.move(self.proxy,self.project)

		open(self.project_proxy,'a').close()

	def set_raw(self):
		if os.path.isfile(self.project_raw):
			print "R ", self.path
			return

		if not os.path.isfile(self.raw):
			print "ERROR No raw file %s" %(self.path)
			return
		
		print "R+", self.path
			
		try:
			os.makedirs(os.path.dirname(self.project))
		except OSError as e:
			if e.errno == errno.EEXIST:
				pass

		os.symlink(self.raw,self.project)

		open(self.project_raw,'a').close()

	def unset_proxy(self):
		if not os.path.isfile(self.project_proxy):
			return
		print "X-", self.path
		os.remove(self.project_proxy)
		shutil.move(self.project,self.proxy)
		
	def unset_raw(self):
		if not os.path.isfile(self.project_raw):
			return
		print "R-", self.path
		os.remove(self.project_raw)
		os.remove(self.project)

	def clear(self):
		if not os.path.isfile(self.project) and not os.path.islink(self.project):
			print "-  %s" %(self.path)
			return
		if os.path.isfile(self.project_proxy):
			self.unset_proxy()
		elif os.path.isfile(self.project_raw):
			self.unset_raw()
		else:
			print "Unknown project mode for %s" %(self.path)

	def importraw(self,importpath):
		
		print "creating",self.raw,"from",importpath
		if os.path.islink(importpath):
			print "link",importpath
		else:
			print "file",importpath
		
		if not os.path.isfile(importpath) and not os.path.islink(importpath):
			print "ERROR cannot find",importpath
			return
		
		
		try:
			os.makedirs(os.path.dirname(self.raw))
		except OSError as e:
			if e.errno == errno.EEXIST:
				pass
		
		importpath = os.path.realpath(importpath)
		
		if not os.path.isfile(self.raw) and not os.path.islink(self.raw):
			os.symlink(importpath,self.raw)
		else:
			print "ERROR file already exists", importpath

	

class ProjectMode(LWHelperBase):
	def __init__(self):
