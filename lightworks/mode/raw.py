class RawMode(LWHelperBase):
	def __init__(self):
		LWHelperBase.__init__(self)
		print "raw init"
		
	def add_options(self,parser):
		LWHelperBase.add_options(self,parser)
		
	def do_import(self,options,args):
		for i in options.imports:
			print "  ",os.path.realpath(i)
			i = os.path.realpath(i)
			if os.path.isdir(i):
				print "dir",i
				files = find_media(i)
				for f in files:
					
					lwf = LWHelperFile(options, f)
					
					lwf.importraw(os.path.join(i,f))
					
			elif os.path.isfile(i):
				
				lwf = LWHelperFile(options, i)
				
				lwf.importraw(i)
				
			else:
				print "ERROR Unsupported import file", i
	
		
	def main(self, options, args):
		print "raw main"
		
		if options.imports:
			print "raw importing", options.imports
			self.do_import(options, args)
			return
			
		paths = find_media(options.raw_dir)
		for r in paths:
			f = LWHelperFile(options, r)
			
			if f.is_raw():
				continue
			
			f.clear()

			if options.action_set:
				f.set_raw()
