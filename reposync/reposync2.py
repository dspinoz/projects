from yum.constants import *
from yum.plugins import PluginYumExit, TYPE_CORE
import tarfile
import time;
import os.path
import sys
import glob
import re

# TODO catch exceptions

requires_api_version = '2.6'
plugin_type = (TYPE_CORE)
pre_packages = []

def package_is_valid(pack):
	if os.path.isfile(pack.localPkg()) == True and os.path.getsize(pack.localPkg()) == int(pack.returnSimple('packagesize')) and pack.verifyLocalPkg() == True:
		return True
	return False

def merge_incrementals(opts, conduit):

	cwd = os.getcwd()
	opts.incrdir = os.path.realpath(opts.incrdir)
	opts.destdir = os.path.realpath(opts.destdir)
	print "DS MERGE AT", cwd, "FROM", opts.incrdir, "TO", opts.destdir

	# Easiest for untarring
	os.chdir(opts.destdir)

	lastupdate=0
	if os.path.isfile('.reposync2.meta'):
		meta = open('.reposync2.meta')
		lastupdate = meta.readline()
		if lastupdate:
			lastupdate = lastupdate.rstrip()
			lastupdate = float(lastupdate)
			print "LAST UPDATE AT", time.strftime(conduit.confString('main', 'timeformat', '%c'), time.localtime(lastupdate)), lastupdate
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
				print "[X]", os.path.basename(inc), sec
				toexport.append((sec, inc))
			else:
				print "[ ]", os.path.basename(inc), sec
				break
			
	
	# Export older packages first
	toexport.sort()

	for tm,inc in toexport:
		print "DS EXTRACT", os.path.basename(inc), tm
		tar = tarfile.open(inc)
		tar.extractall()
		tar.close()
		lastupdate = tm

	# TODO perform createrepo

	print "DS MERGE SUCCESS"

	meta = open('.reposync2.meta', 'w')
	meta.write("%02f\n" %( lastupdate ))
	meta.close()

def init_hook(conduit):
	#conduit.info(2, 'hello world')
	print "DS INIT FOO", conduit.confBool('main','foo',False) == True, conduit.confBool('main', 'keeplog', False) == False, sys.argv[0]

	if hasattr(conduit.getOptParser(), 'parse_args'):
		(opts, args) = conduit.getOptParser().parse_args()
		if opts.merge:
			merge_incrementals(opts, conduit)
			raise PluginYumExit('Exiting because merging only')

def config_hook(conduit):
	print "DS CONFIG"
	# Command Options cannot be added to reposync
	if hasattr(conduit.getOptParser(), 'add_option'):
		print "DS ADDED MERGE OPTION"
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

def args_hook(conduit):
	print "DS ARGS", conduit.getArgs()

def postconfig_hook(conduit):
	print "DS POST CONFIG"

def prereposetup(conduit):
	print "DS MERGE", conduit.getConf().merge == True

def postreposetup_hook(conduit):
	#conduit.info(2', 'got repos')
	print "DS REPO SETUP", conduit.getRepos().listEnabled()

def predownload_hook(conduit):
	#conduit.info(2, 'downloading...')
	print "DS PREDOWN", len(pre_packages)
	for pack in conduit.getDownloadPackages():
		if package_is_valid(pack) != True:
			pre_packages.append(pack)
	print "DS PREDOWN", len(pre_packages), "TO FETCH"

def postdownload_hook(conduit):
	#conduit.info(2, 'downloaded.')
	print "DS POSTDOWN", len(conduit.getDownloadPackages())

def posttrans_hook(conduit):
	print "DS TRANS DONE"

def close_hook(conduit):

	new_packages = []
	print "DS CLOSE", len(new_packages), " FETCHED"
	# verify packages have been downloaded in full
	for pack in pre_packages:
		if package_is_valid(pack) == True:
			new_packages.append(pack)
			print "DS DOWNLOADED", pack, pack.repo.id
	if len(new_packages) > 0:
		repolist = {}
		outname = "%s-%s.tar.gz" %(
			conduit.confString('main', 'fileprefix', 'reposync'), 
			time.strftime(conduit.confString('main', 'timeformat', '%c')))

		logfilename = "%s-%s.csv" %(
			conduit.confString('main', 'fileprefix', 'reposync'), 
			time.strftime(conduit.confString('main', 'timeformat', '%c')))
		logfile = open(logfilename, 'w')

		logfile.write("rpmfile,remote_url\n")
		for pack in new_packages:
			fname = "%s/%s" %(pack.repo.id,
					os.path.basename(pack.localPkg()))

			logfile.write("%s,%s\n" %(
				fname, pack._remote_url() ))

		logfile.close()

		# TODO split large tar file into smaller chunks

		tar = tarfile.open(outname, 'w:gz')
		tar.add(logfilename)
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

		
		if conduit.confBool('main', 'keeplog', False) == False:
			os.remove(logfilename)

		print "Incremental package list built:", outname
		print "  Contains", len(new_packages), "packages from", len(repolist.keys()), "repos"
	print "DS DONE", len(new_packages)





