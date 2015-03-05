all: test

test: install
	reposync --plugins --repoid=repo 

test2: install
	reposync --plugins --repo=epel7 

install: reposync2.conf reposync2.py
	cp reposync2.conf /etc/yum/pluginconf.d/reposync2.conf
	cp reposync2.py /usr/share/yum-plugins/reposync2.py
