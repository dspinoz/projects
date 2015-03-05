from yum.constants import *
from yum.plugins import PluginYumExit, TYPE_CORE
import tarfile
from time import strftime
import os.path
import sys

requires_api_version = '2.6'
plugin_type = (TYPE_CORE)
pre_packages = []

def package_is_valid(pack):
	if os.path.isfile(pack.localPkg()) == True and os.path.getsize(pack.localPkg()) == int(pack.returnSimple('packagesize')) and pack.verifyLocalPkg() == True:
		return True
	return False

def init_hook(conduit):
	#conduit.info(2, 'hello world')
	print "DS INIT FOO", conduit.confBool('main','foo',False) == True, conduit.confBool('main', 'keeplog', False) == False, sys.argv[0]

	if hasattr(conduit.getOptParser(), 'parse_args'):
		(opts, args) = conduit.getOptParser().parse_args()
		if opts.merge:
			raise PluginYumExit('merging incremental reposync')

def config_hook(conduit):
	print "DS CONFIG"
	# Command Options cannot be added to reposync
	if hasattr(conduit.getOptParser(), 'add_option'):
		print "DS ADDED MERGE OPTION"
		# TODO option to perform sync from yum interface
		#      this way, will use available yum options instead
		conduit.getOptParser().add_option('','--reposync2-merge', 
			dest='merge', action='store_true', default=False,
			help='Merge incremental reposync changes locally')

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
			strftime(conduit.confString('main', 'timeformat', '%c')))

		logfilename = "%s-%s.csv" %(
			conduit.confString('main', 'fileprefix', 'reposync'), 
			strftime(conduit.confString('main', 'timeformat', '%c')))
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





