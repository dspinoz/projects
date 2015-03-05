from yum.constants import *
from yum.plugins import PluginYumExit, TYPE_CORE
import tarfile
from time import strftime
import os.path

requires_api_version = '2.6'
plugin_type = (TYPE_CORE)
pre_packages = []
timeformat=''

def package_is_valid(pack):
	if os.path.isfile(pack.localPkg()) == True and os.path.getsize(pack.localPkg()) == int(pack.returnSimple('packagesize')):
		return True
	return False

def init_hook(conduit):
	#conduit.info(2, 'hello world')
	print "DS INIT FOO", conduit.confBool('main','foo',False) == True
	timeformat = conduit.confString('main', 'timeformat', '%Y%m%d%H%M%S')
	print "TIME", strftime(timeformat)

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
	for pack in pre_packages:
		if package_is_valid(pack) == True:
			new_packages.append(pack)
			print "DS DOWNLOADED", pack.localPkg()
	print "DS POSTDOWN DONE", len(new_packages)
	if len(new_packages) > 0 or len(new_packages) == 0:
		outname = "%s%s%s" %('tar-', strftime(conduit.confString('main', 'timeformat', '%Y%m%d%H%M%S')), '.tar.gz')
		tar = tarfile.open(outname, 'w:gz')
		tar.add('reposync2.py', 'zzz.py')
		tar.add('reposync2.conf', 'aaa')
		tar.close()





