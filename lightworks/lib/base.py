
class LWHelperBase:
	def __init__(self):
		print "base init"
		
	def add_options(self, parser):
		print "base adding options"
		parser.add_option("-r", "--raw_dir", dest="raw_dir", default="raw", help="Directory for raw files [default: %default]")
		parser.add_option("-p", "--project_dir", dest="project_dir", default="project", help="Directory for project files [default: %default]")
		parser.add_option("-x", "--proxy_dir", dest="proxy_dir", default="proxy", help="Directory for proxy files [default: %default]")
		
	def main(self, options, args):
		print "base main"


