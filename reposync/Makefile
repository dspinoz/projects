VERSION = 0.5

all: check 

check: reposync2.py
	python -m py_compile reposync2.py

test: testbasic testyum

testbasic: install
	rm -rf repo reposync-*.tar.gz reposync-*.csv
	reposync --plugins --repoid=repo 
	@# Do multiple builds to ensure reposync only builds one incremental
	reposync --plugins --repoid=repo 
	test `ls reposync-*.tar.gz | wc -l` -eq 1
	test `find repo -type f -name '*.rpm' | wc -l` -eq  `tar tvf reposync-*.tar.gz | grep rpm | wc -l`

testyum: install testbasic
	yum --reposync2-enable --downloadonly install `find repo -type f -name '*.rpm' -exec rpm --queryformat '%{NAME}\n' -qp {} \; | sort | uniq | xargs`

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

test8: install
	rm -f rhel-7-server-rpms/Packages/trousers-0.3.11.2-3.el7.x86_64.rpm
	yum remove -y trousers
	yum install -y --reposync2-enable trousers

source: 
	rm -rf tmp; mkdir -p tmp/reposync2-$(VERSION); cp reposync2.conf reposync2.py README.md reposync2.spec Makefile tmp/reposync2-$(VERSION)/; tar cvfz reposync2-$(VERSION).tgz -C tmp/ . 

rpm: source
	rpmbuild -ta reposync2-$(VERSION).tgz
	
install: reposync2.conf reposync2.py check
	mkdir -p $(DESTDIR)/etc/yum/pluginconf.d $(DESTDIR)/usr/share/yum-plugins
	cp reposync2.conf $(DESTDIR)/etc/yum/pluginconf.d/reposync2.conf
	cp reposync2.py $(DESTDIR)/usr/share/yum-plugins/reposync2.py
