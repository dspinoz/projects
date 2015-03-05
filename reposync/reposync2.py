from yum.constants import *
from yum.plugins import PluginYumExit, TYPE_CORE
import tarfile
from time import strftime
import os.path

requires_api_version = '2.6'
plugin_type = (TYPE_CORE)
pre_packages = []

def package_is_valid(pack):
	if os.path.isfile(pack.localPkg()) == True and os.path.getsize(pack.localPkg()) == int(pack.returnSimple('packagesize')) and pack.verifyLocalPkg() == True:
		return True
	return False

def init_hook(conduit):
	#conduit.info(2, 'hello world')
	print "DS INIT FOO", conduit.confBool('main','foo',False) == True, conduit.confBool('main', 'keeplog', False) == False
	#timeformat = conduit.confString('main', 'timeformat', '%c')
	#if conduit.confBool('main', 'keeplog', False):
	#	outname = "%s-%s.log" %(
	#		conduit.confString('main', 'fileprefix', 'reposync'), 
	#		strftime(timeformat))
	#	logfile = open(outname, 'w')
	#	print "Writing progress to", outname

def config_hook(conduit):
	if hasattr(conduit.getOptParser, 'add_option'):
		# Command Options cannot be added to reposync
		conduit.getOptParser().add_option('','--foo', dest='foo',
			action='store_true', default=False,
			help='Fooooooooo')

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





