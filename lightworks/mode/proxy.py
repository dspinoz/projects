
class ProxyMode(LWHelperBase):
	def __init__(self):
		LWHelperBase.__init__(self)
		print "proxy init"
		
	def add_options(self,parser):
		LWHelperBase.add_options(self,parser)
		
	def main(self, options, args):
		print "proxy main"
		paths = find_media(options.raw_dir)
		for r in paths:
			f = LWHelperFile(options, r)
			
			if f.is_proxy():
				continue
			
			f.clear()
			
			if options.action_set:
				f.set_proxy()
			else:
				f.unset_proxy()

