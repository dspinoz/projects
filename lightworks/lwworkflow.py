#!/usr/bin/python

import os
import sys
import errno
import subprocess
import shutil
from optparse import OptionParser

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

class LWHelperFile:
	def __init__(self, options, path):
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

		subprocess.check_output(["ffmpeg", "-i", self.raw, "-c:a", "copy", "-filter:v", "scale=iw/%d:-1" %(self.options.scale), self.proxy], stderr=subprocess.STDOUT)


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

class RawMode(LWHelperBase):
	def __init__(self):
		LWHelperBase.__init__(self)
		print "raw init"
		
	def add_options(self,parser):
		LWHelperBase.add_options(self,parser)
		
	def main(self, options, args):
		print "raw main"
		
		if options.imports:
			print "raw importing", options.imports.split(',')
			
			return
			
			for i in options.imports:
				print "  ",os.path.realpath(i)
				i = os.path.realpath(i)
				if os.path.isdir(i):
					print "dir",i
					files = find_media(i)
					for f in files:
						# file path
						fp = os.path.join(i,f)
						# project path
						pp = options.raw_dir + os.sep + os.path.join(fp)
						
						print "creating",pp,"from",fp
						
						try:
							os.makedirs(os.path.dirname(pp))
						except OSError as e:
							if e.errno == errno.EEXIST:
								pass
						
						if not os.path.isfile(pp) and not os.path.islink(pp):
							os.symlink(fp,pp)
						else:
							print "ERROR file already exits", pp
				elif os.path.isfile(i):
					
					if not os.path.isfile(i) and not os.path.islink(i):
						print "ERROR cannot find",i
						return
					
					if os.path.islink(i):
						print "link",i
					else:
						print "file",i
						
					fp = i
					pp = options.raw_dir + os.sep + i
					
					print "creating",pp,"from",fp
					
					try:
						os.makedirs(os.path.dirname(pp))
					except OSError as e:
						if e.errno == errno.EEXIST:
							pass
					
					if not os.path.isfile(pp) and not os.path.islink(pp):
						os.symlink(fp,pp)
					else:
						print "ERROR file already exits", pp
					
				else:
					print "ERROR Unsupported file type", i
			return
		
		paths = find_media(options.raw_dir)
		for r in paths:
			f = LWHelperFile(options, r)
			
			if f.is_raw():
				continue
			
			f.clear()

			if options.action_set:
				f.set_raw()
	
desc="""Helper script for maintaining a workflow for video editing.

This workflow helps to ensure the "best possible" performance while editing video, even on low-end machines.

Consider the following directory structure:

* raw/     : raw capture files
* project/ : working video files
* proxy/   : low-resolution video files

The project directory is a dynamic area, which will be managed by this script.

To get started:

1. Import raw files into the raw directory

   ./conv.py --mode=raw --import=FILE --import=DIR

2. Create the project directory and proxy files for editing

   ./conv.py 
   
   Proxy files will also be generated (using ffmpeg)

3. Open video editor and make your video...

4. When ready for high-resolution export, close the video editing program

5. Revert to raw files

   ./conv.py --mode=raw

5. Open video editor and export using high-res files

6. Revert back to proxy files for more editing

   ./conv.py --mode=proxy

"""
	
from optparse import HelpFormatter as fmt
def decorate(fn):
	def wrapped(self=None, desc=""):
		return '\n'.join( [ fn(self, s).rstrip() for s in desc.split('\n') ] )
	return wrapped
fmt.format_description = decorate(fmt.format_description)
	
	
def main():
	parser = OptionParser(add_help_option=False,description=desc)
	parser.add_option('-h', "--help", dest="help", action="store_true", help="Show help message and exit")
	parser.add_option("-s", "--search", dest="searchdir", help="Print files in a directory")
	parser.add_option("-L", "--list_modes", dest="listmodes", action="store_true", help="List the available modes")
	parser.add_option("-m", "--mode", dest="mode", help="Set the current mode of the project [default: %default]", default="proxy")
	parser.add_option("-U", "--unset", dest="action_set", action="store_false", default=True, help="Unset the project file as per mode [default: Set]")
	parser.add_option("-S", "--scale", dest="scale", default=4, help="Set the scale factor for proxy files [default: %default]")
	parser.add_option("-C", "--clear", dest="project_clear", action="store_true", default=False, help="Clear all project files")
	parser.add_option("-i", "--import", dest="imports", action="append", help="Import raw files to the project")
	
	(options,args) = parser.parse_args()

	if options.help and not options.mode:
		print parser.format_help()
		sys.exit(0)
		
	if options.listmodes:
		print "project"
		print "proxy"
		print "raw"
		sys.exit(0)

	if options.searchdir:
		for f in find_media(options.searchdir):
			print f
		sys.exit(0)
		
	if not options.mode:
		parser.error("No mode supplied")

	modeObject = None

	if options.mode == "project":
		modeObject = ProjectMode()
	if options.mode == "proxy":
		modeObject = ProxyMode()
	if options.mode == "raw":
		modeObject = RawMode()
		
	if modeObject == None:
		parser.error("Invalid Mode \"%s\"" %(options.mode))
		
	modeObject.add_options(parser)
	
	(options,args) = parser.parse_args()
	
	if options.help:
		print parser.format_help()
		sys.exit(0)
	
	modeObject.main(options,args)

if __name__ == "__main__":
	main()

