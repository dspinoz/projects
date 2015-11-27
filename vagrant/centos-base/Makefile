tag = ds:centos7
name = centos7_test
volume = 
links = --net=host

.PHONY: all clean build export stop logs

all: start

build: $(name).build

$(name).build: Dockerfile
	docker build --tag=$(tag) .
	docker create --name=$(name) $(links) --publish=8080:8080 $(tag)
	touch $(name).build

export: $(name).tgz

$(name).tgz: $(name).build
	docker export $(name) | gzip - > $(name).tgz
	touch $(name).tgz

bash: build start
	docker exec -it $(name) bash

start: $(name).started

$(name).started: build
	docker start $(name)
	touch $(name).started

stop:
	if [ -f $(name).started ]; then rm -f $(name).started; 	docker stop $(name); fi

logs:
	docker logs -f $(name)

backup: export start
	docker run -it --volumes-from $(name) $(links) --volume `pwd`/backup:/backups $(tag) sh -c 'apt-get install rsync && rsync -arvb $(volume) /backups'

clean: stop
	if [ -f $(name).build ]; then rm -f $(name).build; docker rm -f $(name); fi
