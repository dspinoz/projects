all: check install test

check: reposync2.py
	python -m py_compile reposync2.py

test: install
	reposync --plugins --repoid=repo 

test2: install
	reposync --plugins --source --repo=epel7 

test3: install
	rm -rf repo*/pytho* repo2/lib*
	reposync --plugins --repo=repo\*

test4: install
	yum --reposync2-merge 

test5:	install
	rm -rf tmp
	mkdir tmp
	cd tmp && yum --reposync2-merge --incremental-dir=../ --dest-dir=.
	cat tmp/.reposync2.meta
	find tmp

test6: install
	rm -rf repo/lib*
	reposync --plugins --repoid=repo
	yum --reposync2-merge 

test7: install
	rm -rf repo/lib*
	reposync --plugins --repoid=repo
	rm -rf repo/lib*
	reposync --plugins --repoid=repo
	rm -rf repo/lib*
	reposync --plugins --repoid=repo
	yum --reposync2-merge 

install: reposync2.conf reposync2.py check
	cp reposync2.conf /etc/yum/pluginconf.d/reposync2.conf
	cp reposync2.py /usr/share/yum-plugins/reposync2.py
