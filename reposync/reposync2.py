from yum.constants import *
from yum.plugins import PluginYumExit, TYPE_CORE
import tarfile
import time;
import os.path
import sys
import glob
import re
from operator import itemgetter

# TODO catch exceptions

requires_api_version = '2.6'
plugin_type = (TYPE_CORE)
pre_packages = []

class TarSplit:

	name = None
	fd = None
	max = None
	written = 0
	count = 1
	input = []

	def __init__(self, name, max=None):
		self.name = name
		self.max = max

	def read(self, bufsize):
		if self.fd is None:
			self.fd = open(self.name, 'rb')
			print "Reading incremental", os.path.basename(self.name)
			files = glob.glob("%s.*" %( self.name ))

			# Sort files in number order, not ascii order
			for f in files:
				match = re.search(".*.tar.gz.([0-9]+)", f)
				if match:
					self.input.append((int(match.group(1)), f))
			self.input.sort(key=lambda x: x[0], reverse=True)

		got = self.fd.read(bufsize)

		if len(got) == 0:
			try:
				(i, n) = self.input.pop()
				print "Reading incremental", os.path.basename(n)
				self.fd.close()
				self.fd = open(n, 'rb')
				got = self.fd.read(bufsize)
			except IndexError:
				pass
		
		return got

	def write(self, str):
		# TODO handle disk filling up
		if self.fd is None:
			self.fd = open(self.name, 'wb')
			print "Writing incremental", os.path.basename(self.name)

		if self.max > 0 and self.written + len(str) > self.max:
			self.fd.close()
			n = "%s.%02d" %( self.name, self.count )
			self.fd = open(n, 'wb')
			self.count += 1
			self.written = 0

		self.written += len(str)
		self.fd.write(str)


def package_is_valid(pack):
	if os.path.isfile(pack.localPkg()) == True and os.path.getsize(pack.localPkg()) == int(pack.returnSimple('packagesize')) and pack.verifyLocalPkg() == True:
		return True
	return False

def merge_incrementals(opts, conduit):

	cwd = os.getcwd()
	opts.incrdir = os.path.realpath(opts.incrdir)
	opts.destdir = os.path.realpath(opts.destdir)
	print "Merging incrementals FROM", opts.incrdir, "TO", opts.destdir

	# Easiest for untarring
	os.chdir(opts.destdir)

	lastupdate=0
	if os.path.isfile('.reposync2.meta'):
		meta = open('.reposync2.meta')
		lastupdate = meta.readline()
		if lastupdate:
			lastupdate = lastupdate.rstrip()
			lastupdate = float(lastupdate)
			print "Repo currently at", time.strftime(conduit.confString('main', 'timeformat', '%c'), time.localtime(lastupdate))
		else:
			lastupdate = 0
		meta.close()

	incrementals = glob.glob("%s/%s*.tar.gz" %( opts.incrdir, 
		conduit.confString('main', 'fileprefix', 'reposync')) )

	toexport = []

	# have latest first - dont keep searching unnecessarily
	incrementals.sort(reverse=True)

	for inc in incrementals:
		match = re.search( "%s-(.*).tar.gz" %(
				conduit.confString('main', 'fileprefix', 'reposync')), 
			os.path.basename(inc) )
		
		if match:
			sec = time.mktime(time.strptime(match.group(1), conduit.confString('main', 'timeformat', '%c')))
			if int(sec) > int(lastupdate):
				toexport.append((sec, inc))
			else:
				break
			
	
	# Export older packages first
	toexport.sort()

	for tm,inc in toexport:
		tar = tarfile.open(fileobj=TarSplit(inc), mode='r|gz')
		# its a tarfile stream - can only call extractall!
		tar.extractall()
		tar.close()
		lastupdate = tm

	if len(toexport) == 0:
		print "Repo is up to date"
	else:
		print "Repo updated to", time.strftime(conduit.confString('main', 'timeformat', '%c'), time.localtime(lastupdate))

	# TODO perform createrepo

	meta = open('.reposync2.meta', 'w')
	meta.write("%02f\n" %( lastupdate ))
	meta.close()

def init_hook(conduit):

	if hasattr(conduit.getOptParser(), 'parse_args'):
		(opts, args) = conduit.getOptParser().parse_args()
		if opts.merge:
			merge_incrementals(opts, conduit)
			raise PluginYumExit('Exiting because merging only')

def config_hook(conduit):

	# Command Options cannot be added to reposync
	if hasattr(conduit.getOptParser(), 'add_option'):
		# TODO option to perform sync from yum interface
		#      this way, will use available yum options instead
		# TODO allow command line options to override config file
		# TODO specify options for all available in config
		conduit.getOptParser().add_option('','--reposync2-merge', 
			dest='merge', action='store_true', default=False,
			help='Merge incremental reposync changes locally')
		conduit.getOptParser().add_option('','--incremental-dir', 
			dest='incrdir', action='store', default='.',
			help='Directory for performing merge')
		conduit.getOptParser().add_option('','--dest-dir', 
			dest='destdir', action='store', default='./repos-merged/',
			help='Directory where rpms are kept')

def predownload_hook(conduit):
	# new packages available in the repo, filter what we need to get
	for pack in conduit.getDownloadPackages():
		if package_is_valid(pack) != True:
			pre_packages.append(pack)

def close_hook(conduit):

	new_packages = []
	
	# verify packages have been downloaded in full
	for pack in pre_packages:
		if package_is_valid(pack) == True:
			new_packages.append(pack)
	
	if len(new_packages) == 0:
		print 'No packages downloaded'
	else:

		if sys.argv[0] != '/bin/reposync':
			print "Not building download incremental, not in reposync"
			return

		timestr = time.strftime(conduit.confString('main', 'timeformat', '%c'))

		outname = "%s-%s.tar.gz" %(
			conduit.confString('main', 'fileprefix', 'reposync'), 
			timestr )

		logfilename = "%s-%s.csv" %(
			conduit.confString('main', 'fileprefix', 'reposync'), 
			timestr )

		# maintain audit log
		logfile = open(logfilename, 'w')

		logfile.write("rpmfile,remote_url\n")
		for pack in new_packages:
			fname = "%s/%s" %(pack.repo.id,
					os.path.basename(pack.localPkg()))

			logfile.write("%s,%s\n" %(
				fname, pack._remote_url() ))

		logfile.close()

		# Create incremental
		
		splitter = TarSplit( outname,
				conduit.confInt('main', 'maxfilesize', None) )

		tar = tarfile.open(fileobj=splitter, mode='w|gz')
		tar.add(logfilename)

		repolist = {}
		
		for pack in new_packages:
			if pack.repo.id in repolist.keys():
				repolist[pack.repo.id] += 1
			else:
				repolist[pack.repo.id] = 1

			fname = "%s/%s" %(
				pack.repo.id, 
				os.path.basename(pack.localPkg()) )
			tar.add(pack.localPkg(), fname)
		
		tar.close()

		if splitter.count > 0:
			print "  Split into", splitter.count, "files"

		if conduit.confBool('main', 'keeplog', False) == False:
			os.remove(logfilename)

		print "Successfully built incremental", timestr
		print "  Contains", len(new_packages), "packages from", len(repolist.keys()), "repos"


