from yum.plugins import PluginYumExit, TYPE_CORE

requires_api_version = '2.3'
plugin_type = (TYPE_CORE)

def init_hook(conduit):
	#conduit.info(2, 'hello world')
	print "DS INIT"

def postreposetup_hook(conduit):
	#conduit.info(2', 'got repos')
	print "DS REPO SETUP"

def predownload_hook(conduit):
	#conduit.info(2, 'downloading...')
	print "DS PREDOWN"

def postdownload_hook(conduit):
	#conduit.info(2, 'downloaded.')
	print "DS POSTDOWN"

def posttrans_hook(conduit):
	print "DS TRANS DONE"

def close_hook(conduit):
	print "DS CLOSE"


