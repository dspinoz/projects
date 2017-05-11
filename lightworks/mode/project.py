
class ProjectMode(LWHelperBase):
	def __init__(self):
		LWHelperBase.__init__(self)
		print "project init"
		
	def add_options(self,parser):
		LWHelperBase.add_options(self,parser)
		
	def main(self, options, args):
		print "project main", options.project_clear, options.raw_dir
		paths = find_media(options.project_dir)
		print "paths", paths
		for r in paths:
			f = LWHelperFile(options, r)
			print "f", f
			if options.project_clear:
				f.clear()

