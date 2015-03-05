all: check install test

check: reposync2.py
	python -m py_compile reposync2.py

test: install
	reposync --plugins --repoid=repo 

test2: install
	reposync --plugins --repo=epel7 

test3: install
	rm -rf repo*/pytho* repo2/lib*
	reposync --plugins --repo=repo\*


install: reposync2.conf reposync2.py check
	cp reposync2.conf /etc/yum/pluginconf.d/reposync2.conf
	cp reposync2.py /usr/share/yum-plugins/reposync2.py
