all: check 

check: reposync2.py
	python -m py_compile reposync2.py

test: install
	reposync --plugins --repoid=repo 

test2: install
	reposync --plugins --source --repo=epel7 

test3: install
	rm -rf repo*/pytho* repo2/lib*
	mkdir -p repos-merged
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

source: 
	rm -rf tmp; mkdir -p tmp/reposync2-0.2; cp reposync2.conf reposync2.py README.md reposync2.spec Makefile tmp/reposync2-0.2/; cd tmp; zip -r ../reposync2-0.2.zip reposync2-0.2/

install: reposync2.conf reposync2.py check
	mkdir -p $(DESTDIR)/etc/yum/pluginconf.d $(DESTDIR)/usr/share/yum-plugins
	cp reposync2.conf $(DESTDIR)/etc/yum/pluginconf.d/reposync2.conf
	cp reposync2.py $(DESTDIR)/usr/share/yum-plugins/reposync2.py
