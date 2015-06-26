from yum.constants import *
from yum.plugins import PluginYumExit, TYPE_CORE
import tarfile
import time;
import os.path
import sys
import glob
import re
import shutil
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

	if hasattr(conduit.getOptParser(), 'parse_args'):
		(opts, args) = conduit.getOptParser().parse_args()
		if opts.reposync2enable == False:
			print "reposync2 disabled, no incremental will be produced"


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
		conduit.getOptParser().add_option('','--reposync2-enable', 
			dest='reposync2enable', action='store_true', default=False,
			help='Continue to build package cache from yum')
		conduit.getOptParser().add_option('','--incremental-dir', 
			dest='incrdir', action='store', default='.',
			help='Directory for performing merge')
		conduit.getOptParser().add_option('','--dest-dir', 
			dest='destdir', action='store', default='./',
			help='Directory where rpms are kept')
		conduit.getOptParser().add_option('','--download_path', 
			dest='reposyncdir', action='store', default='./',
			help='Directory where reposync writes')

def predownload_hook(conduit):
	repodir = False
	if hasattr(conduit.getOptParser(), 'parse_args'):
		(opts, args) = conduit.getOptParser().parse_args()
		if opts.reposync2enable == False:
			return
		repodir = opts.reposyncdir
	
	saved_downloads = 0
	saved_packages = 0

	# new packages available in the repo, filter what we need to get
	for pack in conduit.getDownloadPackages():
		
		# Package is in the yum cache
		package_cached = package_is_valid(pack)
		
		# Package has been downloaded already
		package_downloaded = False
		syncpath = False

		if repodir != False:
			# Check if package is available
			syncpath = os.path.join(repodir, "%s/%s" %( pack.repo.id, pack.remote_path ))

			if not os.path.isfile(syncpath):
				# Access remote url on the object as will be used later on...
				pack._remote_url()
			else:
				package_downloaded = True

		# Already have the package, put it into the yum cache
		# Speedup for yum - use the packages downloaded via reposync
		if not package_cached and package_downloaded and syncpath != False:
			dir = os.path.dirname(syncpath)
			if not os.path.exists(dir):
				os.makedirs(dir)
			shutil.copy(syncpath, pack.localPkg())

			saved_packages += 1
			saved_downloads += int(pack.returnSimple('packagesize'))

		# Build an incremental
		if not package_cached or not package_downloaded:
			pre_packages.append(pack)

	if saved_packages != 0:
		print "Saved downloading", saved_packages, "packages (", saved_downloads, " bytes)"
			
def postdownload_hook(conduit):
	if sys.argv[0] == '/bin/reposync':
		return

	# path for when inside yum
	# --downloadonly skips here - see close_hook
	# build incremental early - packages in local cache may be removed!
	build_incremental(conduit, conduit.getDownloadPackages())

def close_hook(conduit):
	# Path for reposync
	# Path for yum with --downloadonly
	# TODO consolidate seperate paths into single function def
	build_incremental(conduit, pre_packages)

def build_incremental(conduit, packages):
	if len(packages) == 0:
		return
		
	inreposync = sys.argv[0] == '/bin/reposync'
	reposyncdir = False

	if hasattr(conduit.getOptParser(), 'parse_args'):
		(opts, args) = conduit.getOptParser().parse_args()
		if opts.reposync2enable == False:
			print "reposync2 not enabled"
			return
		reposyncdir = opts.reposyncdir
		inreposync = False

	# prescan the packages - only build if something downloaded and not in the cache
	forbuild = []
	
	for pack in packages:
	
		if inreposync:
			# in reposync 
			# verify packages have been downloaded in full
			if package_is_valid(pack) == True:
				forbuild.append(pack)
					
		else:
			# in yum
			syncpath = os.path.join(reposyncdir, "%s/%s" %( pack.repo.id, pack.remote_path ))
			syncdir = os.path.dirname(syncpath)

			# A custom verify
			#   1. verify it is available locally (downloaded to local yum cache)
			#   2. check if its already in the cache (in reposync format)
			#   3. verify has been downloaded in full

			if os.path.isfile(pack.localPkg()) == True and pack.verifyLocalPkg() == True and os.path.isfile("%s/%s" %( syncdir, os.path.basename(pack.localPkg()) )) == True:
				# already in cache
				continue

			if os.path.isfile(pack.localPkg()) == True and pack.verifyLocalPkg() == True and os.path.getsize(pack.localPkg()) == int(pack.returnSimple('packagesize')):
				# Put it into the cache - create the structure like reposync
				pack.reposync2_output_path = syncpath
				print "reposync2 - caching", "%s/%s" %( pack.repo.id, pack.remote_path )
				forbuild.append(pack)
	
	
	# only for reposync, unless otherwise specified

	if hasattr(conduit.getOptParser(), 'parse_args'):
		# in yum
		(opts, args) = conduit.getOptParser().parse_args()
		if opts.reposync2enable == False:
			if len(forbuild) > 0:
				print "Not building download incremental, disabled"
				print "  ", len(forbuild), "packages were available for caching"
			return
	
	if len(forbuild) == 0:
		print 'No new packages downloaded'
		return
	
	# contribute to the repo and build incremental
	repolist = {}

	timestr = time.strftime(conduit.confString('main', 'timeformat', '%c'))
	
	# maintain audit log
	logfilename = "%s-%s.csv" %(
		conduit.confString('main', 'fileprefix', 'reposync'), 
		timestr )

	logfile = open(logfilename, 'w')

	logfile.write("rpmfile,remote_url\n")
	for pack in forbuild:

		logfile.write("%s,%s\n" %(
			"%s/%s" %( pack.repo.id, pack.remote_path ), pack._remote_url() ))

	logfile.close()
	
	
	# Create incremental

	outname = "%s-%s.tar.gz" %(
		conduit.confString('main', 'fileprefix', 'reposync'), 
		timestr )
		
	print "Writing incremental", os.path.basename(outname)
	
	splitter = TarSplit( outname,
			conduit.confInt('main', 'maxfilesize', None) )

	tar = tarfile.open(fileobj=splitter, mode='w|gz')
	tar.add(logfilename)
	
	for pack in forbuild:
		
		# track repositories for user stats
		if pack.repo.id in repolist.keys():
			repolist[pack.repo.id] += 1
		else:
			repolist[pack.repo.id] = 1
			
		if inreposync == False:
			# yum contributes to reposync cache
			dir = os.path.dirname(pack.reposync2_output_path)
			if not os.path.exists(dir):
				os.makedirs(dir)
			shutil.copy(pack.localPkg(), pack.reposync2_output_path)

		# maintain files inside the incremental like reposync does
		# this way, the directory structure will look the same
		# and reposync can be performed on the remote host

		tar.add(pack.localPkg(), "%s/%s" %( pack.repo.id, pack.remote_path ))
	
	tar.close()
	
	if splitter.count > 0:
		print "  Split into", splitter.count, "files"

	if conduit.confBool('main', 'keeplog', False) == False:
		os.remove(logfilename)

	print "Successfully built incremental", timestr
	print "  Contains", len(forbuild), "packages from", len(repolist.keys()), "repos"
	
	
