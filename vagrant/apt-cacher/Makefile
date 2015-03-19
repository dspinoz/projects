tag = apt-cacher-ng
name = test-apt-cacher
volume = /var/cache/apt-cacher-ng/
links = 
linkcache = --link=test-apt-cacher:apt-cache
setupcache = echo "Acquire::http { Proxy \"http://apt-cache:3142\"; };" >> /etc/apt/apt.conf.d/01proxy

.PHONY: all clean build export stop logs

all: start

build: $(name).build

$(name).build: Dockerfile
	docker build --tag=$(tag) .
	docker create --name=$(name) $(links) $(tag)
	touch $(name).build

export: $(name).tgz

$(name).tgz: $(name).build
	docker export $(name) | gzip - > $(name).tgz
	touch $(name).tgz

bash: build
	docker run -it --volumes-from $(name) $(links) $(tag) bash

start: $(name).started

$(name).started: build
	@#docker start --attach=true --interactive=true $(name)
	docker start $(name)
	touch $(name).started

stop:
	rm -f $(name).started
	docker stop $(name) 

logs:
	docker logs -f $(name)

backup: export
	docker run -it --volumes-from $(name) $(links) $(linkcache) --volume `pwd`/backup:/backups $(tag) sh -c '$(setupcache) && apt-get install rsync && mkdir -p /backups/$(volume) && rsync -arvb --delete --backup-dir=/backups/.deleted $(volume) /backups/$(volume)'

# TODO restore from backup
#restore: build
#	docker run -it --volumes-from $(name) $(links) $(linkcache) --volume `pwd`/cache:/backups $(tag) sh -c '$(setupcache) && apt-get install rsync && rsync -arvb /backups/* $(volume)/..'

clean: stop
	rm -f $(name).build $(name).started
	docker rm $(name)
