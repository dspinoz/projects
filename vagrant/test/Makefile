tag = test
name = test
volume = /var/cache
links = --link=webcache:webcache

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
	docker run -it $(links) -e http_proxy=http://webcache:8123/  $(tag) bash

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

backup: export start
	docker run -it --volumes-from $(name) $(links) --volume `pwd`/backup:/backups $(tag) sh -c 'apt-get install rsync && rsync -arvb $(volume) /backups'

clean: stop
	rm -f $(name).build $(name).started
	docker rm $(name)
